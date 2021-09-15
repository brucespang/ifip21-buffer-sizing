/*******************************************************************************
 * BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
 *
 * Copyright (c) 2015-2019 Barefoot Networks, Inc.

 * All Rights Reserved.
 *
 * NOTICE: All information contained herein is, and remains the property of
 * Barefoot Networks, Inc. and its suppliers, if any. The intellectual and
 * technical concepts contained herein are proprietary to Barefoot Networks,
 * Inc.
 * and its suppliers and may be covered by U.S. and Foreign Patents, patents in
 * process, and are protected by trade secret or copyright law.
 * Dissemination of this information or reproduction of this material is
 * strictly forbidden unless prior written permission is obtained from
 * Barefoot Networks, Inc.
 *
 * No warranty, explicit or implicit is provided, unless granted under a
 * written agreement with Barefoot Networks, Inc.
 *
 ******************************************************************************/

#ifndef _P4_TYPES_
#define _P4_TYPES_

// ----------------------------------------------------------------------------
// Common protocols/types
//-----------------------------------------------------------------------------
#define ETHERTYPE_IPV4 0x0800
#define ETHERTYPE_ARP  0x0806
#define ETHERTYPE_VLAN 0x8100
#define ETHERTYPE_IPV6 0x86dd
#define ETHERTYPE_MPLS 0x8847
#define ETHERTYPE_PTP  0x88F7
#define ETHERTYPE_FCOE 0x8906
#define ETHERTYPE_ROCE 0x8915
#define ETHERTYPE_BFN  0x9000
//#define ETHERTYPE_QINQ 0x88A8 // Note: uncomment once ptf/scapy-vxlan are fixed
#define ETHERTYPE_QINQ 0x8100

#define IP_PROTOCOLS_ICMP   1
#define IP_PROTOCOLS_IGMP   2
#define IP_PROTOCOLS_IPV4   4
#define IP_PROTOCOLS_TCP    6
#define IP_PROTOCOLS_UDP    17
#define IP_PROTOCOLS_IPV6   41
#define IP_PROTOCOLS_SRV6   43
#define IP_PROTOCOLS_GRE    47
#define IP_PROTOCOLS_ICMPV6 58

#define UDP_PORT_VXLAN  4789
#define UDP_PORT_ROCEV2 4791
#define UDP_PORT_GENV   6081
#define UDP_PORT_SFLOW  6343
#define UDP_PORT_MPLS   6635

#define GRE_PROTOCOLS_ERSPAN_TYPE_3 0x22EB
#define GRE_PROTOCOLS_NVGRE         0x6558
#define GRE_PROTOCOLS_IP            0x0800
#define GRE_PROTOCOLS_ERSPAN_TYPE_2 0x88BE

#define VLAN_DEPTH 2
#define MPLS_DEPTH 3


// ----------------------------------------------------------------------------
// Common types
//-----------------------------------------------------------------------------
typedef bit<32> switch_uint32_t;
typedef bit<16> switch_uint16_t;
typedef bit<8> switch_uint8_t;

typedef PortId_t switch_port_t;
const switch_port_t SWITCH_PORT_INVALID = 9w0x1ff;

typedef QueueId_t switch_qid_t;

typedef ReplicationId_t switch_rid_t;
const switch_rid_t SWITCH_RID_DEFAULT = 0xffff;

typedef bit<3> switch_ingress_cos_t;

typedef bit<3> switch_digest_type_t;
const switch_digest_type_t SWITCH_DIGEST_TYPE_INVALID = 0;
const switch_digest_type_t SWITCH_DIGEST_TYPE_MAC_LEARNING = 1;

typedef bit<16> switch_ifindex_t;
typedef bit<10> switch_port_lag_index_t;
const switch_port_lag_index_t SWITCH_FLOOD = 0x3ff;

typedef bit<16> switch_bd_t;
const switch_bd_t SWITCH_BD_DEFAULT_VRF = 4097; // bd allocated for default vrf

#ifndef switch_vrf_width
#define switch_vrf_width 14
#endif
typedef bit<switch_vrf_width> switch_vrf_t;

#ifndef switch_nexthop_width
#define switch_nexthop_width 16
#endif
typedef bit<switch_nexthop_width> switch_nexthop_t;
typedef bit<16> switch_outer_nexthop_t;

#ifndef switch_user_metadata_width
#define switch_user_metadata_width 10
#endif
typedef bit<switch_user_metadata_width> switch_user_metadata_t;

#ifdef RESILIENT_ECMP_HASH_ENABLE
#define switch_hash_width 64
#else
#define switch_hash_width 32
#endif
typedef bit<switch_hash_width> switch_hash_t;

typedef bit<16> switch_xid_t;
typedef bit<9> switch_yid_t;

