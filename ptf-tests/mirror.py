"""
Mirroring and Queue Occupancy reporting functionality
"""

from common import *

import time
import sys
import logging
import copy
import pdb
import datetime
# from scapy.all import *

import unittest
import random

import pd_base_tests

from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *

import os
from mirror_test.p4_pd_rpc.ttypes import *
from conn_mgr_pd_rpc.ttypes import *
from mirror_pd_rpc.ttypes import *
from mc_pd_rpc.ttypes import *
from devport_mgr_pd_rpc.ttypes import *
from res_pd_rpc.ttypes import *
from pal_rpc.ttypes import *
from ptf_port import *
import codecs

sys.path.append("/vagrant/src/postcard")
import postcard

try:
    from pltfm_pm_rpc.ttypes import *
except ImportError as e:
    pass

class TestGroup1(P4ProgramTest):
    def setUp(self):
        P4ProgramTest.setUp(self)

        self.programTable(self.forward_table, [
            ([("hdr.ethernet.dst_addr", "00:00:00:00:00:01")],
             "SwitchIngress.hit", [("port", 1)]),
            ([("hdr.ethernet.dst_addr", "00:00:00:00:00:02")],
             "SwitchIngress.hit", [("port", 2)])
        ])
        self.programTable(self.sender_ports_table, [
            ([("hdr.mirror.original_ingress_port", 1)],
             "SwitchEgress.wred.set_sender_packet", [])
        ])
        self.programTable(self.sender_action_table, [
            ([("exceeds_threshold", True)],
             "nop", []),
            ([("exceeds_threshold", False)],
             "nop", [])
        ])
        self.programTable(self.mirror_sid_table, [
            ([("hdr.mirror.original_ingress_port", 1)],
             "SwitchEgress.queue_mirrorer.set_mirror_sid", [("eg_ses",1)])
        ])

        self.queue_threshold_register.entry_add(
            self.dev_tgt,
            [self.queue_threshold_register.make_key([gc.KeyTuple('$REGISTER_INDEX', 1)])],
            [self.queue_threshold_register.make_data(
                [gc.DataTuple('SwitchEgress.wred.qdepth_threshold_cells.f1', 0)])])

        mirror_cfg_table = self.mirror_cfg_table

        self.ingress_port = 1
        self.egress_port = 2
        self.mirror_port = 3
        self.max_len = 85 # Size of ETHERNET+IPV4+UDP+QueueReport
        
        # Setup a session to mirror the packets out the ingress ports.
        # The original packets will be sent to a dummy port that drops them.
        for sid in self.sids:
            mirror_cfg_table.entry_add(
                self.dev_tgt,
                [mirror_cfg_table.make_key([gc.KeyTuple('$sid', sid)])],
                [mirror_cfg_table.make_data([gc.DataTuple('$direction', str_val="EGRESS"),
                                             gc.DataTuple('$ucast_egress_port', self.mirror_port),
                                             gc.DataTuple('$ucast_egress_port_valid', bool_val=True),
                                             gc.DataTuple('$session_enable', bool_val=True),
                                             gc.DataTuple('$max_pkt_len', self.max_len)],
                                            '$normal')]
            )
            logger.info("Using session %d for port %d", sid, self.mirror_port)

            # Verify mirror session config using entry get
            logger.info("Verifying entry get for session %d for port %d", sid, self.mirror_port)
            resp = mirror_cfg_table.entry_get(
                self.dev_tgt,
                [mirror_cfg_table.make_key([gc.KeyTuple('$sid', sid)])],
                {"from_hw": True},
                mirror_cfg_table.make_data([gc.DataTuple('$direction'),
                                            gc.DataTuple('$ucast_egress_port'),
                                            gc.DataTuple('$ucast_egress_port_valid'),
                                            gc.DataTuple('$max_pkt_len')],
                                           '$normal')
            )
            data_dict = next(resp)[0].to_dict()

            self.assertEqual(
                data_dict["$direction"], "EGRESS",
                "$direction should be EGRESS in entry get for session %d and port %d"%(sid, self.mirror_port)
            )
            self.assertEqual(
                data_dict["$ucast_egress_port"], self.mirror_port,
                "Verified $ucast_egress_port in entry get for session %d for port %d"%(sid, self.mirror_port)
            )
            self.assertEqual(
                data_dict["$ucast_egress_port_valid"], True,
                "Verified $ucast_egress_port_valid in entry get for session %d for port %d"%(sid, self.mirror_port)
            )
            self.assertEqual(
                data_dict["$max_pkt_len"], self.max_len,
                "Verified $max_pkt_len in entry get for session %d for port %d"%(sid, self.mirror_port)
            )

