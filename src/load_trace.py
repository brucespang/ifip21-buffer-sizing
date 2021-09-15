import pandas as pd
import tcp_probe
import os
import click
import uuid
import sqlalchemy
import json
import datetime
import sys
import tempfile
import io
import uptime

sys.path.append("./src/postcard")
import postcard_logger

def load_df(engine, table, df):
    sio = io.StringIO()
    sio.write(df.to_csv(index=None, header=None, na_rep="\\N"))  # Write the Pandas DataFrame as a csv to the buffer
    sio.seek(0)  # Be sure to reset the position to the start of the stream

    # Copy the string buffer to the database, as if it were an actual file
    conn = engine.raw_connection()
    with conn.cursor() as c:
        c.copy_from(sio, table, columns=df.columns, sep=',')
        conn.commit()

@click.command()
@click.argument('experiment_path', type=click.Path(exists=True))
def load(experiment_path):
    db_url = "postgresql:///cc_traces"
    engine = sqlalchemy.create_engine(db_url)

    trace_path = os.path.join(experiment_path, "trace.tr")
    config_path = os.path.join(experiment_path, "config.json")
    postcard_trace_path = os.path.join(experiment_path, "postcards.tr")

    experiment = json.loads(open(config_path).read())
    exp_id = experiment['id']
    mtu = experiment['mtu_bytes']
    experiment['run_at'] = datetime.datetime.fromtimestamp(experiment['run_at'])

    # check if we've already loaded this file
    q = sqlalchemy.sql.text('select * from experiments where id=:id')
    res = engine.execute(q, id=exp_id)
    if res.first() is not None:
        print("skipping %s"%exp_id)
        return

    print("loading %s"%exp_id)

    exp = pd.DataFrame([experiment])

    trace_df,retrans_df = tcp_probe.parser.parse_trace(trace_path)
    postcard_df = postcard_logger.parse_postcard_log(postcard_trace_path)

    if len(trace_df) == 0 or len(postcard_df) == 0:
        print("error: empty trace file for %s"%(exp_id))
        return

    # clean up the trace df
    trace_df['experiment_id'] = exp_id
    base_time = trace_df['timestamp'].min()
    trace_df['timestamp_sec'] = trace_df['timestamp'] - base_time
    
    #trace_df['queue_depth_cells'] = trace_df['window'].astype(int) - 1000
    #trace_df['queue_depth_packets'] = trace_df['queue_depth_cells']*80/mtu
    #trace_df = trace_df.drop(columns='window')
    
    trace_df = trace_df.rename(columns={
        'timestamp':'absolute_timestamp',
        'srtt': 'srtt_us'
    })

    # insert the postcard trace
    postcard_df['experiment_id'] = exp_id
    postcard_df['timestamp_sec'] = postcard_df['absolute_timestamp'] - base_time
    postcard_df['queue_depth_packets'] = postcard_df['queue_depth_cells']*80/mtu

    queue_depth_histogram_df = postcard_df.groupby(['experiment_id', 'queue_depth_packets'], as_index=False).count()
    queue_depth_histogram_df = queue_depth_histogram_df.rename(columns={'timestamp_sec': 'count'})
    queue_depth_histogram_df = queue_depth_histogram_df[['experiment_id', 'queue_depth_packets', 'count']]

    # clean up the retrans df
    if len(retrans_df) > 0:
        retrans_df['experiment_id'] = exp_id
        retrans_df['timestamp_sec'] = retrans_df['timestamp'] - base_time

        retrans_df = retrans_df.rename(columns={
            'timestamp':'absolute_timestamp',
        })
        load_df(engine, "retransmits", retrans_df)

    load_df(engine, "experiments", exp)
    load_df(engine, "traces", trace_df)
    load_df(engine, "postcard_traces", postcard_df)
    load_df(engine, "queue_depth_histograms", queue_depth_histogram_df)

#@click.command()
#@click.argument('directory', type=click.Path(exists=True))
# def main(directory):
#     for filename in os.listdir(directory):
#         if not os.is_dir(filename): continue
#         # check if the directory has the right files
#         if not os.is_file(os.path.join(directory, filename, "trace.tr")): continue
#         if not os.is_file(os.path.join(directory, filename, "config.json")): continue

#         load(con, os.path.join(directory, filename))

if __name__ == "__main__":
    load()