#ifdef PORT_GROUP_IN_ACL_KEY_ENABLE
typedef bit<32> switch_port_lag_label_t;
#else
typedef bit<16> switch_port_lag_label_t;
#endif
typedef bit<16> switch_bd_label_t;
typedef bit<16> switch_if_label_t;

typedef bit<10> switch_rmac_group_t;
typedef bit<16> switch_smac_index_t;

typedef bit<16> switch_mtu_t;

typedef bit<12> switch_stats_index_t;

typedef bit<16> switch_cpu_reason_t;
const switch_cpu_reason_t SWITCH_CPU_REASON_PTP = 8;

struct switch_cpu_port_value_set_t {
    bit<16> ether_type;
    bit<9> port;
}

#define switch_drop_reason_width 8
typedef bit<switch_drop_reason_width> switch_drop_reason_t;
const switch_drop_reason_t SWITCH_DROP_REASON_UNKNOWN = 0;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_SRC_MAC_ZERO = 10;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_SRC_MAC_MULTICAST = 11;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_DST_MAC_ZERO = 12;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_ETHERNET_MISS = 13;
const switch_drop_reason_t SWITCH_DROP_REASON_SRC_MAC_ZERO = 14;
const switch_drop_reason_t SWITCH_DROP_REASON_SRC_MAC_MULTICAST = 15;
const switch_drop_reason_t SWITCH_DROP_REASON_DST_MAC_ZERO = 16;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_IP_VERSION_INVALID = 25;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_IP_TTL_ZERO = 26;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_IP_SRC_MULTICAST = 27;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_IP_SRC_LOOPBACK = 28;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_IP_MISS = 29;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_IP_IHL_INVALID = 30;
const switch_drop_reason_t SWITCH_DROP_REASON_OUTER_IP_INVALID_CHECKSUM = 31;
const switch_drop_reason_t SWITCH_DROP_REASON_IP_VERSION_INVALID = 40;
const switch_drop_reason_t SWITCH_DROP_REASON_IP_TTL_ZERO = 41;
const switch_drop_reason_t SWITCH_DROP_REASON_IP_SRC_MULTICAST = 42;
const switch_drop_reason_t SWITCH_DROP_REASON_IP_SRC_LOOPBACK = 43;
const switch_drop_reason_t SWITCH_DROP_REASON_IP_IHL_INVALID = 44;
const switch_drop_reason_t SWITCH_DROP_REASON_IP_INVALID_CHECKSUM = 45;
const switch_drop_reason_t SWITCH_DROP_REASON_PORT_VLAN_MAPPING_MISS = 55;
const switch_drop_reason_t SWITCH_DROP_REASON_STP_STATE_LEARNING = 56;
const switch_drop_reason_t SWITCH_DROP_REASON_STP_STATE_BLOCKING = 57;
const switch_drop_reason_t SWITCH_DROP_REASON_SAME_IFINDEX = 58;
const switch_drop_reason_t SWITCH_DROP_REASON_MULTICAST_SNOOPING_ENABLED = 59;
const switch_drop_reason_t SWITCH_DROP_REASON_MTU_CHECK_FAIL = 70;
const switch_drop_reason_t SWITCH_DROP_REASON_TRAFFIC_MANAGER = 71;
const switch_drop_reason_t SWITCH_DROP_REASON_STORM_CONTROL = 72;
const switch_drop_reason_t SWITCH_DROP_REASON_WRED = 73;
const switch_drop_reason_t SWITCH_DROP_REASON_INGRESS_PORT_METER = 75;
const switch_drop_reason_t SWITCH_DROP_REASON_INGRESS_ACL_METER = 76;
const switch_drop_reason_t SWITCH_DROP_REASON_EGRESS_PORT_METER = 77;
const switch_drop_reason_t SWITCH_DROP_REASON_EGRESS_ACL_METER = 78;
const switch_drop_reason_t SWITCH_DROP_REASON_ACL_DENY = 80;
const switch_drop_reason_t SWITCH_DROP_REASON_RACL_DENY = 81;
const switch_drop_reason_t SWITCH_DROP_REASON_URPF_CHECK_FAIL = 82;
const switch_drop_reason_t SWITCH_DROP_REASON_IPSG_MISS = 83;
const switch_drop_reason_t SWITCH_DROP_REASON_IFINDEX = 84;
const switch_drop_reason_t SWITCH_DROP_REASON_CPU_COLOR_YELLOW = 85;
const switch_drop_reason_t SWITCH_DROP_REASON_CPU_COLOR_RED = 86;
const switch_drop_reason_t SWITCH_DROP_REASON_STORM_CONTROL_COLOR_YELLOW = 87;
const switch_drop_reason_t SWITCH_DROP_REASON_STORM_CONTROL_COLOR_RED = 88;
const switch_drop_reason_t SWITCH_DROP_REASON_L2_MISS_UNICAST = 89;
const switch_drop_reason_t SWITCH_DROP_REASON_L2_MISS_MULTICAST = 90;
const switch_drop_reason_t SWITCH_DROP_REASON_L2_MISS_BROADCAST = 91;
const switch_drop_reason_t SWITCH_DROP_REASON_EGRESS_ACL_DENY = 92;
const switch_drop_reason_t SWITCH_DROP_REASON_NEXTHOP = 93;
const switch_drop_reason_t SWITCH_DROP_REASON_NON_IP_ROUTER_MAC = 94;
const switch_drop_reason_t SWITCH_DROP_REASON_MLAG_MEMBER = 95;
const switch_drop_reason_t SWITCH_DROP_REASON_L3_IPV4_DISABLE = 99;
const switch_drop_reason_t SWITCH_DROP_REASON_L3_IPV6_DISABLE = 100;
const switch_drop_reason_t SWITCH_DROP_REASON_INGRESS_PFC_WD_DROP = 101;
const switch_drop_reason_t SWITCH_DROP_REASON_EGRESS_PFC_WD_DROP = 102;

