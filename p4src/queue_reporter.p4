#include "types.p4"

control QueueMirrorer(
    inout header_t hdr,
    inout egress_metadata_t eg_md,
    in egress_intrinsic_metadata_t eg_intr_md,
    inout egress_intrinsic_metadata_for_deparser_t eg_intr_md_for_dprsr)
{
    Hash<bit<32>>(HashAlgorithm_t.IDENTITY) set_mirror_src_ip;
    action mirror_src_ip() {
        hdr.mirror.ipv4_src_addr = set_mirror_src_ip.get(hdr.ipv4.src_addr);
    }
    table assign_mirror_src_ip {
        actions = { mirror_src_ip; }
        const default_action = mirror_src_ip();
    }

    Hash<bit<32>>(HashAlgorithm_t.IDENTITY) set_mirror_dst_ip;
    action mirror_dst_ip() {
        hdr.mirror.ipv4_dst_addr = set_mirror_dst_ip.get(hdr.ipv4.dst_addr);
    }
    table assign_mirror_dst_ip {
        actions = { mirror_dst_ip; }
        const default_action = mirror_dst_ip();
    }

    Hash<bit<16>>(HashAlgorithm_t.IDENTITY) set_mirror_src_port;
    action mirror_src_port() {
        hdr.mirror.src_port = set_mirror_src_port.get(hdr.tcp.src_port);
    }
    table assign_mirror_src_port {
        actions = { mirror_src_port; }
        const default_action = mirror_src_port();
    }

    Hash<bit<16>>(HashAlgorithm_t.IDENTITY) set_mirror_dst_port;
    action mirror_dst_port() {
        hdr.mirror.dst_port = set_mirror_dst_port.get(hdr.tcp.dst_port);
    }
    table assign_mirror_dst_port {
        actions = { mirror_dst_port; }
        const default_action = mirror_dst_port();
    }

    Hash<bit<32>>(HashAlgorithm_t.IDENTITY) set_mirror_seq_no;
    action mirror_seq_no() {
        hdr.mirror.seq_no = set_mirror_seq_no.get(hdr.tcp.seq_no);
    }
    table assign_mirror_seq_no {
        actions = { mirror_seq_no; }
        const default_action = mirror_seq_no();
    }

    Hash<bit<32>>(HashAlgorithm_t.IDENTITY) set_mirror_ack_no;
    action mirror_ack_no() {
        hdr.mirror.ack_no = set_mirror_ack_no.get(hdr.tcp.ack_no);
    }
    table assign_mirror_ack_no {
        actions = { mirror_ack_no; }
        const default_action = mirror_ack_no();
    }

    Hash<qdepth_t>(HashAlgorithm_t.IDENTITY) set_mirror_queue_depth;
    action mirror_queue_depth() {
        hdr.mirror.queue_depth = set_mirror_queue_depth.get((qdepth_t) eg_intr_md.deq_qdepth);
    }
    table assign_mirror_queue_depth {
        actions = { mirror_queue_depth; }
        const default_action = mirror_queue_depth();
    }

    Hash<bit<32>>(HashAlgorithm_t.IDENTITY) set_mirror_timestamp;
    action mirror_timestamp() {
        hdr.mirror.timestamp = set_mirror_timestamp.get((bit<32>) eg_intr_md.enq_tstamp);
    }
    table assign_mirror_timestamp {
        actions = { mirror_timestamp; }
        const default_action = mirror_timestamp();
    }

    Hash<port_t>(HashAlgorithm_t.IDENTITY) set_mirror_original_egress_port;
    action mirror_original_egress_port() {
        hdr.mirror.original_egress_port = set_mirror_original_egress_port.get((port_t) eg_intr_md.egress_port);
    }
    table assign_mirror_original_egress_port {
        actions = { mirror_original_egress_port; }
        const default_action = mirror_original_egress_port();
    }

    Hash<bit<3>>(HashAlgorithm_t.IDENTITY) set_mirror_was_dropped;
    action mirror_was_dropped() {
        hdr.mirror.was_dropped = set_mirror_was_dropped.get(eg_intr_md_for_dprsr.drop_ctl);
    }
    table assign_mirror_was_dropped {
        actions = { mirror_was_dropped; }
        const default_action = mirror_was_dropped();
    }

    action set_mirror_sid(MirrorId_t eg_ses) {
        eg_md.mirror_sid = eg_ses;
    }
    
    table select_mirror_sid {
        key = {
            hdr.mirror.original_ingress_port: exact;
        }
        actions = {
            set_mirror_sid;
        }
        size = 256; // mirror_type is a field of 3 bits
    }

    // Some configuration to enable/disable postcards via the cli
    bool should_do_mirroring;
    
    action enable_mirroring() {
        should_do_mirroring = true;
    }
    
    action disable_mirroring() {
        should_do_mirroring = false;
    }
    
    table check_mirroring {
        actions = {
            enable_mirroring;
            disable_mirroring;
        }
        default_action = disable_mirroring;
        size = 512;
    }


    apply {
        // TODO: possibly will not mirror already dropped packets-test this out!
        // TODO: possible bug where we will emit junk headers for non tcp packets,
        // but ifs and mirrors don't play well together in tofino

        check_mirroring.apply();
        if (!should_do_mirroring) {
            return;
        }

        select_mirror_sid.apply();
        
        hdr.mirror.setValid(); // Already valid
        hdr.mirror.is_mirrored = true;
        assign_mirror_src_ip.apply();
        assign_mirror_dst_ip.apply();
        assign_mirror_src_port.apply();
        assign_mirror_dst_port.apply();

        assign_mirror_seq_no.apply();
        assign_mirror_ack_no.apply();

        assign_mirror_queue_depth.apply();
        
        // XXX: Setting to zero now so we can be hacky in the tests.
        hdr.mirror.timestamp = 0;

        assign_mirror_was_dropped.apply();

        assign_mirror_original_egress_port.apply();

        hdr.queue_report.setInvalid();

        eg_intr_md_for_dprsr.mirror_type = 3w1;

    }
}

