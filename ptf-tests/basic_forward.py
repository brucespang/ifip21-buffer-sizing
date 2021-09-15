"""
Testing forwarding functionality across specific table setup
"""

# The common.py file in the same directory contains the foundational class,
# that is used for these individual tests

from common import *

########################################################################
########    Running Multiple Tests with the same setup   ###############
########################################################################

# This new Base Class extends the setup method of Simple L3 by adding the
# desired network setup
class TestGroup1(P4ProgramTest):
    def setUp(self):
        P4ProgramTest.setUp(self)

        self.programTable(self.forward_table, [
            ([("hdr.ethernet.dst_addr", "00:00:00:00:00:01")],
             "SwitchIngress.hit", [("port", 1)]),
            ([("hdr.ethernet.dst_addr", "00:00:00:00:00:02")],
             "SwitchIngress.hit", [("port", 2)])
        ])

#
# The following are multiple tests that all use the same setup
#
# There are a lot of tests that can be run on this topology. Feel free to
# add more
#

class Test1_1(TestGroup1):
    """
    Sending a packet to 00:00:00:00:00:01 into port 0. Expected on Port 1
    """
    def runTest(self):
        # Test Parameters
        ingress_port = 0
        egress_port  = 1

        pkt = simple_tcp_packet(eth_dst="00:00:00:00:00:01",
                                eth_src='00:55:55:55:55:55')
        send_packet(self, ingress_port, pkt)
        print("Expecting the packet to be forwarded to port %d" % egress_port)
        verify_packet(self, pkt, egress_port)
        print("Packet received of port %d" % egress_port)
        
class Test1_2(TestGroup1):
    """
    Sending a packet to 00:00:00:00:00:02 into port 1. Expected on Port 2
    """
    def runTest(self):
        # Test Parameters
        ingress_port = 1
        egress_port  = 2

        pkt = simple_tcp_packet(eth_dst="00:00:00:00:00:02",
                                eth_src='00:00:00:00:00:01')
        send_packet(self, ingress_port, pkt)
        print("Expecting the packet to be forwarded to port %d" % egress_port)
        verify_packet(self, pkt, egress_port)
        print("Packet received of port %d" % egress_port)
