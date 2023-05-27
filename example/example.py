#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from time import sleep
from serial import Serial

from awd10.client import Client
from awd10.device import AWD10

logging.basicConfig(level=logging.INFO)


transport = Serial(port="COM5", timeout=0.1)
awd = Client(transport=transport, device=AWD10, unit=5)
print(awd)

print("Move: {}".format(awd.move(speed=100)))
sleep(5)
print("Move: {}".format(awd.move(speed=0)))

# print("Get Address: {}".format(awd.get_param("Address")))
# print("Set Address: {}".format(awd.set_param("Address", 5)))
# print("Echo: {}".format(awd.echo()))
# print("State: {}".format(awd.state()))
# print("Result: {}".format(awd.result("Status")))
# print("Stop: {}".format(awd.stop()))
# print("Reset: {}".format(awd.reset()))