typedef bit<1> switch_port_type_t;
const switch_port_type_t SWITCH_PORT_TYPE_NORMAL = 0;
const switch_port_type_t SWITCH_PORT_TYPE_CPU = 1;

typedef bit<2> switch_ip_type_t;
const switch_ip_type_t SWITCH_IP_TYPE_NONE = 0;
const switch_ip_type_t SWITCH_IP_TYPE_IPV4 = 1;
const switch_ip_type_t SWITCH_IP_TYPE_IPV6 = 2;

typedef bit<2> switch_ip_frag_t;
const switch_ip_frag_t SWITCH_IP_FRAG_NON_FRAG = 0b00; // Not fragmented.
const switch_ip_frag_t SWITCH_IP_FRAG_HEAD = 0b10; // First fragment of the fragmented packets.
const switch_ip_frag_t SWITCH_IP_FRAG_NON_HEAD = 0b11; // Fragment with non-zero offset.

// Bypass flags ---------------------------------------------------------------
typedef bit<16> switch_ingress_bypass_t;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_L2 = 16w0x0001;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_L3 = 16w0x0002;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_ACL = 16w0x0004;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_SYSTEM_ACL = 16w0x0008;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_QOS = 16w0x0010;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_METER = 16w0x0020;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_STORM_CONTROL = 16w0x0040;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_STP = 16w0x0080;
const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_SMAC = 16w0x0100;

// Add more ingress bypass flags here.

const switch_ingress_bypass_t SWITCH_INGRESS_BYPASS_ALL = 16w0xffff;
#define INGRESS_BYPASS(t) (ig_md.bypass & SWITCH_INGRESS_BYPASS_##t != 0)

typedef bit<8> switch_egress_bypass_t;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_REWRITE = 8w0x01;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_ACL = 8w0x02;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_SYSTEM_ACL = 8w0x04;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_QOS = 8w0x08;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_WRED = 8w0x10;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_STP = 8w0x20;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_MTU = 8w0x40;
const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_METER = 8w0x80;

// Add more egress bypass flags here.

const switch_egress_bypass_t SWITCH_EGRESS_BYPASS_ALL = 8w0xff;
#define EGRESS_BYPASS(t) (eg_md.bypass & SWITCH_EGRESS_BYPASS_##t != 0)


// PKT ------------------------------------------------------------------------
typedef bit<16> switch_pkt_length_t;

typedef bit<8> switch_pkt_src_t;
const switch_pkt_src_t SWITCH_PKT_SRC_BRIDGED = 0;
const switch_pkt_src_t SWITCH_PKT_SRC_CLONED_INGRESS = 1;
const switch_pkt_src_t SWITCH_PKT_SRC_CLONED_EGRESS = 2;
const switch_pkt_src_t SWITCH_PKT_SRC_DEFLECTED = 3;

typedef bit<2> switch_pkt_color_t;
const switch_pkt_color_t SWITCH_METER_COLOR_GREEN = 0;
const switch_pkt_color_t SWITCH_METER_COLOR_YELLOW = 1;
const switch_pkt_color_t SWITCH_METER_COLOR_RED = 3;

typedef bit<2> switch_pkt_type_t;
const switch_pkt_type_t SWITCH_PKT_TYPE_UNICAST = 0;
const switch_pkt_type_t SWITCH_PKT_TYPE_MULTICAST = 1;
const switch_pkt_type_t SWITCH_PKT_TYPE_BROADCAST = 2;

// LOU ------------------------------------------------------------------------
#define switch_l4_port_label_width 8
typedef bit<switch_l4_port_label_width> switch_l4_port_label_t;

// STP ------------------------------------------------------------------------
typedef bit<2> switch_stp_state_t;
const switch_stp_state_t SWITCH_STP_STATE_FORWARDING = 0;
const switch_stp_state_t SWITCH_STP_STATE_BLOCKING = 1;
const switch_stp_state_t SWITCH_STP_STATE_LEARNING = 2;

