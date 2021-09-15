#include <core.p4>
#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

#include "types.p4"
#include "common/headers.p4"
#include "common/util.p4"

#include "queue_enforcer.p4"
#include "stats.p4"
#include "queue_reporter.p4"

// ---------------------------------------------------------------------------
// Ingress parser
// ---------------------------------------------------------------------------
parser SwitchIngressParser(
    packet_in pkt,
    out header_t hdr,
    out empty_metadata_t ig_md,
    out ingress_intrinsic_metadata_t ig_intr_md) {

    TofinoIngressParser() tofino_parser;

    state start {
        tofino_parser.apply(pkt, ig_intr_md);
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition parse_ipv4;
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition accept;
    }
}

control SwitchIngress(
    inout header_t hdr,
    inout empty_metadata_t ig_md,
    in ingress_intrinsic_metadata_t ig_intr_md,
    in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md) {

    action hit(PortId_t port) {
        ig_tm_md.ucast_egress_port = port;
    }

    action miss(bit<3> drop) {
        ig_dprsr_md.drop_ctl = drop; // Drop packet.
    }

    table forward {
        key = {
            hdr.ethernet.dst_addr : exact;
        }

        actions = {
            hit;
            @defaultonly miss;
        }

        const default_action = miss(0x1);
        size = 1024;
    }

    Hash<bit<9>>(HashAlgorithm_t.IDENTITY) set_mirror_ingress_port;
    action mirror_ingress_port() {
        hdr.mirror.original_ingress_port = set_mirror_ingress_port.get(ig_intr_md.ingress_port);
    }
    table assign_mirror_ingress_port {
        actions = { mirror_ingress_port; }
        const default_action = mirror_ingress_port();
    }

    apply {
        forward.apply();

        //hdr.ipv4.ttl = hdr.ipv4.ttl - 1;

        hdr.mirror.setValid();
        hdr.mirror.is_mirrored = false;
        assign_mirror_ingress_port.apply();
    }
}

// ---------------------------------------------------------------------------
// Ingress Deparser
// ---------------------------------------------------------------------------
control SwitchIngressDeparser(
    packet_out pkt,
    inout header_t hdr,
    in empty_metadata_t ig_md,
    in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md) {

    Checksum() ipv4_checksum;

    apply {
        hdr.ipv4.hdr_checksum = ipv4_checksum.update({
                hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.diffserv,
                hdr.ipv4.total_len,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.frag_offset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.src_addr,
                hdr.ipv4.dst_addr});

        pkt.emit(hdr.mirror);
        pkt.emit(hdr.ethernet);
        pkt.emit(hdr.ipv4);
    }
}

// ---------------------------------------------------------------------------
// Egress Parser
// ---------------------------------------------------------------------------
parser SwitchEgressParser(
    packet_in pkt,
    out header_t hdr,
    out egress_metadata_t eg_md,
    out egress_intrinsic_metadata_t eg_intr_md) {

    TofinoEgressParser() tofino_parser;
    Checksum() tcp_checksum;

    state start {
        tofino_parser.apply(pkt, eg_intr_md);

        transition parse_mirror;
    }

    state parse_mirror {
        pkt.extract(hdr.mirror);
        
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition parse_ipv4;
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);

        transition select(hdr.ipv4.protocol) {
            IP_PROTOCOLS_TCP : parse_tcp;
            IP_PROTOCOLS_UDP : parse_udp;
            default : accept;
        }
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);

        // The intent here is to pull all the tcp headers out of the checksum
        // so that we can get the body checksum without knowing the body. later we will put
        // them back. I think this works because the checksum is essentially adding bits over
        // F_2 with some carrying stuff and there are no sign errors in F_2.
        tcp_checksum.subtract({
                hdr.tcp.src_port,
                hdr.tcp.dst_port,
                hdr.tcp.seq_no,
                hdr.tcp.ack_no,
                hdr.tcp.data_offset,
                hdr.tcp.res,
                hdr.tcp.ns,
                hdr.tcp.cwr,
                hdr.tcp.ece,
                hdr.tcp.urg,
                hdr.tcp.ack,
                hdr.tcp.psh,
                hdr.tcp.rst,
                hdr.tcp.syn,
                hdr.tcp.fin,
                hdr.tcp.window,
                hdr.tcp.checksum,
                hdr.tcp.urgent_ptr
            });

        eg_md.data_checksum = tcp_checksum.get();

        transition accept;
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition accept;
    }
}

