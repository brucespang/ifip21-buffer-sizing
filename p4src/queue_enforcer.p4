#include "types.p4"

control QueueEnforcer(
    inout header_t hdr,
    in egress_intrinsic_metadata_t eg_intr_md,
    inout egress_intrinsic_metadata_for_deparser_t eg_intr_md_for_dprsr
) {

    bool is_sender_packet = false;
    bool exceeds_threshold = false;
    bool ecnEnabled = false;

    const bit<32> number_of_ports = 256;

    Register<qdepth_t, port_t>(number_of_ports, 0) port_to_qdepth;
    RegisterAction<qdepth_t, port_t, qdepth_t>(port_to_qdepth) port_qdepth_reg_set = {
        void apply(inout qdepth_t val) {
            val = (bit<32>)eg_intr_md.deq_qdepth;
        }
    };

    // XXX: I think "0" here is the default value, which is probably not correct
    // Tofino stores deq_qdepth in units of 80-byte cells.
    Register<qdepth_t, port_t>(number_of_ports, 0) qdepth_threshold_cells;
    RegisterAction<qdepth_t, port_t, bool>(qdepth_threshold_cells) qdepth_exceeds_threshold = {
        void apply(inout qdepth_t threshold, out bool rv) {
            rv = (eg_intr_md.deq_qdepth >= threshold[18:0]);
        }
    };

    action set_tcp_ecn() {
        hdr.tcp.ece = 1;
    }

    action nop() {}
    action set_sender_packet() {
        is_sender_packet = true;
    }

    action drop() {
        eg_intr_md_for_dprsr.drop_ctl = 1; // Drop packet.
    }

    action set_ipv4_ecn() {
        ecnEnabled = true;
    }

    table sender_action {
        key = {
            exceeds_threshold : exact;
        }

        actions = {
            drop;
            set_ipv4_ecn;
            nop;
        }

        size = 2;
    }

    apply {
        // for some reason, han-3 started generating TCP SYN's with ECT(0) set
        // which han-2 does not like. I think this is possibly related to some change
        // in the kernel (e.g. http://lkml.iu.edu/hypermail/linux/kernel/1904.0/03502.html).
        // Don't want to try and figure out what's up with that, so hacky hacky fix.
        if (hdr.tcp.isValid() && (hdr.tcp.syn == 1)) {
            hdr.ipv4.diffserv[1:0] = 0;
        }

        exceeds_threshold = qdepth_exceeds_threshold.execute(eg_intr_md.egress_port);

        // check if the queue depth exceeds the threshold
        sender_action.apply();

        // If we're doing ECN, set it. This isn't in the action, since
        // the compiler has issues with if statements and actions.
        if (ecnEnabled){
            if (hdr.ipv4.diffserv[1:0] == 1 || hdr.ipv4.diffserv[1:0] == 2){
                // Mark ECN
                hdr.ipv4.diffserv[1:0] = SWITCH_ECN_CODEPOINT_CE;
            }
        }

        port_qdepth_reg_set.execute(eg_intr_md.egress_port);
    }
}
