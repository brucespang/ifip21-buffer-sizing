"""
The most basic marking functionality
"""

from common import *
import pdb

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
             "SwitchEgress.wred.set_ipv4_ecn", []),
            ([("exceeds_threshold", False)],
             "SwitchEgress.wred.nop", [])
        ])

class TestECNEnabled(TestGroup1):
    """
    Marking should happen when ECN is enabled for the ingress port
    """
    def runTest(self):
        self.queue_threshold_register.entry_add(
            self.dev_tgt,
            [self.queue_threshold_register.make_key([gc.KeyTuple('$REGISTER_INDEX', 1)])],
            [self.queue_threshold_register.make_data(
                [gc.DataTuple('SwitchEgress.wred.qdepth_threshold_cells.f1', 0)])])

        # Test Parameters
        ingress_port = 1
        egress_port  = 2

        # packet should be sent with ECN bits modified
        print("Testing ECN marking when packet is compatible...")
        pkt = simple_tcp_packet(eth_dst="00:00:00:00:00:02",
                                eth_src='00:00:00:00:00:01',
                                tcp_flags='A',
                                ip_ecn=1)
        expected = simple_tcp_packet(eth_dst="00:00:00:00:00:02",
                                     eth_src='00:00:00:00:00:01',
                                     tcp_flags='A',
                                     ip_ecn=3)
        send_packet(self, ingress_port, pkt)
        verify_packet(self, expected, egress_port)

        # packet should not be sent with ECN bits modified
        print("Testing ECN marking when ECN is not enabled on packet...")
        pkt = simple_tcp_packet(eth_dst="00:00:00:00:00:02",
                                eth_src='00:00:00:00:00:01',
                                tcp_flags='A',
                                ip_ecn=0)
        expected = simple_tcp_packet(eth_dst="00:00:00:00:00:02",
                                     eth_src='00:00:00:00:00:01',
                                     tcp_flags='A',
                                     ip_ecn=0)
        send_packet(self, ingress_port, pkt)
        verify_packet(self, expected, egress_port)