typedef bit<10> switch_stp_group_t;

struct switch_stp_metadata_t {
    switch_stp_group_t group;
    switch_stp_state_t state_;
}

// Sflow ----------------------------------------------------------------------
typedef bit<8> switch_sflow_id_t;
const switch_sflow_id_t SWITCH_SFLOW_INVALID_ID = 8w0xff;

struct switch_sflow_metadata_t {
    switch_sflow_id_t session_id;
    bit<1> sample_packet;
}

// Metering -------------------------------------------------------------------
#define switch_copp_meter_id_width 8
typedef bit<switch_copp_meter_id_width> switch_copp_meter_id_t;

#define switch_meter_index_width 10
typedef bit<switch_meter_index_width> switch_meter_index_t;

#define switch_mirror_meter_id_width 8
typedef bit<switch_mirror_meter_id_width> switch_mirror_meter_id_t;

// QoS ------------------------------------------------------------------------
typedef bit<2> switch_qos_trust_mode_t;
const switch_qos_trust_mode_t SWITCH_QOS_TRUST_MODE_UNTRUSTED = 0;
const switch_qos_trust_mode_t SWITCH_QOS_TRUST_MODE_TRUST_DSCP = 1;
const switch_qos_trust_mode_t SWITCH_QOS_TRUST_MODE_TRUST_PCP = 2;

typedef bit<5> switch_qos_group_t;

#define switch_tc_width 8
typedef bit<switch_tc_width> switch_tc_t;
typedef bit<3> switch_cos_t;

// struct switch_qos_metadata_t {
//     switch_qos_trust_mode_t trust_mode; // Ingress only.
//     switch_qos_group_t group;
//     switch_tc_t tc;
//     switch_pkt_color_t color;
//     switch_pkt_color_t acl_meter_color;
//     switch_pkt_color_t port_color;
//     switch_pkt_color_t flow_color;
//     switch_pkt_color_t storm_control_color;
//     switch_meter_index_t port_meter_index;
//     switch_meter_index_t acl_meter_index;
//     switch_qid_t qid;
//     switch_ingress_cos_t icos; // Ingress only.
//     bit<19> qdepth; // Egress only.
// }

// Learning -------------------------------------------------------------------
typedef bit<1> switch_learning_mode_t;
const switch_learning_mode_t SWITCH_LEARNING_MODE_DISABLED = 0;
const switch_learning_mode_t SWITCH_LEARNING_MODE_LEARN = 1;

// struct switch_learning_digest_t {
//     switch_bd_t bd;
//     switch_port_lag_index_t port_lag_index;
//     mac_addr_t src_addr;
// }

// struct switch_learning_metadata_t {
//     switch_learning_mode_t bd_mode;
//     switch_learning_mode_t port_mode;
//     switch_learning_digest_t digest;
// }

// Multicast ------------------------------------------------------------------
typedef bit<2> switch_multicast_mode_t;
const switch_multicast_mode_t SWITCH_MULTICAST_MODE_NONE = 0;
const switch_multicast_mode_t SWITCH_MULTICAST_MODE_PIM_SM = 1; // Sparse mode
const switch_multicast_mode_t SWITCH_MULTICAST_MODE_PIM_BIDIR = 2; // Bidirectional

typedef MulticastGroupId_t switch_mgid_t;

typedef bit<16> switch_multicast_rpf_group_t;

// struct switch_multicast_metadata_t {
//     switch_mgid_t id;
//     bit<2> mode;
//     switch_multicast_rpf_group_t rpf_group;
// }

// URPF -----------------------------------------------------------------------
typedef bit<2> switch_urpf_mode_t;
const switch_urpf_mode_t SWITCH_URPF_MODE_NONE = 0;
const switch_urpf_mode_t SWITCH_URPF_MODE_LOOSE = 1;
const switch_urpf_mode_t SWITCH_URPF_MODE_STRICT = 2;

// WRED/ECN -------------------------------------------------------------------
#define switch_wred_index_width 8
typedef bit<switch_wred_index_width> switch_wred_index_t;

typedef bit<2> switch_ecn_codepoint_t;
const switch_ecn_codepoint_t SWITCH_ECN_CODEPOINT_NON_ECT = 0b00; // Non ECN-capable transport
const switch_ecn_codepoint_t SWITCH_ECN_CODEPOINT_ECT0 = 0b10; // ECN capable transport
const switch_ecn_codepoint_t SWITCH_ECN_CODEPOINT_ECT1 = 0b01; // ECN capable transport
const switch_ecn_codepoint_t SWITCH_ECN_CODEPOINT_CE = 0b11; // Congestion encountered

