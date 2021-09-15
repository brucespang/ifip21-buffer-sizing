import click
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import gzip
import sqlalchemy

@click.command()
@click.option("--id", "exp_id")
@click.option("--note", "note")
@click.option("--prompt/--no-prompt", "prompt", default=True, help="Check before deleting")
def main(exp_id, note, prompt):
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

    if prompt:
        click.confirm("Are you sure you want to delete %d experiment(s)?"%(len(exp_df)), abort=True)

    for _,exp in exp_df.iterrows():
        q = sqlalchemy.sql.text("""
          delete from experiments where id = :id;
          delete from traces where experiment_id = :id;
          delete from postcard_traces where experiment_id = :id;
          delete from retransmits where experiment_id = :id;
          delete from packet_counts where experiment_id = :id;
          delete from retrans_counts where experiment_id = :id;
          delete from snd_cwnd_histograms where experiment_id = :id;
          delete from queue_depth_histograms where experiment_id = :id;
        """)
        con.execute(q, id=exp.id)

    print("Deleted %d experiment(s)"%(len(exp_df)))

if __name__ == "__main__":
    main()
