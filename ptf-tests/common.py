"""
PTF foundational class for main.p4

This module contains the P4ProgramTest class specifically tailored for
main program (eventually this tailoring will go away).

All individual tests are subclassed from the this base (P4ProgramTest) or
its subclasses if necessary.

The easiest way to write a test is to start with a line

from common import *
"""

import time
import sys
import random

######### STANDARD MODULE IMPORTS ########
import unittest
import logging
import grpc
import pdb

######### PTF modules for BFRuntime Client Library APIs #######
import ptf
from ptf.testutils import *
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import bfrt_grpc.client as gc
import pdb

from ptf import config
from ptf.thriftutils import *

logger = logging.getLogger('Test')
if not len(logger.handlers):
    logger.addHandler(logging.StreamHandler())

########## Basic Initialization ############
class P4ProgramTest(BfRuntimeTest):
    # The setUp() method is used to prepare the test fixture. Typically
    # you would use it to establich connection to the gRPC Server
    #
    # You can also put the initial device configuration there. However,
    # if during this process an error is encountered, it will be considered
    # as a test error (meaning the test is incorrect),
    # rather than a test failure
    #
    # Here is the stuff we set up that is ready to use
    #  client_id
    #  p4_name
    #  bfrt_info
    #  dev
    #  dev_tgt
    #  allports
    #  tables    -- the list of tables
    #     Individual tables of the program with short names
    #     ipv4_host
    #     ipv4_lpm
    def setUp(self):
        self.client_id = 0
        self.p4_name = "main"     # Specialization
        self.dev      = 0
        self.dev_tgt  = gc.Target(self.dev, pipe_id=0xFFFF)

        print("\n")
        print("Test Setup")
        print("==========")

        BfRuntimeTest.setUp(self, self.client_id, self.p4_name)

        # This is the simple case when you run only one program on the target.
        # Otherwise, you might have to retrieve multiple bfrt_info objects and
        # in that case you will need to specify program name as a parameter
        self.bfrt_info = self.interface.bfrt_info_get()

        print("    Connected to Device: {}, Program: {}, ClientId: {}".format(
            self.dev, self.p4_name, self.client_id))

        # Create a list of all ports available on the device
        self.swports = []
        for (device, port, ifname) in ptf.config['interfaces']:
            self.swports.append(port)
        self.swports.sort()

        # Since this class is not a test per se, we can use the setup method
        # for common setup. For example, we can have our tables and annotations
        # ready

        # Program-specific customization
        self.forward_table = self.bfrt_info.table_get("pipe.SwitchIngress.forward")
        # pdb.set_trace()
        self.forward_table.info.key_field_annotation_add(
            "hdr.ethernet.dst_addr", "mac" )

        self.sender_ports_table = self.bfrt_info.table_get("pipe.SwitchEgress.wred.sender_ports")

        self.sender_action_table = self.bfrt_info.table_get("pipe.SwitchEgress.wred.sender_action")
        # self.nonsender_action_table = self.bfrt_info.table_get("pipe.SwitchEgress.wred.nonsender_action")

        self.mirror_sid_table = self.bfrt_info.table_get("pipe.SwitchEgress.queue_mirrorer.select_mirror_sid")
        self.check_mirroring_table = self.bfrt_info.table_get("pipe.SwitchEgress.queue_mirrorer.check_mirroring")

        self.queue_threshold_register = self.bfrt_info.table_get("pipe.SwitchEgress.wred.qdepth_threshold_cells")

        self.tables = [
            self.forward_table, self.sender_ports_table,
            self.sender_action_table, self.mirror_sid_table,
            self.check_mirroring_table
            # self.nonsender_action_table
        ]
        self.registers = [ self.queue_threshold_register  ]

        # Mirroring related state
        self.sids = [1]
        self.mirror_cfg_table = self.bfrt_info.table_get("$mirror.cfg")
        
        # Optional, but highly recommended
        self.cleanUp()

    # Use tearDown() method to return the DUT to the initial state by cleaning
    # all the configuration and clearing up the connection
    def tearDown(self):
        print("\n")
        print("Test TearDown:")
        print("==============")

        self.cleanUp()

        # Call the Parent tearDown
        BfRuntimeTest.tearDown(self)

    def clean_table(self, table):
        keys = []
        for (d, k) in table.entry_get(self.dev_tgt):
            if k is not None:
                keys.append(k)
        table.entry_del(self.dev_tgt, keys)
        return keys
        
    # Use Cleanup Method to clear the tables before and after the test starts
    # (the latter is done as a part of tearDown()
    def cleanUp(self):
        print("\n")
        print("Table Cleanup:")
        print("==============")

        try:
            for t in self.tables:
                print("  Clearing Table {}".format(t.info.name_get()))
                self.clean_table(t)

            for reg in self.registers:
                print("  Clearing Register {}".format(t.info.name_get()))
                keys = []
                for (d, k) in t.entry_get(self.dev_tgt):
                    if k is not None:
                        keys.append(k)

            # Delete all mirror sessions
            # import pdb
            # pdb.set_trace()
            for sid in self.sids:
                for _, k in self.mirror_cfg_table.entry_get(self.dev_tgt):
                    self.mirror_cfg_table.entry_del(self.dev_tgt, [k])

        except Exception as e:
            print("Error cleaning up: {}".format(e))

    #
    # This is a simple helper method that takes a list of entries and programs
    # them in a specified table
    #
    # Each entry is a tuple, consisting of 3 elements:
    #  key         -- a list of tuples for each element of the key
    #  action_name -- the action to use. Must use full name of the action
    #  data        -- a list (may be empty) of the tuples for each action
    #                 parameter
    #
    def programTable(self, table, entries, target=None):
        if target is None:
            target = self.dev_tgt

        key_list=[]
        data_list=[]
        for k, a, d in entries:
            key_list.append(table.make_key([gc.KeyTuple(*f)   for f in k]))
            data_list.append(table.make_data([gc.DataTuple(*p) for p in d], a))
        table.entry_add(target, key_list, data_list)

#
# Individual tests can now be subclassed from P4ProgramTest
#