// Mirroring ------------------------------------------------------------------
typedef MirrorId_t switch_mirror_session_t; // Defined in tna.p4
const switch_mirror_session_t SWITCH_MIRROR_SESSION_CPU = 250;

// Using same mirror type for both Ingress/Egress to simplify the parser.
typedef bit<8> switch_mirror_type_t;
#define SWITCH_MIRROR_TYPE_INVALID 0
#define SWITCH_MIRROR_TYPE_PORT 1
#define SWITCH_MIRROR_TYPE_CPU 2
#define SWITCH_MIRROR_TYPE_DTEL_DROP 3
#define SWITCH_MIRROR_TYPE_DTEL_SWITCH_LOCAL 4
#define SWITCH_MIRROR_TYPE_TRUNCATE_ONLY 5
/* Although strictly speaking deflected packets are not mirrored packets,
 * need a mirror_type codepoint for packet length adjustment.
 * Pick a large value since this is not used by mirror logic.
 */
#define SWITCH_MIRROR_TYPE_DTEL_DEFLECT 255

// Common metadata used for mirroring.
struct switch_mirror_metadata_t {
    switch_pkt_src_t src;
    switch_mirror_type_t type;
    switch_mirror_session_t session_id;
    switch_mirror_meter_id_t meter_index;
}

header switch_port_mirror_metadata_h {
    switch_pkt_src_t src;
    switch_mirror_type_t type;
    bit<48> timestamp;
#if __TARGET_TOFINO__ == 1
    bit<6> _pad;
#endif
    switch_mirror_session_t session_id;

}

header switch_cpu_mirror_metadata_h {
    switch_pkt_src_t src;
    switch_mirror_type_t type;
    bit<7> _pad1;
    switch_port_t port;
    switch_bd_t bd;
    bit<6> _pad2;
    switch_port_lag_index_t port_lag_index;
    switch_cpu_reason_t reason_code;
}

// Tunneling ------------------------------------------------------------------
enum switch_tunnel_mode_t { PIPE, UNIFORM }
typedef bit<3> switch_tunnel_type_t;
const switch_tunnel_type_t SWITCH_TUNNEL_TYPE_NONE = 0;
const switch_tunnel_type_t SWITCH_TUNNEL_TYPE_VXLAN = 1;
const switch_tunnel_type_t SWITCH_TUNNEL_TYPE_IPINIP = 2;

enum switch_tunnel_term_mode_t { P2P, P2MP };

#ifndef switch_tunnel_index_width
#define switch_tunnel_index_width 16
#endif
typedef bit<switch_tunnel_index_width> switch_tunnel_index_t;
typedef bit<24> switch_tunnel_id_t;

struct switch_tunnel_metadata_t {
    switch_tunnel_type_t type;
    switch_tunnel_index_t index;
    switch_tunnel_id_t id;
    switch_ifindex_t ifindex;
    bit<16> hash;
    bool terminate;
}

// Data-plane telemetry (DTel) ------------------------------------------------
/* report_type bits for drop and flow reflect dtel_acl results,
 * i.e. whether drop reports and flow reports may be triggered by this packet.
 * report_type bit for queue is not used by bridged / deflected packets,
 * reflects whether flow report is triggered by this packet in cloned packets.
 */
typedef bit<4> switch_dtel_report_type_t;
const switch_dtel_report_type_t SWITCH_DTEL_REPORT_TYPE_NONE = 0b000;
const switch_dtel_report_type_t SWITCH_DTEL_REPORT_TYPE_DROP = 0b100;
const switch_dtel_report_type_t SWITCH_DTEL_REPORT_TYPE_QUEUE = 0b010;
const switch_dtel_report_type_t SWITCH_DTEL_REPORT_TYPE_FLOW = 0b001;

const switch_dtel_report_type_t SWITCH_DTEL_SUPPRESS_REPORT = 0b1000;

struct switch_dtel_metadata_t {
    switch_dtel_report_type_t report_type;
    bit<32> latency; // Egress only.
    switch_mirror_session_t session_id; // Ingress only.
    bit<32> hash;
    bit<2> drop_report_flag; // Egress only.
    bit<2> flow_report_flag; // Egress only.
    bit<1> queue_report_flag; // Egress only.
}

header switch_dtel_switch_local_mirror_metadata_h {
    switch_pkt_src_t src;
    switch_mirror_type_t type;
    bit<48> timestamp;
#if __TARGET_TOFINO__ == 1
    bit<6> _pad;
#endif
    switch_mirror_session_t session_id;
    bit<32> hash;
    bit<4> _pad1;
    switch_dtel_report_type_t report_type;
    bit<7> _pad2;
    bit<9> ingress_port;
    bit<7> _pad3;
    bit<9> egress_port;
#if __TARGET_TOFINO__ == 1
    bit<3> _pad4;
#else
    bit<1> _pad4;
#endif
    switch_qid_t qid;
    bit<5> _pad5;
    bit<19> qdepth;
    bit<32> egress_timestamp;
}

