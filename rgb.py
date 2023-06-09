#
# rgb.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import RPi.GPIO as GPIO
import time

RED = 17
GREEN = 27
BLUE = 22
colors = [0xFF0000, 0xFF0023, 0xFF00FF, 0x0000FF, 0x00FF00, 0x64EB00, 0x4BFB00]

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.output(RED, True)
GPIO.output(GREEN, True)
GPIO.output(BLUE, True)

pwm_red = GPIO.PWM(RED, 2000)
pwm_green = GPIO.PWM(GREEN, 2000)
pwm_blue = GPIO.PWM(BLUE, 2000)

pwm_red.start(0)
pwm_green.start(0)
pwm_blue.start(0)


def refactory(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def set_color(value):
    red_value = (value & 0x110000) >> 16
    green_value = (value & 0x001100) >> 8
    blue_value = (value & 0x000011) >> 0

    red_value = refactory(red_value, 0, 255, 0, 100)
    green_value = refactory(green_value, 0, 255, 0, 100)
    blue_value = refactory(blue_value, 0, 255, 0, 100)

    pwm_red.ChangeDutyCycle(100-red_value)
    pwm_green.ChangeDutyCycle(100 - green_value)
    pwm_blue.ChangeDutyCycle(100 - blue_value)


try:
    while True:
        for col in colors:
            set_color(col)
            time.sleep(1)
except KeyboardInterrupt:
    pwm_red.stop()
    pwm_green.stop()
    pwm_blue.stop()
    GPIO.output(RED, True)
    GPIO.output(GREEN, True)
    GPIO.output(BLUE, True)
    GPIO.cleanup()
