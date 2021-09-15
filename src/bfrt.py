import atexit
import sys
import os
sde_install = os.environ['SDE_INSTALL']
sys.path.append('%s/lib/python2.7/site-packages/tofino'%(sde_install))
sys.path.append('%s/lib/python2.7/site-packages/p4testutils'%(sde_install))
sys.path.append('%s/lib/python2.7/site-packages'%(sde_install))
import grpc
import bfrt_grpc.client as gc

class Register():
    def __init__(self, client, target, name):
        self.name = name
        self.client = client
        self.target = target
        self.register = self.client.bfrt_info_get().table_get("pipe.%s"%(name))

    def make_key(self, key):
        return self.register.make_key([gc.KeyTuple('$REGISTER_INDEX', key)])

    def get_key_value(self, key):
        return key.to_dict()['$REGISTER_INDEX']['value']
    
    def get_data_value(self, data):
        return data.to_dict()['%s.f1'%self.name]
    
    def entries(self):
        # Returns a dictionary of index to register value array
        res = {}
        for data, key in self.register.entry_get(self.target, []):
            res[self.get_key_value(key)] = self.get_data_value(data)
        return res
    
    def get(self, index):
        # Returns the register data for a given index. Returns an array, since the
        # different pipelines may have different values.
        for data, key in self.register.entry_get(self.target, [self.make_key(index)]):
            return self.get_data_value(data)

    def set(self, index, value):
        return self.register.entry_add(
            self.target,
            [self.make_key(index)],
            [self.register.make_data(
                [gc.DataTuple('%s.f1'%self.name, value)])])
class Table():
    def __init__(self, client, target, name):
        self.name = name
        self.client = client
        self.target = target
        self.table = client.bfrt_info_get().table_get("pipe.%s"%name)

    def annotate_key(self, key, annotation):
        self.table.info.key_field_annotation_add(key, annotation)

    def clear(self):
        keys = []
        for data,key in self.table.entry_get(self.target):
            if key is not None:
                keys.append(key)
        self.table.entry_del(self.target, keys)
        
    def entries(self):
        # Return the table entries
        # XXX - make sure that the format of this one matches the add format
        res = []
        for data,key in self.table.entry_get(self.target, []):
            data = data.to_dict()
            keys = []
            for field_name, val in key.to_dict().items():
                keys.append((field_name, val['value']))
            
            res.append((keys, data))
            
        return res
        
    def add(self, keys, action, action_data=[]):
        # This is a simple helper method that takes a list of entries and programs
        # them in a specified table
        #
        # Parameters
        #  keys         -- a list of tuples for each element of the key
        #  action       -- the action to use. Must use full name of the action
        #  data         -- a list (may be empty) of the tuples for each action
        #                  parameter
        # TODO: add some input checking
        
        keys = [self.table.make_key([gc.KeyTuple(*f)   for f in keys])]
        datas = [self.table.make_data([gc.DataTuple(*p) for p in action_data],
                                      action)]
        self.table.entry_add(self.target, keys, datas)

    def default_entry_set(self, action):
        data = self.table.make_data([], action)
        self.table.default_entry_set(self.target, data)

class XXXHistogram():
    # A histogram feels like a pretty standard construct in p4, this wraps
    # histograms which have exact matches.
    ######
    # XXX: this is some old code from a RangeHistogram and doesn't do what you want!
    ######
    
    def __init__(self, client, target, name, count_func):
        self.name = name
        self.client = client
        self.target = target
        self.table = client.bfrt_info_get().table_get("pipe.%s"%name)
        
        # TODO: feels kind of ugly that we have to pass the name of
        # the counting function here.
        self.count_func = count_func

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
        
    def add(self, field, low, high):
        keys = [self.table.make_key([
            gc.KeyTuple(field, low=low, high=high),
            gc.KeyTuple('$MATCH_PRIORITY', 0)])]

        data = [self.table.make_data([], self.count_func)]

        self.table.entry_add(self.target, keys, data)

    def entries(self):
        res = {}
        for d,k in self.table.entry_get(self.target, []):
            keys = []
            keys = k.to_dict()
            assert(len(keys) == 2)
            del keys['$MATCH_PRIORITY']
            name,val = keys.items()[0]
            keys = (name, val['low'], val['high'])
            res[keys] = d.to_dict()['$COUNTER_SPEC_PKTS']
        return res
        
class Connection():
    def __init__(self, p4_name, grpc_addr="localhost:50052", client_id=0, device_id=0, pipe_id=0xFFFF):
        self.p4_name = p4_name
        self.grpc_addr = grpc_addr
        self.client_id = client_id
        self.device_id = device_id
        self.pipe_id = pipe_id

        self.client = gc.ClientInterface(grpc_addr, client_id, device_id)
        self.target = gc.Target(device_id, pipe_id)

        self.client.bind_pipeline_config(p4_name)
        
        # Does not seem to work, so let's not be misleading...
        # atexit.register(self.close)

    def close(self):
        self.client._tear_down_stream()
        
    def register(self, name):
        return Register(self.client, self.target, name)

    def table(self, name):
        return Table(self.client, self.target, name)

    def range_histogram(self, name, count_func):
        return RangeHistogram(self.client, self.target, name, count_func)
    
if __name__ == "__main__":
    try:
        conn = Connection("main")    
        # reg = conn.register("SwitchEgress.wred.qdepth_threshold_cells")
        # print(reg.set(1, 0xFF))
        # print(reg.set(2, 0xFE))
        # print(reg.get(1))
        # print(reg.entries())

        qdepth_hist = conn.range_histogram("SwitchEgress.stats.qdepth_hist",
                                     "SwitchEgress.stats.count_qdepth_stats")
        qdepth_hist.clear()
        qdepth_hist.add('eg_intr_md.deq_qdepth', 0, 10)
        qdepth_hist.reset()
        print(qdepth_hist.entries())
    finally:
        conn.close()
