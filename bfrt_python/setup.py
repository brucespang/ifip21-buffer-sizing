p4 = bfrt.main.pipe

# # This function can clear all the tables and later on other fixed objects
# # once bfrt support is added.
def clear_all(p4):
    # The order is important. We do want to clear from the top, i.e.
    # delete objects that use other objects, e.g. table entries use
    # selector groups and selector groups use action profile members

    # Clear Match Tables
    for table in p4.info(return_info=True, print_info=False):
        if table['type'] in ['MATCH_DIRECT', 'MATCH_INDIRECT_SELECTOR']:
            print("Clearing table {}".format(table['full_name']))
            if table['usage'] > 0:
                for entry in table['node'].get(regex=True):
                    entry.remove()
    # Clear Selectors
    for table in p4.info(return_info=True, print_info=False):
        if table['type'] in ['SELECTOR']:
            print("Clearing ActionSelector {}".format(table['full_name']))
            for entry in table['node'].get(regex=True):
                entry.remove()
    # Clear Action Profiles
    for table in p4.info(return_info=True, print_info=False):
        if table['type'] in ['ACTION_PROFILE']:
            print("Clearing ActionProfile {}".format(table['full_name']))
            for entry in table['node'].get(regex=True):
                entry.remove()

clear_all(p4)

p4.SwitchEgress.wred.sender_action.add_with_drop(exceeds_threshold=True)

p4.SwitchIngress.forward.add_from_json(open('/home/bspang/ifip21-buffer-sizing/tables/tofino-1/routes.json').read())
p4.SwitchEgress.wred.sender_ports.add_from_json(open('/home/bspang/ifip21-buffer-sizing/tables/tofino-1/sender_ports.json').read())

bfrt.mirror.cfg.add_from_json(open('/home/bspang/ifip21-buffer-sizing/tables/tofino-1/mirror_cfg.json').read())
p4.SwitchEgress.queue_mirrorer.select_mirror_sid.add_from_json(open('/home/bspang/ifip21-buffer-sizing/tables/tofino-1/select_mirror_sid.json').read())
p4.SwitchEgress.queue_mirrorer.check_mirroring.set_default_with_enable_mirroring()

ports = [180,183,189]
drop_ctls = [0,1,2]

for port in ports:
    p4.SwitchEgress.wred.qdepth_threshold_cells.mod(register_index=port, f1=20000)

qdepth_hist = p4.SwitchEgress.stats.qdepth_hist

# All entries below will have the same match_priority=0. If you want to use
# overlapping ranges, match_priority must be explicitly specified
for port in ports:
    # for i in range(5650):
    #     qdepth_hist.add_with_count_qdepth_stats(egress_port=port, deq_qdepth=i)
    for i in range(10):
        qdepth_hist.add_with_count_qdepth_stats(egress_port=port, deq_qdepth=i)

    for i in range(1,150):
        qdepth_hist.add_with_count_qdepth_stats(egress_port=port, deq_qdepth=113*i)

    # for i in range(112, 4520):
    #     qdepth_hist.add_with_count_qdepth_stats(egress_port=port, deq_qdepth=113*i)

# for i in range(0,18):
#     #for d in drop_ctls:
#     if i == 4:
#         for j in range(2**i, 2**(i+1)):
#             qdepth_hist.add_with_count_qdepth_stats(deq_qdepth_start=j, deq_qdepth_end=j)
#     else:
#         qdepth_hist.add_with_count_qdepth_stats(deq_qdepth_start=2**i, deq_qdepth_end=2**(i+1))


flow_stats_hist = p4.SwitchEgress.stats.flow_stats_hist
for i in ports:
    for j in ports:
        for d in drop_ctls:
            flow_stats_hist.add_with_count_flow_stats(egress_port=i, original_ingress_port=j, drop_ctl=d)

print ("Table qdepth_hist:")
qdepth_hist.dump(table=True)

print ("Table flow_stats_hist:")
flow_stats_hist.dump(table=True)
