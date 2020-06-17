#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
#UID = "64uer4"
UID = "Mfb"
# master: 64uer4
# ir: Lr8
offset = 10.2

from tinkerforge.ip_connection import IPConnection
# from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_distance_ir_v2 import BrickletDistanceIRV2
from time import sleep

if __name__ == "__main__":
  ipcon = IPConnection() # Create IP connection
  # master = BrickMaster(UID, ipcon) # Create device object
  dir = BrickletDistanceIRV2(UID, ipcon)

  ipcon.connect(HOST, PORT) # Connect to brickd
  # Don't use device before ipcon is connected

  # Get current stack voltage
  #blah = master.get_stack_current() # get_stack_voltage()
  #print("Info: " + str(blah))
  distance = dir.get_distance()
  print("Distance: " + str(distance/10.0) + " cm")

  while True:
      distance = dir.get_distance()
      print("Distance: " + str(distance/10.0) + " cm")

      sleep(0.1)

  ipcon.disconnect()
