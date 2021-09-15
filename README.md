# Updating the Theory of Buffer Sizing

These are a set of packet-by-packet traces of two Linux hosts sending data using TCP. We collected these traces by writing some code for [a Tofino](https://www.intel.com/content/www/us/en/products/network-io/programmable-ethernet-switch/tofino-2-series.html), which is included in this repository. These measurements were collected for our IFIP Performance 2021 Paper "Updating the Theory of Buffer Sizing."

## Datasets

[Download the datasets here.](https://drive.google.com/file/d/1HrfHMYLfpcYCgIe9doew8ajCX6GFBJcN/view?usp=sharing)

The datasets have packet-by-packet TCP data (congestion window, RTT, etc...) and queue depth data for different congestion control algorithms, queue depths, numbers of TCP flows, and whether the switch is dropping packets or marking them with ECN. Each trace runs for about one thousand RTTs.

We collect two pieces of information: at the sender side, we use Linux's [TCP tracing system](https://lore.kernel.org/patchwork/patch/865762/) to measure the congestion window, sRTT, and other sender-side information for each sent packet. We also use p4 to measure and report the queue length for each packet as measured by the switch.

The dataset is available as a 6GB compressed postgres database, [downloadable here](https://drive.google.com/file/d/1HrfHMYLfpcYCgIe9doew8ajCX6GFBJcN/view?usp=sharing). Uncompressed it is about 40 GB. It can be loaded into postgres by running:
```
$ tar xvfz cc_traces.db.tar.gz
x cc_traces.db
$ psql cc_traces < cc_traces.db
...[This takes a while]...
```

For examples on how to use this data, please see the `notebooks/` directory.

We are happy to give more information about how to use the dataset, and answer any questions you have! Please reach out to us either by opening an issue or emailing [bruce@brucespang.com](mailto:bruce@brucespang.com).

## Experimental Setup

Our test network consists of two servers with 32 2.4Ghz cores and 32 GB of RAM each, connected by a Barefoot Tofino switch and use up to 2 MB of buffers. The servers run Linux 5.5.0, each with an Intel 82599ES 10Gb/s NIC. Each NIC is connected to a port of a 6.5Tb/s Barefoot Tofino switch via 100G to 4x10 Gb/s breakout cables. The sender server is connected to the Tofino with two 10G cables. The interfaces are bonded and packets are equally split between them, which ensures that congestion happens at the switch (otherwise we only see congestion at the sender NIC). We set MTUs to 9000 bytes so the servers can sustain a 10Gb/s rate. We add 1ms of delay at the sender using [tc](https://man7.org/linux/man-pages/man8/tc.8.html), and used [iperf3](https://iperf.fr/) to generate TCP traffic. We used congestion control algorithms available in Linux 5.5.0, including TCP Reno, Cubic, BBR (v1), and Scalable TCP. We also used Google's alpha release of BBR2. 

**Note:** We are aware of two minor ways this setup is non-standard. These were not important for the analysis in our paper, but might be for your work:

1. In a standard tail-drop queue, when a packet arrives to a full queue it is immediately dropped. Because of implementation details with the Tofino, our queue drops packets on departure if the packet arrived and the queue is too long. This means that the queue depth can briefly exceed a "full" queue, and that queueing delays will be longer than they would be in a standard queue.
2. There's some variability in the way packets are sent into the queue that we haven't been able to track down. This causes rapid, short-term fluctuation in the queue depth of about ten packets. For whatever reason, this doesn't happen with BBR.


## Code

The respository also includes code for running simple TCP experiments on Tofino. The p4 code has been tested on a Tofino running Barefoot SDE 9.1.0. We have not updated it to newer versions of Intel's P4 Studio SDE. We don't promise any support for the code, and it will take some work if you want to use it for your experiments. If you do want to use it though, please feel free to reach out to us! We may be able to give some pointers and help sort out the issues you will run into.

At a very high level,
* `p4src/` includes the p4 source code for some simple switching, queuing logic (marking, dropping, etc...), and for sending postcards to the sender with the current queue depth.
* `ptf-tests/` includes tests for the p4 code
* `bfrt_python/` includes configuration for the Tofino
* `src/` includes python tools for running, categorizing, and collecting the results of experiments. 