class TestMirrorDisabled(TestGroup1):
    """
    Check if a packet is mirrored as configured
    """

    def runTest(self):
        # Disable mirroring
        # TODO: would be nice to have this in a python library and use it
        # from both here and tofino_ctl.
        self.check_mirroring_table.default_entry_set(
            self.dev_tgt,
            self.check_mirroring_table.make_data(
                [],
                "SwitchEgress.queue_mirrorer.disable_mirroring"
            )
        )
        
        # packet should be sent without being modified
        pkt = simple_tcp_packet(pktlen = 200,
                                eth_dst="00:00:00:00:00:02",
                                eth_src='00:00:00:00:00:01',
                                ip_src='192.168.0.1',
                                ip_dst='192.168.0.2',
                                tcp_flags='A')
        send_packet(self, self.ingress_port, pkt)
        expected = simple_tcp_packet(pktlen = 200,
                                     eth_dst="00:00:00:00:00:02",
                                     eth_src='00:00:00:00:00:01',
                                     ip_src='192.168.0.1',
                                     ip_dst='192.168.0.2',
                                     tcp_flags='A')
        verify_packet(self, expected, self.egress_port)
        logger.info("Verified forwarded packet for port %d", self.egress_port)

        verify_no_other_packets(self)
        logger.info("Verified no mirrored packet for port %d", self.mirror_port)

        
class TestMirrorEnabled(TestGroup1):
    """
    Check if a packet is mirrored as configured
    """

    def runTest(self):
        # Enable mirroring
        # TODO: would be nice to have this in a python library and use it
        # from both here and tofino_ctl.
        self.check_mirroring_table.default_entry_set(
            self.dev_tgt,
            self.check_mirroring_table.make_data(
                [],
                "SwitchEgress.queue_mirrorer.enable_mirroring"
            )
        )

        # packet should be sent without being modified
        pkt = simple_tcp_packet(pktlen = 200,
                                eth_dst="00:00:00:00:00:02",
                                eth_src='00:00:00:00:00:01',
                                ip_src='192.168.0.1',
                                ip_dst='192.168.0.2',
                                tcp_flags='A')
        send_packet(self, self.ingress_port, pkt)
        
        expected = simple_tcp_packet(pktlen = 200,
                                     eth_dst="00:00:00:00:00:02",
                                     eth_src='00:00:00:00:00:01',
                                     ip_src='192.168.0.1',
                                     ip_dst='192.168.0.2',
                                     tcp_flags='A')
        verify_packet(self, expected, self.egress_port)
        logger.info("Verified forwarded packet for port %d", self.egress_port)

        # TODO: this is brittle, would be better to parse the body we get
        # using whatever library we'll use for this irl and make sure it's
        # reasonable
        payload = [0x80, 0x04, 0x01, 0xC0, 0xA8, 0x00, 0x01, 0xC0, 0xA8, 0x00, 0x02, 0x04, 0xD2, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        payload = codecs.decode("".join(["%02x"%(x%256) for x in payload]), "hex")
        self.assertFalse(postcard.Postcard(payload).was_dropped)

        mirrored = simple_udp_packet(pktlen = self.max_len,
                                     eth_dst="00:00:00:00:00:01",
                                     eth_src='00:00:00:00:00:02',
                                     ip_src='192.168.0.2',
                                     ip_dst='192.168.0.1',
                                     udp_sport=4444,
                                     udp_dport=4444,
                                     with_udp_chksum=False,
                                     udp_payload=payload
        )
        verify_packet(self, mirrored, self.mirror_port)
        logger.info("Verified mirrored packet for port %d", self.mirror_port)

class TestDroppedPackets(TestGroup1):
    """
    If a packet is dropped in the egress, we should still generate a postcard
    """

    def runTest(self):
        # Enable mirroring
        # TODO: would be nice to have this in a python library and use it
        # from both here and tofino_ctl.
        self.check_mirroring_table.default_entry_set(
            self.dev_tgt,
            self.check_mirroring_table.make_data(
                [],
                "SwitchEgress.queue_mirrorer.enable_mirroring"
            )
        )

        # TODO: don't put stuff in here we have to clean up.
        self.clean_table(self.sender_action_table)
        self.programTable(self.sender_action_table, [
            ([("exceeds_threshold", True)],
             "drop", []),
            ([("exceeds_threshold", False)],
             "drop", [])
        ])

        # send a packet that will be dropped
        pkt = simple_tcp_packet(pktlen = 200,
                                eth_dst="00:00:00:00:00:02",
                                eth_src='00:00:00:00:00:01',
                                ip_src='192.168.0.1',
                                ip_dst='192.168.0.2',
                                tcp_flags='A')
        send_packet(self, self.ingress_port, pkt)
        
        # TODO: this is brittle, would be better to parse the body we get
        # using whatever library we'll use for this irl and make sure it's
        # reasonable
        payload = [0x90, 0x04, 0x01, 0xC0, 0xA8, 0x00, 0x01, 0xC0, 0xA8, 0x00, 0x02, 0x04, 0xD2, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        payload = codecs.decode("".join(["%02x"%(x%256) for x in payload]), "hex")
        self.assertTrue(postcard.Postcard(payload).was_dropped)

        mirrored = simple_udp_packet(pktlen = self.max_len,
                                     eth_dst="00:00:00:00:00:01",
                                     eth_src='00:00:00:00:00:02',
                                     ip_src='192.168.0.2',
                                     ip_dst='192.168.0.1',
                                     udp_sport=4444,
                                     udp_dport=4444,
                                     with_udp_chksum=False,
                                     udp_payload=payload
        )
        verify_packet(self, mirrored, self.mirror_port)
        logger.info("Verified mirrored packet for port %d", self.mirror_port)
        
        verify_no_other_packets(self)        
