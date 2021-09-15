import click
import pandas as pd
import plorts
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import sys
import os
import gzip
import tcp_probe.parser as parser
import sqlalchemy
plt.style.use(['plorts','plorts-print'])

def plot_trace(experiment_df, trace_df, retrans_df, postcard_df, legend=False):
    num_plots = 4
    xmin = 0
    xmax = trace_df.timestamp_sec.max()
    xlabel = "Time (sec)"
    output_dir = 'plots/traces'

    note = experiment_df.note
    alg = experiment_df.algorithm
    action = experiment_df.action
    qdepth = experiment_df.max_queue_depth_packets
    mtu = experiment_df.mtu_bytes
    num_flows = experiment_df.num_flows
    fair_bdp = (1250000000*0.0012+qdepth*mtu)/(mtu*num_flows)

    #plt.suptitle("%s - %s - %d flows - %d packets"%(alg, action, num_flows, qdepth))

    ind = 1
    plt.figure(figsize=(18,5*num_plots))

    plt.subplot(num_plots,1,ind)
    plt.title("snd_cwnd")
    plorts.scatter(trace_df, x="timestamp_sec", y="snd_cwnd", hue=["sport", "dport"])
    plt.axis(xmin=xmin, xmax=xmax, ymin=0)
    plt.axhline(y=fair_bdp, linestyle=":")
    plt.xlabel(xlabel)
    if legend:
        plt.legend(loc='best')
    ind +=1

    plt.subplot(num_plots,1,ind)
    plt.title("srtt")
    plorts.scatter(trace_df, x="timestamp_sec", y="srtt_us", hue=["sport", "dport"])
    plt.axis(xmin=xmin, xmax=xmax, ymin=0)
    plt.xlabel(xlabel)
    plt.title("Timeseries RTT (usec)")
    if legend:
        plt.legend(loc='best')
    ind +=1

    # plt.subplot(num_plots,1,ind)
    # plt.title("queue_depth_packets")
    # plorts.scatter(trace_df, x="timestamp_sec", y="queue_depth_packets", hue=["sport", "dport"])
    # plt.axis(xmin=xmin, xmax=xmax, ymin=0)
    # plt.xlabel(xlabel)
    # plt.ylabel("Queue Depth (packets)")
    # plt.axhline(y=qdepth, linestyle=":")
    # if legend:
    #     plt.legend(loc='best')
    # ind +=1

    # # columns to join trace_df with postcard_df
    # trace_cols = ["dport","snd_nxt","sport"]
    # postcard_cols = ["dst_port","seq_no","src_port"]
    # # Merge the two dfs so that we can synch
    # # (we use merge_asof because retransmitted packet may create a problem)
    # trace_df["timestamp_sec_tr"] = trace_df["timestamp_sec"]
    # postcard_df = pd.merge_asof(postcard_df,
    #                             trace_df[["dport","snd_nxt","sport","timestamp_sec","timestamp_sec_tr"]].sort_values("timestamp_sec"),
    #                             left_by = postcard_cols,
    #                             right_by = trace_cols,
    #                             on = "timestamp_sec",
    #                             direction = "nearest") # The closest time trace_df had data for this packet
    # # trace_df.join(postcard_df.set_index(postcard_cols), on=trace_cols, rsuffix="_pc") #_pc for postcard
    plt.subplot(num_plots,1,ind)
    plt.title("queue_depth_cells")
    # plorts.scatter(postcard_df, x="timestamp_sec_tr", y="q_depth_cells", hue=["src_port", "dst_port"])
    # plorts.scatter(postcard_df, x="timestamp_sec", y="queue_depth_cells", hue=["src_port", "dst_port"])
    plorts.scatter(postcard_df, x="timestamp_sec", y="queue_depth_cells", hue=["src_port", "dst_port"])
    plt.axis(xmin=xmin, xmax=xmax, ymin=0)
    plt.xlabel(xlabel)
    plt.ylabel("Queue Depth (cells)")
    plt.axhline(y=qdepth*mtu/80, linestyle=":")
    if legend:
        plt.legend(loc='best')
    ind +=1

    plt.subplot(num_plots,1,ind)
    plt.title("retransmitted skbs")
    if len(retrans_df) > 0:
        flow_ids = {}
        for sport in retrans_df.sport.unique():
            flow_ids[sport] = len(flow_ids)
        retrans_df["flow_id"] = [flow_ids[sport] for sport in retrans_df.sport]

        plorts.scatter(retrans_df, x="timestamp_sec", y="flow_id", hue="sport")
        plt.axis(xmin=xmin, xmax=xmax)
        plt.xlabel(xlabel)
    ind +=1

    if experiment_df.pacing:
        pacing_factor = experiment_df.pacing_factor
        filename = '{}_pacing_{:.1f}_{}_{}_{}_{:.0f}.png'.format(note,
                                                                 pacing_factor,
                                                                 alg,action,
                                                                 num_flows,
                                                                 qdepth)

    else:
        filename = '%s_%s_%s_%d_%d.png'%(note, alg, action, num_flows,qdepth)

    output_path = os.path.join(output_dir, filename)
    plorts.savefig(output_path)
    print("Saved image as '{}'".format(output_path))
    plt.close()

    return output_path

@click.command()
@click.option("--id", "exp_id")
@click.option("--note", "note")
@click.option("--open/--no-open", "open_file", default=False)
def main(exp_id, note, open_file):
    if exp_id is None and note is None:
        print("error: must pass either --id or --note", file=sys.stderr)
        sys.exit(1)

    if exp_id is not None and note is not None:
        print("error: cannot pass both --id and --note", file=sys.stderr)
        sys.exit(1)

    pw = open('config/postgres.pw').read()
    url = 'postgresql://%s@localhost:5432/cc_traces'%pw
    con = sqlalchemy.create_engine(url)

    if exp_id is not None:
        exp_df = pd.read_sql("""
        select * from experiments
        where id = '%s'"""%(exp_id), con=con)
    elif note is not None:
        exp_df = pd.read_sql("""
        select * from experiments
        where note = '%s'"""%(note), con=con)

    for _,exp in exp_df.iterrows():
        trace_df = pd.read_sql("""
        select * from traces
        where experiment_id = '%s'
        and (sport != 22 and dport != 22)
        """%(exp.id), con=con)

        retrans_df = pd.read_sql("""
        select * from retransmits where experiment_id = '%s'
        and  (sport != 22 and dport != 22)
        """%(exp.id), con=con)

        postcard_df = pd.read_sql("""
        select * from postcard_traces
        where experiment_id = '%s'
        """%(exp.id),con=con)

        path = plot_trace(exp, trace_df, retrans_df, postcard_df)
        if open_file:
            subprocess.call("open %s"%(path), shell=True)

if __name__ == "__main__":
    main()