header switch_dtel_drop_mirror_metadata_h {
    switch_pkt_src_t src;
    switch_mirror_type_t type;
    bit<48> timestamp;
#if __TARGET_TOFINO__ == 1
    bit<6> _pad;
#endif
    switch_mirror_session_t session_id;
    bit<32> hash;
    bit<4> _pad1;
    switch_dtel_report_type_t report_type;
    bit<7> _pad2;
    bit<9> ingress_port;
    bit<7> _pad3;
    bit<9> egress_port;
#if __TARGET_TOFINO__ == 1
    bit<3> _pad4;
#else
    bit<1> _pad4;
#endif
    switch_qid_t qid;
    switch_drop_reason_t drop_reason;
}

// Used for truncate_only mirror sessions
header switch_simple_mirror_metadata_h {
    switch_pkt_src_t src;
    switch_mirror_type_t type;
#if __TARGET_TOFINO__ == 1
    bit<6> _pad;
#endif
    switch_mirror_session_t session_id;
}

@flexible
struct switch_bridged_metadata_dtel_extension_t {
    switch_dtel_report_type_t report_type;
    switch_mirror_session_t session_id;
    bit<32> hash;
    bit<9> egress_port;
}

//-----------------------------------------------------------------------------
// Other Metadata Definitions
//-----------------------------------------------------------------------------
// Flags
//XXX Force the fields that are XORd to NOT share containers.
// @pa_container_size("ingress", "ig_md.checks.same_if", 16)
struct switch_ingress_flags_t {
    bool ipv4_checksum_err;
    bool inner_ipv4_checksum_err;
    bool link_local;
    bool routed;
    bool acl_deny;
    bool racl_deny;
    bool port_vlan_miss;
    bool rmac_hit;
    bool dmac_miss;
    bool myip;
    bool glean;
    bool storm_control_drop;
    bool acl_meter_drop;
    bool port_meter_drop;
    bool flood_to_multicast_routers;
    bool peer_link;
    bool capture_ts;
    bool mac_pkt_class;
    bool pfc_wd_drop;
    // Add more flags here.
}

struct switch_egress_flags_t {
    bool routed;
    bool acl_deny;
    bool mlag_member;
    bool peer_link;
    bool capture_ts;
    bool wred_drop;
    bool port_meter_drop;
    bool acl_meter_drop;
    bool pfc_wd_drop;

    // Add more flags here.
}


// Checks
struct switch_ingress_checks_t {
    switch_port_lag_index_t same_if;
    bool mrpf;
    bool urpf;
    // Add more checks here.
}

struct switch_egress_checks_t {
    switch_bd_t same_bd;
    switch_mtu_t mtu;
    bool stp;

    // Add more checks here.
}

// IP
struct switch_ip_metadata_t {
    bool unicast_enable;
    bool multicast_enable;
    bool multicast_snooping;
    // switch_urpf_mode_t urpf_mode;
}

// struct switch_lookup_fields_t {
//     switch_pkt_type_t pkt_type;
//
//     mac_addr_t mac_src_addr;
//     mac_addr_t mac_dst_addr;
//     bit<16> mac_type;
//     bit<3> pcp;
//
//     // 1 for ARP request, 2 for ARP reply.
//     bit<16> arp_opcode;
//
//     switch_ip_type_t ip_type;
//     bit<8> ip_proto;
//     bit<8> ip_ttl;
//     bit<8> ip_tos;
//     bit<2> ip_frag;
//     bit<128> ip_src_addr;
//     bit<128> ip_dst_addr;
//
//     bit<8> tcp_flags;
//     bit<16> l4_src_port;
//     bit<16> l4_dst_port;
// }

// Header types used by ingress/egress deparsers.
@flexible
struct switch_bridged_metadata_t {
    // user-defined metadata carried over from ingress to egress.
    switch_port_t ingress_port;
    switch_port_lag_index_t ingress_port_lag_index;
    switch_bd_t ingress_bd;
    switch_nexthop_t nexthop;
    switch_pkt_type_t pkt_type;
    bool routed;
    //TODO(msharif) : Fix the bridged metadata fields for PTP.
#if defined(PTP_ENABLE)
    bool capture_ts;
#endif
#ifdef MLAG_ENABLE
    bool peer_link;
#endif
    switch_cpu_reason_t cpu_reason;
    bit<48> timestamp;
    switch_tc_t tc;
    switch_qid_t qid;
    switch_pkt_color_t color;

    // Add more fields here.
}

