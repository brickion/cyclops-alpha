#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
#UID = "64uer4"
UID = "Mfb"
UIDTemp = "Lr8"
# master: 64uer4
# ir: Lr8
offset = 14.2

def calculate_temp(distance, temp):
  lower_distance = 21.6
  lower_temp = 20.5
  linear_dimish = (22.4-lower_temp)/(59.6-lower_distance)
  return round((distance - lower_distance) * linear_dimish + temp,2)

from tinkerforge.ip_connection import IPConnection
# from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_distance_ir_v2 import BrickletDistanceIRV2
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from time import sleep

if __name__ == "__main__":
  ipcon = IPConnection() # Create IP connection
  dir = BrickletDistanceIRV2(UID, ipcon)
  tir = BrickletTemperatureIRV2(UIDTemp, ipcon)

  ipcon.connect(HOST, PORT) # Connect to brickd




  while True:
      distance = dir.get_distance()
      temperature = tir.get_object_temperature()
      ambient_temp = tir.get_ambient_temperature()

      # print(str(distance/10.0) + " cm | " + str(temperature/10.0) + ' °C | ' + str(round(distance/(temperature),2)))

      # top 60 = 20
      # bottom 10 = 24.3
      # (24.3-20) / (60-10) = every cm = 0.086c increase
      distance_offset_temp = calculate_temp(distance/10.0, temperature/10.0)
      #print(str(distance/10.0) + " cm | " + str(temperature/10.0) + ' °C | ' + str(distance_offset_temp) + ' | ' + str(distance_offset_temp + offset) )
      print(str(ambient_temp))
      sleep(0.2)

  ipcon.disconnect()
