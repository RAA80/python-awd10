#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from serial import Serial
from awd10.client import Client
from awd10.device import AWD10


class AWD(Client):
    def __init__(self, transport, device, unit):
        super(AWD, self).__init__(transport, device, unit)

    def _bus_exchange(self, packet):
        return {b'\x10<\x05\x00\x00\x00\x00\xaf': b'\x10<\x05\x00\x01\xf40\x8a',        # get result "Speed"
                b'\x10<\x04\x00\x00\x00\x00\xb0': b'\x10<\x04\x00\x00\x10\x10\x91',     # get result "Status" with crc error
                b'\x10K\x0b\x00\x00\x00\x00\x9a': b'\x10K\x0b\x00\x00\x00\x00\x9a',     # test enrot
                b'\x10K\n\x00\x00\x00\x00\x9b': b'\x10K\n\x00\x00\x00\x00\x9b',         # test stop
                b'\x10\xf0\x00\x00\x00\x00\x00\x00': b'\x10\xf0AWD\x00\x10\x14',        # test echo
                b'\x10K\t\x00\x00\x00\x00\x9c': b'\x10K\t\x00\x00\x00\x00\x9c',         # test reset
                b'\x10\x87\x1c\x00\x00\x00\x00M': b'\x10\x87\x1c\x00N\x00\x10\xef',     # test state
                b'\x10K\x08\x00\x01\xf4\x00\xa8': b'\x10K\x08\x00\x01\xf4\x00\xa8',     # test move speed 500
                b'\x10K\x08\x00\x00\x00\x00\x9d': b'\x10\xc3\x08\x00\x00\x00\x00\x25',  # test move speed 0 with errorcode C3
                b'\x10K\x08\x00\x00\x01\x00\x9c': b'',                                  # test move speed 1 with no answer
                b'\x10x\x00\x00\x00\n\x00n': b'\x10x\x00\x00\x00\n\x00n',               # test set_param
                b'\x10\x87\x00\x00\x00\x00\x00i': b'\x10\x87\x00\x00\x00\x10\x10I'      # test get_param
               }[bytes(packet)]


class TestAWDClient(unittest.TestCase):
    def setUp(self):
        self.client = AWD(transport=Serial(port=None), device=AWD10, unit=16)

    def tearDown(self):
        del self.client

    def test_make_packet(self):
        self.assertEqual(b'\x10K\x08\x00\x01\xf4\x00\xa8', self.client._make_packet(command=75, param=8, data=500))

    def test_get_param(self):
        self.assertEqual(16, self.client.get_param(name="Address"))

    def test_set_param(self):
        self.assertTrue(self.client.set_param(name="Address", value=10))
        self.assertRaises(ValueError, lambda: self.client.set_param(name="Address", value=500))

    def test_move(self):
        self.assertTrue(self.client.move(speed=500))
        self.assertIsNone(self.client.move(speed=0))
        self.assertIsNone(self.client.move(speed=1))

    def test_state(self):
        self.assertEqual({'FB': False, 'SkipLim': True, 'LimDrop': False, 'StopDrop': False, 'IntrfEN': True,
                          'IntrfVal': True, 'IntrfDir': True, 'SrcParam': False, 'SkipCV': False, 'Mode': 0,
                          'StOverCur': False, 'StMaxPWM': False, 'StDirFrwRev': False, 'StMotAct': True,
                          'StInRev': False, 'StInFrw': False, 'StLimRev': False, 'StLimFrw': False},
                         self.client.state())

    def test_reset(self):
        self.assertTrue(self.client.reset())

    def test_echo(self):
        self.assertTrue(self.client.echo())

    def test_stop(self):
        self.assertTrue(self.client.stop())

    def test_enrot(self):
        self.assertTrue(self.client.enrot())

    def test_result(self):
        self.assertEqual(500, self.client.result(name="Speed"))
        self.assertIsNone(self.client.result(name="Status"))


if __name__ == "__main__":
    unittest.main()
