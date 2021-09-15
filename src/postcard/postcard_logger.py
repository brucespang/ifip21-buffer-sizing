import uptime

def log(**kwargs):
    entries = ["{}={}".format(k,v) for k,v in kwargs.items()]
    # print out the line and flush the buffer since
    # sys.stdout apparently not flushed on exit(0)?
    print("{}: postcard: {}".format(uptime.uptime(), ' '.join(entries)),
          flush=True)

def parse_log_line(line,
                   bool_fields=set(['is_mirrored']),
                   integer_fields=set(['egress_port', 'ingress_port','src_port',
                                       'dst_port','seq_no','ack_no',
                                       'queue_depth_cells','switch_id',
                                       'was_dropped']),
                   str_fields=set(['ipv4_src_addr','ipv4_dst_addr']),
                   float_fields=set(['queue_timestamp']),
                   hex_fields=set()):

    fields = line.strip().split()
    if len(fields) != 14:
        print(line)
        print(fields)
        print("incorrect number of fields")

    timestamp = float(fields[0].replace(':', ''))
    data = {}

    for pair in fields[2:]:
        try:
            k,v = pair.split('=')
        except:
            print(line)
            print(fields)
            print(pair)
            
            raise Exception("broke")
        if v == "None":
            v = np.nan
        elif k in integer_fields:
            v = int(v)
        elif k in float_fields:
            v = float(v)
        elif k in hex_fields:
            v = int(v, 16)
        elif k in bool_fields:
            v = bool(v)
        elif k in str_fields:
            v = str(v)
        # else:
        #     continue
        data[k] = v

    data['timestamp'] = timestamp

    return data

def parse_postcard_log(postcard_trace_path):
    import pandas as pd
    import numpy as np
    
    with open(postcard_trace_path, "r") as postcard_trace:
        lines = postcard_trace.readlines()
    rows = [parse_log_line(line) for line in lines]
    rows = [r for r in rows if r is not None]
    if len(rows) == 0:
        return

    df = pd.DataFrame(rows)
    df = df.rename(columns={
        'timestamp': 'absolute_timestamp',
    })
    return df

if __name__ == "__main__":
    import sys
    print(parse_postcard_log(sys.argv[1]))