control SwitchEgress(
    inout header_t hdr,
    inout egress_metadata_t eg_md,
    in egress_intrinsic_metadata_t eg_intr_md,
    in egress_intrinsic_metadata_from_parser_t eg_intr_from_prsr,
    inout egress_intrinsic_metadata_for_deparser_t eg_intr_md_for_dprsr,
    inout egress_intrinsic_metadata_for_output_port_t eg_intr_md_for_oport) {

    QueueEnforcer() queue_enforcer;
    Stats() stats;

    QueueReporter() queue_reporter;
    QueueMirrorer() queue_mirrorer;

    apply {
        if (hdr.mirror.is_mirrored) {
            // Second time around, turn the packet into a queue report postcard
            queue_reporter.apply(hdr, eg_intr_md, eg_intr_md_for_dprsr);

            // add the mirror header
            hdr.queue_report = hdr.mirror;
            hdr.queue_report.setValid();

            hdr.queue_report_padding._padding = 0;
            hdr.queue_report_padding.setValid();

        } else {
            // First time around, apply the queueing/stats logic and then
            // set up the mirroring
            queue_enforcer.apply(hdr, eg_intr_md, eg_intr_md_for_dprsr);
            stats.apply(hdr, eg_intr_md, eg_intr_md_for_dprsr);

            queue_mirrorer.apply(hdr, eg_md, eg_intr_md, eg_intr_md_for_dprsr);
        }
    }
}

// ---------------------------------------------------------------------------
// Egress Deparser
// ---------------------------------------------------------------------------
control SwitchEgressDeparser(packet_out pkt,
    inout header_t hdr,
    in egress_metadata_t eg_md,
    in egress_intrinsic_metadata_for_deparser_t eg_intr_dprs_md) {

    Checksum() ipv4_checksum;
    Checksum() tcp_checksum;
    Mirror() mirror;

    apply {
        if (eg_intr_dprs_md.mirror_type == 3w1) {
            mirror.emit<mirror_h>(eg_md.mirror_sid, hdr.mirror);
        }

        pkt.emit(hdr.ethernet);

        if (hdr.ipv4.isValid()) {
            hdr.ipv4.hdr_checksum = ipv4_checksum.update(
                {hdr.ipv4.version,
                    hdr.ipv4.ihl,
                    hdr.ipv4.diffserv,
                    hdr.ipv4.total_len,
                    hdr.ipv4.identification,
                    hdr.ipv4.flags,
                    hdr.ipv4.frag_offset,
                    hdr.ipv4.ttl,
                    hdr.ipv4.protocol,
                    hdr.ipv4.src_addr,
                    hdr.ipv4.dst_addr});

        }
        pkt.emit(hdr.ipv4);

        if (hdr.tcp.isValid()) {
            // Update the checksum with the new tcp flags we may have set.
            hdr.tcp.checksum = tcp_checksum.update({
                    hdr.tcp.src_port,
                    hdr.tcp.dst_port,
                    hdr.tcp.seq_no,
                    hdr.tcp.ack_no,
                    hdr.tcp.data_offset,
                    hdr.tcp.res,
                    hdr.tcp.ns,
                    hdr.tcp.cwr,
                    hdr.tcp.ece,
                    hdr.tcp.urg,
                    hdr.tcp.ack,
                    hdr.tcp.psh,
                    hdr.tcp.rst,
                    hdr.tcp.syn,
                    hdr.tcp.fin,
                    hdr.tcp.window,
                    // including the previous checksum here because we subtracted out
                    // everything else we're adding in the egress parser.
                    eg_md.data_checksum,
                    hdr.tcp.urgent_ptr
                });

        }
        pkt.emit(hdr.udp);
        pkt.emit(hdr.tcp);

        pkt.emit(hdr.queue_report);
        pkt.emit(hdr.queue_report_padding);
    }
}

Pipeline(
    SwitchIngressParser(),
    SwitchIngress(),
    SwitchIngressDeparser(),
    SwitchEgressParser(),
    SwitchEgress(),
    SwitchEgressDeparser()
) pipe;

Switch(pipe) main;