@flexible
struct switch_bridged_metadata_acl_extension_t {
#if defined(EGRESS_IP_ACL_ENABLE) || defined(EGRESS_MIRROR_ACL_ENABLE)
    bit<16> l4_src_port;
    bit<16> l4_dst_port;
    bit<8> tcp_flags;
    switch_l4_port_label_t l4_src_port_label;
    switch_l4_port_label_t l4_dst_port_label;
#ifdef ACL_USER_META_ENABLE
    switch_user_metadata_t user_metadata;
#endif
#else
    bit<8> tcp_flags;
#endif
}

@flexible
struct switch_bridged_metadata_tunnel_extension_t {
    switch_tunnel_index_t index;
    switch_outer_nexthop_t outer_nexthop;
    bit<16> hash;
    switch_vrf_t vrf;
    bool terminate;
}

#ifdef DTEL_ENABLE
@pa_atomic("ingress", "hdr.bridged_md.base_qid")
@pa_container_size("ingress", "hdr.bridged_md.base_qid", 8)
@pa_container_size("ingress", "hdr.bridged_md.dtel_report_type", 8)
@pa_no_overlay("ingress", "hdr.bridged_md.base_qid")
@pa_no_overlay("ingress", "hdr.bridged_md.__pad_2")
@pa_no_overlay("ingress", "hdr.bridged_md.__pad_3")
@pa_no_overlay("ingress", "hdr.bridged_md.__pad_4")
@pa_no_overlay("ingress", "hdr.bridged_md.__pad_5")
@pa_no_overlay("egress", "hdr.dtel_report.ingress_port")
@pa_no_overlay("egress", "hdr.dtel_report.egress_port")
@pa_no_overlay("egress", "hdr.dtel_report.queue_id")
@pa_no_overlay("egress", "hdr.dtel_drop_report.drop_reason")
@pa_no_overlay("egress", "hdr.dtel_drop_report.reserved")
#endif

typedef bit<8> switch_bridge_type_t;

header switch_bridged_metadata_h {
    switch_pkt_src_t src;
    switch_bridge_type_t type;
    switch_bridged_metadata_t base;
#if defined(EGRESS_IP_ACL_ENABLE) || defined(EGRESS_MIRROR_ACL_ENABLE) \
    || defined(DTEL_FLOW_REPORT_ENABLE)
    switch_bridged_metadata_acl_extension_t acl;
#endif
#ifdef TUNNEL_ENABLE
    switch_bridged_metadata_tunnel_extension_t tunnel;
#endif
#ifdef DTEL_ENABLE
    switch_bridged_metadata_dtel_extension_t dtel;
#endif
}

struct switch_port_metadata_t {
    switch_port_lag_index_t port_lag_index;
    switch_port_lag_label_t port_lag_label;
}

// @pa_container_size("ingress", "ig_md.mirror.src", 8)
// @pa_container_size("ingress", "ig_md.mirror.type", 8)
// @pa_container_size("ingress", "smac_src_move", 16)
// @pa_alias("ingress", "ig_md.egress_port", "ig_intr_md_for_tm.ucast_egress_port")
#if !defined(DTEL_DROP_REPORT_ENABLE) && !defined(DTEL_QUEUE_REPORT_ENABLE)
// @pa_alias("ingress", "ig_md.multicast.id", "ig_intr_md_for_tm.mcast_grp_b")
#endif
// @pa_alias("ingress", "ig_md.qos.qid", "ig_intr_md_for_tm.qid")
// @pa_alias("ingress", "ig_md.qos.icos", "ig_intr_md_for_tm.ingress_cos")
// @pa_alias("ingress", "ig_intr_md_for_dprsr.mirror_type", "ig_md.mirror.type")
// Ingress metadata
// struct switch_ingress_metadata_t {
//     switch_port_t port;                            /* ingress port */
//     switch_port_t egress_port;                     /* egress port */
//     switch_port_lag_index_t port_lag_index;        /* ingress port/lag index */
//     switch_port_lag_index_t egress_port_lag_index; /* egress port/lag index */
//     switch_bd_t bd;
//     switch_vrf_t vrf;
//     switch_nexthop_t nexthop;
//     switch_outer_nexthop_t outer_nexthop;
//     switch_nexthop_t acl_nexthop;
//     bool acl_port_redirect;
//     switch_nexthop_t unused_nexthop;
//
//     bit<48> timestamp;
//     bit<32> hash;
//
//     switch_ingress_flags_t flags;
//     switch_ingress_checks_t checks;
//     switch_ingress_bypass_t bypass;
//
//     switch_ip_metadata_t ipv4;
//     switch_ip_metadata_t ipv6;
//     switch_port_lag_label_t port_lag_label;
//     switch_bd_label_t bd_label;
//     switch_if_label_t if_label;
//     switch_l4_port_label_t l4_src_port_label;
//     switch_l4_port_label_t l4_dst_port_label;
//
//     switch_drop_reason_t drop_reason;
//     switch_cpu_reason_t cpu_reason;
//
//     switch_rmac_group_t rmac_group;
//     switch_lookup_fields_t lkp;
//     switch_multicast_metadata_t multicast;
//     switch_stp_metadata_t stp;
//     switch_qos_metadata_t qos;
//     switch_sflow_metadata_t sflow;
//     switch_tunnel_metadata_t tunnel;
//     switch_learning_metadata_t learning;
//     switch_mirror_metadata_t mirror;
//     switch_dtel_metadata_t dtel;
//
//     switch_user_metadata_t user_metadata;
// }