control QueueReporter(
    inout header_t hdr,
    // in egress_metadata_t eg_md,
    in egress_intrinsic_metadata_t eg_intr_md,
    inout egress_intrinsic_metadata_for_deparser_t eg_intr_md_for_dprsr){


    apply {
        // TODO: does not work for acks

        // pick mac address to send to
        mac_addr_t tmp_mac = hdr.ethernet.dst_addr;
        hdr.ethernet.dst_addr = hdr.ethernet.src_addr;
        hdr.ethernet.src_addr = tmp_mac;

        // pick ip address to send to
        ipv4_addr_t tmp_ip = hdr.ipv4.dst_addr;
        hdr.ipv4.dst_addr = hdr.ipv4.src_addr;
        hdr.ipv4.src_addr = tmp_ip;

        // change next protocol information on ip header
        hdr.ipv4.protocol = IP_PROTOCOLS_UDP;
        hdr.ipv4.total_len = IPV4_HEADER_LEN_BYTES + UDP_HEADER_LEN_BYTES + MIRROR_HEADER_LEN_BYTES + PADDING_HEADER_LEN_BYTES;

        // unset tcp header
        hdr.tcp.setInvalid();

        // add udp header
        hdr.udp.setValid();

        // TODO: make this configurable
        // - set the port
        hdr.udp.src_port = 4444;
        hdr.udp.dst_port = 4444;

        // - set the packet length
        hdr.udp.hdr_length = UDP_HEADER_LEN_BYTES + MIRROR_HEADER_LEN_BYTES + PADDING_HEADER_LEN_BYTES;

        // - set the checksum
        hdr.udp.checksum = 0;

        eg_intr_md_for_dprsr.mirror_type = 3w0;
    }
}
