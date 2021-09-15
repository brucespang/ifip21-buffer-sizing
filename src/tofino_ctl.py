import bfrt
import sys
import click
from queue_depth_histogram import QueueDepthHistogram

@click.group()
def cli():
    pass

@cli.group()
def action():
    pass

@action.command(help='Drop packets when queue is full. WARNING: not traffic-safe')
def drop():
    sender_action = conn.table("SwitchEgress.wred.sender_action")
    sender_action.clear()
    sender_action.add([("exceeds_threshold", True)], "SwitchEgress.wred.drop")
    sender_action.add([("exceeds_threshold", False)], "SwitchEgress.wred.nop")

@action.command(help='Mark packets in the forward direction when queue is full. (Proper ECN) WARNING: not traffic-safe')
def ecn():
    sender_action = conn.table("SwitchEgress.wred.sender_action")
    sender_action.clear()
    sender_action.add([("exceeds_threshold", True)], "SwitchEgress.wred.set_ipv4_ecn")
    sender_action.add([("exceeds_threshold", False)], "SwitchEgress.wred.nop")

@cli.group()
def stats():
    pass

@stats.command()
def reset():
    qdepth_hist = QueueDepthHistogram(conn)
    qdepth_hist.reset()

@stats.command()
def qdepth():
    qdepth_hist = QueueDepthHistogram(conn)
    print "egress_port,queue_depth_cells,num_packets"
    for field,qdepth,count in qdepth_hist.entries():
        print "%d,%d,%d"%(field, qdepth, count)

@cli.group()
def threshold():
    pass

@threshold.command()
@click.option('--ports', '-p', 'ports', default='all')
@click.argument('depth')
def set(depth, ports):
    qdepth_threshold = conn.register("SwitchEgress.wred.qdepth_threshold_cells")

    if ports == 'all':
        ports = ','.join([str(x) for x in range(256)])

    for port in ports.split(','):
        qdepth_threshold.set(int(port), int(depth))

@threshold.command()
def list():
    qdepth_threshold = conn.register("SwitchEgress.wred.qdepth_threshold_cells")
    for port,thresholds in qdepth_threshold.entries().items():
        print port, thresholds

@threshold.command()
@click.argument('port')
def get(port):
    qdepth_threshold = conn.register("SwitchEgress.wred.qdepth_threshold_cells")
    print qdepth_threshold.get(int(port))

@cli.group()
def postcard():
    pass

@postcard.command(help='Send queue reporting postcards')
def enable():
    table = conn.table("SwitchEgress.queue_mirrorer.check_mirroring")
    table.default_entry_set("SwitchEgress.queue_mirrorer.enable_mirroring")

@postcard.command(help='Stop sending queue reporting postcards')
def disable():
    table = conn.table("SwitchEgress.queue_mirrorer.check_mirroring")
    table.default_entry_set("SwitchEgress.queue_mirrorer.disable_mirroring")

    
if __name__ == '__main__':
    try:
        conn = bfrt.Connection("main")

        cli()
    finally:
        conn.close()
