#
# fan.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import RPi.GPIO as GPIO
import time

INA = 9
INB = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(INA, GPIO.OUT)
GPIO.setup(INB, GPIO.OUT)
GPIO.output(INA, False)
GPIO.output(INB, False)

try:
    while True:
        GPIO.output(INA, True)
        time.sleep(2.0)
        GPIO.output(INA, False)
        time.sleep(0.5)

        GPIO.output(INB, True)
        time.sleep(2.0)
        GPIO.output(INB, False)
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.output(INA, False)
    GPIO.output(INB, False)
    GPIO.cleanup()
