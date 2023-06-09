#
# sensor.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import Adafruit_DHT

sensor = Adafruit_DHT.DHT11

DHT_PIN = 25

humi, temp = Adafruit_DHT.read_retry(sensor, DHT_PIN)

if humi is not None and temp is not None:
    print("Temp => {0:0.1f}°C, Humi => {1:0.1f}%".format(temp, humi))
else:
    print("ERROR!!")