// Egress metadata
// @pa_container_size("egress", "eg_md.mirror.src", 8)
// @pa_container_size("egress", "eg_md.mirror.type", 8)
#ifdef DTEL_ENABLE
@pa_container_size("egress", "hdr.dtel_drop_report.drop_reason", 8)
@pa_mutually_exclusive("egress", "hdr.dtel.timestamp", "hdr.erspan_type3.timestamp")
#endif
// struct switch_egress_metadata_t {
//     switch_pkt_src_t pkt_src;
//     switch_pkt_length_t pkt_length;
//     switch_pkt_type_t pkt_type;
//
//     /* ingress port_lag_index for cpu going packets, egress port_lag_index for
//      * normal ports */
//     switch_port_lag_index_t port_lag_index;
//
//     switch_port_type_t port_type;               /* egress port type */
//     switch_port_t port;                         /* Mutable copy of egress port */
//     switch_port_t ingress_port;                 /* ingress port */
//     switch_bd_t bd;
//     switch_vrf_t vrf;
//     switch_nexthop_t nexthop;
//     switch_outer_nexthop_t outer_nexthop;
//
//     bit<32> timestamp;
//     bit<48> ingress_timestamp;
//
//     switch_egress_flags_t flags;
//     switch_egress_checks_t checks;
//     switch_egress_bypass_t bypass;
//
//     // for egress ACL
//     switch_port_lag_label_t port_lag_label;
//     switch_bd_label_t bd_label;
//     switch_if_label_t if_label;
//     switch_l4_port_label_t l4_src_port_label;
//     switch_l4_port_label_t l4_dst_port_label;
//
//     switch_lookup_fields_t lkp;
//     switch_qos_metadata_t qos;
//     switch_tunnel_metadata_t tunnel;
//     switch_mirror_metadata_t mirror;
//     switch_dtel_metadata_t dtel;
//     switch_sflow_metadata_t sflow;
//
//     switch_cpu_reason_t cpu_reason;
//     switch_drop_reason_t drop_reason;
//
// #ifdef ACL_USER_META_ENABLE
//     switch_user_metadata_t user_metadata;
// #endif
// }

// Header format for mirrored metadata fields
struct switch_mirror_metadata_h {
    switch_port_mirror_metadata_h port;
    switch_cpu_mirror_metadata_h cpu;
    switch_dtel_drop_mirror_metadata_h dtel_drop;
    switch_dtel_switch_local_mirror_metadata_h dtel_switch_local;
    switch_simple_mirror_metadata_h simple_mirror;
}

// struct switch_header_t {
//     switch_bridged_metadata_h bridged_md;
//     // switch_mirror_metadata_h mirror;
//     ethernet_h ethernet;
//     fabric_h fabric;
//     cpu_h cpu;
//     timestamp_h timestamp;
//     vlan_tag_h[VLAN_DEPTH] vlan_tag;
//     mpls_h[MPLS_DEPTH] mpls;
//     ipv4_h ipv4;
//     ipv4_option_h ipv4_option;
//     ipv6_h ipv6;
//     arp_h arp;
//     udp_h udp;
//     icmp_h icmp;
//     igmp_h igmp;
//     tcp_h tcp;
//     dtel_report_v05_h dtel;
//     dtel_report_base_h dtel_report;
//     dtel_switch_local_report_h dtel_switch_local_report;
//     dtel_drop_report_h dtel_drop_report;
//     rocev2_bth_h rocev2_bth;
//     vxlan_h vxlan;
//     gre_h gre;
//     nvgre_h nvgre;
//     geneve_h geneve;
//     erspan_h erspan;
//     erspan_type2_h erspan_type2;
//     erspan_type3_h erspan_type3;
//     erspan_platform_h erspan_platform;
//     ethernet_h inner_ethernet;
//     ipv4_h inner_ipv4;
//     ipv6_h inner_ipv6;
//     udp_h inner_udp;
//     tcp_h inner_tcp;
//     icmp_h inner_icmp;
// }

typedef bit<9> port_t;
typedef bit<32> qdepth_t;

struct egress_metadata_t {
    // TODO: set this somehow
    // bit<32> egress_timestamp;
    bit<16> data_checksum;
    // port_t egress_port;
    // qdepth_t deq_qdepth;
    bool is_mirrored;
    MirrorId_t mirror_sid;
}

#endif /* _P4_TYPES_ */
