import bfrt
import struct
import bfrt_grpc.client as gc

def bytes_to_int(byte_s):
    return int(str(byte_s).encode('hex'), 16)

class QueueDepthHistogram():
    def __init__(self, conn):
        self.name = "SwitchEgress.stats.qdepth_hist"
        self.client = conn.client
        self.target = conn.target
        self.table = self.client.bfrt_info_get().table_get("pipe.%s"%self.name)
        self.count_func = "SwitchEgress.stats.count_qdepth_stats"

    def clear(self):
        keys = []
        for data,key in self.table.entry_get(self.target):
            if key is not None:
                keys.append(key)
        self.table.entry_del(self.target, keys)
        
    def reset(self):
        for d,k in self.table.entry_get(self.target, []):
            self.table.entry_mod(self.target, [k],
                                 [self.table.make_data([], self.count_func)])
        
    def add(self, egress_port, qdepth):
        keys = [self.table.make_key([
            gc.KeyTuple("eg_intr_md.egress_port", value=egress_port),
            gc.KeyTuple("eg_intr_md.deq_qdepth", value=qdepth),
            gc.KeyTuple('$MATCH_PRIORITY', 0)])]

        data = [self.table.make_data([], self.count_func)]

        self.table.entry_add(self.target, keys, data)

    def entries(self):
        res = {}

        for d,k in self.table.entry_get(self.target, []):
            qdepth = bytes_to_int(k['eg_intr_md.deq_qdepth'].value)
            egress_port = bytes_to_int(k['eg_intr_md.egress_port'].value)
            count = bytes_to_int(d['$COUNTER_SPEC_PKTS'].val)
            yield (egress_port, qdepth, count)
