#include "types.p4"

control Stats(
    inout header_t hdr,
    // in egress_metadata_t eg_md,
    in egress_intrinsic_metadata_t eg_intr_md,
    inout egress_intrinsic_metadata_for_deparser_t eg_intr_md_for_dprsr)
{
    /* The template type reflects the total width of the counter pair */
    DirectCounter<bit<32>>(CounterType_t.PACKETS) qdepth_stats;

    action count_qdepth_stats() {
        qdepth_stats.count();
    }

    table qdepth_hist {
        key = {
            eg_intr_md.egress_port : exact;
            eg_intr_md.deq_qdepth : exact;
            //eg_intr_md_for_dprsr.drop_ctl : exact;
        }
        actions = {
            count_qdepth_stats;
        }
        counters = qdepth_stats;
        size = 65535;
    }

    /* The template type reflects the total width of the counter pair */
    DirectCounter<bit<32>>(CounterType_t.PACKETS) flow_stats;

    action count_flow_stats() {
        flow_stats.count();
    }

    table flow_stats_hist {
        key = {
            hdr.mirror.original_ingress_port : exact;
            eg_intr_md.egress_port : exact;
            eg_intr_md_for_dprsr.drop_ctl : exact;
        }
        actions = {
            count_flow_stats;
        }
        counters = flow_stats;
        size = 512;
    }

    apply {
        qdepth_hist.apply();
        flow_stats_hist.apply();
    }
}
