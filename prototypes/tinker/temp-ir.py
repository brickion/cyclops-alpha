#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
#UID = "64uer4"
UID = "Lr8"
# master: 64uer4
# ir: Lr8
offset = 10.2

from tinkerforge.ip_connection import IPConnection
# from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from time import sleep

if __name__ == "__main__":
  ipcon = IPConnection() # Create IP connection
  # master = BrickMaster(UID, ipcon) # Create device object
  tir = BrickletTemperatureIRV2(UID, ipcon)

  ipcon.connect(HOST, PORT) # Connect to brickd
  # Don't use device before ipcon is connected

  # Get current stack voltage
  #blah = master.get_stack_current() # get_stack_voltage()
  #print("Info: " + str(blah))
  ambient_temperature = tir.get_ambient_temperature()
  print("Ambient Temperature: " + str(ambient_temperature/10.0) + " °C")

  max_temp = tir.get_object_temperature()

  while True:
      object_temperature = tir.get_object_temperature()
      max_temp = max(max_temp, object_temperature)
      max_temp_offset = max_temp/10.0 + offset

      print(str(object_temperature/10.0) + " " + str(max_temp/10.0) + " " + str(max_temp_offset))

      sleep(0.1)

  ipcon.disconnect()
