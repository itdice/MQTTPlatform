#
# ultrasonic.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = 12
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
print("Ultrasonic Initialize")
time.sleep(2)

try:
    while True:
        GPIO.output(TRIG, True)
        print("Triggered")
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            print("echo start")
            start = time.time()

        while GPIO.input(ECHO) == 1:
            print("echo end")
            stop = time.time()

        check_time = stop - start
        distance = check_time * 34300 / 2
        print("Distance : %.1f cm" % distance)
        time.sleep(0.4)

except KeyboardInterrupt:
    print("Exit")
    GPIO.cleanup()
