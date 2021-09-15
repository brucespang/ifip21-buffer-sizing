import sys
import os
import signal
import subprocess
import time
import itertools
import uuid
import traceback
import datetime
import tcp_probe
import json
import click
from functools import partial
from multiprocessing import Pool

def load_trace(exp, username):
    subprocess.run("sudo -u {} python src/load_trace.py {}".format(username,exp), shell=True)

def validate_algorithms(ctx, param, value):
    available = set(open('/proc/sys/net/ipv4/tcp_available_congestion_control', 'r').read().split())
    for alg in value:
        if alg not in available:
            raise click.BadParameter("unknown congestion control algorithm %s. must be one of (%s)"%(alg, ', '.join(available)))
    return value

def validate_actions(ctx, param, value):
    for action in value:
        if action not in ['drop', 'ecn']:
            raise click.BadParameter("must be one of (drop, ecn)")
    return value

@click.command()
@click.option('-u', '--username', required=True, help='Username to be used during the experiment')
@click.option('--tofino-addr', 'tofino_addr', required=True, type=str, help="Address of tofino")
@click.option('-n', '--note', required=True, help='note to help identify experiment')
@click.option('-t', '--duration', default=1, help='experiment duration')
@click.option('-p', '--parallel', default=[1], multiple=True, type=int)
@click.option('-q', '--queue-depth', 'qdepths', default=[20000], multiple=True, type=int)
@click.option('-c', '--cc_algorithm', 'cc_algo', default=['reno'], multiple=True, callback=validate_algorithms)
@click.option('-a', '--action', 'actions', default=['drop'], multiple=True, callback=validate_actions)
@click.option('-m', '--mtu', 'mtus', default=[9000], multiple=True, type=int)
@click.option('-d', '--delay', 'delays', default=[1000], multiple=True, type=int, help="Base delay added to each flow (in us with granularity of 100us)")
@click.option('--delay-diff', 'delay_diffs', default=[0], multiple=True, type=int, help="The delat difference between different flows (in us with granularity of 100us)")
@click.option('--cport-start', 'cport', default=6000, help='The client port number for the first flow')
@click.option('--load-processes', default=12, type=int, help="Number of parallel processes for loading results")
@click.option('--flush/--no-flush', 'flush', default=False, help="Delete existing experiments with same note before running")
def main(username, note, duration, cc_algo, parallel, qdepths,
         actions, mtus, delays, delay_diffs, cport, load_processes, flush):
    # set sysctls on us and the receiver
    subprocess.call("sudo sysctl -w net.ipv4.tcp_slow_start_after_idle=0 net.ipv4.tcp_no_metrics_save=1 net.ipv4.tcp_ecn=1 net.ipv4.tcp_rmem='4096 131072 1250000000' net.ipv4.tcp_wmem='4096 131072 1250000000' net.ipv4.tcp_mtu_probing=1", shell=True)
    subprocess.call('ssh %s@han-2 "sudo sysctl -w net.ipv4.tcp_slow_start_after_idle=0 net.ipv4.tcp_no_metrics_save=1 net.ipv4.tcp_ecn=1 net.ipv4.tcp_rmem=\'4096 262144 1250000000\' net.ipv4.tcp_wmem=\'4096 262144 1250000000\' net.ipv4.tcp_mtu_probing=1"'%(username), shell=True)

    if flush:
        subprocess.call("python ./src/delete_traces.py --note='%s' --no-prompt"%(note), shell=True)

    results = []

    # Set some tcp_probe settings.
    # do it here instead of during the experiment because kernel tracing seems
    # to get finicky (e.g. takes a while and sometimes trace_pipe return EOF)
    # if we do it during the experiment
    tcp_probe.trace.set_trace_filter("tcp", "0")
    tcp_probe.trace.enable_event("tcp")
    tcp_probe.trace.set_trace_buffer_size(100000)

    # Make tcp_probe use boottime instead of some weird local cpu clock,
    # so that we can align it with tcpdump timestamps.
    subprocess.call("echo mono_raw > /sys/kernel/debug/tracing/trace_clock", shell=True)

    experiments = itertools.product(cc_algo,qdepths,mtus,parallel,delays,delay_diffs,actions)
    experiment_paths = []

    for alg,qdepth,mtu,num_flows,delay,delay_diff,action in experiments:

        experiment_name = str(uuid.uuid1())
        #experiment_name = '%s_%d_mtu%d_q%d_%s_%s'%(alg, num_flows, mtu, qdepth, delay, action)

        print("###########################")
        print("alg:", alg, "qdepth:", qdepth, "mtu:", mtu, "num_flows:", num_flows, "delay:", delay, "delay_diff:", delay_diff, "action:", action)
        print("id:", experiment_name)

        server_ssh_command = f'sudo ssh {username}@han-2 '
        server_setup_commands = 'sudo ip link set dev eth2 mtu %d; '%(mtu)
        server_setup_commands += 'sudo tc qdisc del dev eth2 root; '
        if delay is None:
            print("* Traffic controller delay is choosen to be {}. Reconsider it for better results! *".format(delay))
            subprocess.run(server_ssh_command + '"' + server_setup_commands + '"', shell=True)
        else:
            if delay_diff == 0:
                server_setup_commands += 'sudo tc qdisc add dev eth2 root netem delay %d; '%(delay)
                subprocess.run(server_ssh_command + '"' + server_setup_commands + '"', shell=True)
            else:
                num_bands = min(num_flows, 16)
                server_setup_commands += 'sudo tc qdisc add dev eth2 root handle 1: prio bands %d priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0; '%(num_bands)
                for i in range(num_bands):
                    server_setup_commands += 'sudo tc qdisc add dev eth2 parent 1:%x handle %x: netem delay %d; '%(i+1, i+1+num_bands, delay+i*delay_diff)
                    server_setup_commands += 'sudo tc filter add dev eth2 parent 1: protocol ip u32 match ip dport %d 0xffff flowid 1:%x; '%((cport+i)%num_bands, i+1)
                subprocess.run(server_ssh_command + '"' + server_setup_commands + '"', shell=True)
            # print("Issued the following command:\n\t" + server_ssh_command + '"' + server_setup_commands + '"')

        subprocess.run("sudo ip link set dev bond0 mtu %d"%(mtu), shell=True)
        # Set the Tofino configurations below. We use the P4 files under Bruce's
        # folders which is accessable from the root users of han-3 machine
        tofino_config = f'sudo ssh {username}@{tofino_addr} "SDE_INSTALL=/home/{username}/bf-sde-9.1.0/install python tofino-tcp-traces/src/tofino_ctl.py threshold set --ports 180,183,189 {qdepth}; SDE_INSTALL=/home/{username}/bf-sde-9.1.0/install python tofino-tcp-traces/src/tofino_ctl.py action {action}"'
        print("Accessing Tofino for switch congifuration...")
        subprocess.run(tofino_config, shell=True)

        path = "results/%s"%experiment_name
        experiment_paths.append(path)
        os.makedirs(path)
        trace_path = "%s/trace.tr"%(path)
        trace_file = open(trace_path, 'w')

        print("Starting the dataplane telemetry collector...")
        postcard_path = os.path.join(path, "postcards.tr")
        postcard_trace_file = open(postcard_path, 'w+')
        # postcard_p = subprocess.Popen(['tcpdump', '-tt', '-i', 'bond0', 'udp port 4444', '-w', postcard_path])
        subprocess.run('cd src/postcard/ && make compile', shell=True)
        postcard_p = subprocess.Popen(['src/postcard/collector'],
                                      stdout=postcard_trace_file)

        # It takes time to start the collector. If you don't wait for it enough
        # you may lose some postcards.
        time.sleep(1)

        tcp_probe.trace.clear_trace_buffer()
        p = tcp_probe.trace.start_trace(trace_file)

        # make sure tcp_probe is recording data before running iperf
        # TODO: probably this relies on some network traffic happening. would be
        # nice if it did not.
        print("waiting for tcp_probe..", end='')
        while not os.path.exists(trace_path) or os.path.getsize(trace_path) <= 1:
            time.sleep(0.1)
            print(".", end='', flush=True)
            res = p.poll()
            if res is not None:
                print(res)
                print(p.communicate())
                return

        print("ready")

        subprocess.call("sudo sysctl -w net.ipv4.tcp_congestion_control=%s"%(alg), shell=True)
        # Start num_flows many iperf sessions with predefined client ports
        # Client ports are important to know in the beginning so that we can
        # filter flows on the server side for per-flow treatment
        subprocess.run('iperf3 -c 10.0.0.1 -t %d --parallel %d -Z --cport %d'%(duration, num_flows, cport), shell=True)

        print("Killing the dataplane telemetry collector...")
        subprocess.run('sudo kill %d'%(postcard_p.pid), shell=True)
        postcard_trace_file.close()

        subprocess.run('sudo kill %d'%(p.pid), shell=True)
        print("Killed the TCP trace probing...")

        trace_file.close()

        with open('results/%s/config.json'%(experiment_name), 'w') as config_file:
            config_file.write(json.dumps({
                'id': experiment_name,
                'filename': trace_path,
                'algorithm': alg,
                'num_flows': num_flows,
                'mtu_bytes': mtu,
                'max_queue_depth_cells': qdepth,
                'max_queue_depth_bytes': qdepth*80,
                'max_queue_depth_packets': qdepth*80/mtu,
                'receiver_delay': str(delay/1000)+'ms',
                'action': action,
                'note': note,
                'experimenter': username,
                'run_at': datetime.datetime.timestamp(datetime.datetime.now())
            }))
        print("Written the config.json file...")

    # FINALLY,
    # disable tracing
    tcp_probe.trace.disable_event("tcp")

    # load all the results
    pool = Pool(processes=load_processes)
    pool.map(partial(load_trace, username=username), experiment_paths)

if __name__ == '__main__':
    main()
