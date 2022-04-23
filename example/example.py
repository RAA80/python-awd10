#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from time import sleep
from serial import Serial

from awd10.client import Client
from awd10.device import AWD10

logging.basicConfig(level=logging.INFO)


transport = Serial(port="COM5", timeout=0.1)
id_awd = Client(transport=transport, device=AWD10, unit=5)

print (id_awd)

print ("Get Address: {}".format(id_awd.getParam("Address")))
#print ("Set Address: {}".format(id_awd.setParam("Address", 5)))
print ("Echo: {}".format(id_awd.echo()))
print ("State: {}".format(id_awd.state()))
print ("Move: {}".format(id_awd.move(speed=100)))

sleep(5)

print ("Move: {}".format(id_awd.move(speed=0)))
print ("Result: {}".format(id_awd.result("Status")))

#print ("Stop: {}".format(id_awd.stop()))
#print ("Reset: {}".format(id_awd.reset()))
