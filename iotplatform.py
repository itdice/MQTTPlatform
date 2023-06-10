#
# iotplatform.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import Adafruit_DHT
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import subprocess
import time


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print(f"==============================")
    print(f"MQTT Connected[{str(rc)}]")
    client.subscribe("iot/door")
    client.subscribe("iot/fan")
    client.subscribe("iot/screen")
    print(f"==============================")


def on_message(client: mqtt.Client, userdata, msg):
    print(f"==============================")
    topic_data: str = msg.topic
    payload_data = msg.payload.decode('utf-8')
    print(f"MQTT Data Received [{topic_data}] {payload_data}")

    if topic_data == "iot/door":
        if payload_data == "open":
            pass  # Todo Door Open
        elif payload_data == "close":
            pass  # Todo Door Close
    elif topic_data == "iot/fan":
        if payload_data == "on":
            pass  # Todo Fan ON
        elif payload_data == "off":
            pass  # Todo Fan OFF
    elif topic_data == "iot/screen":
        pass  # Todo OLED Screen Customize

    print(f"==============================")


def nfc_read() -> str:
    print(f"==============================")
    print(f"NFC READ Start!!")

    with subprocess.Popen(["nfc-poll"], stdout=subprocess.PIPE) as process:
        nfc_raw_data: str = process.stdout.read().decode("utf-8")  # Read NFC Data
        nfc_uid: str = nfc_raw_data[nfc_raw_data.find('UID') + 14:nfc_raw_data.find('UID') + 28]  # Get UID Data
        nfc_uid_clear: str = nfc_uid.replace(" ", "")  # Remove Space

    print(f"NFC READ Result => {nfc_uid_clear}")
    print(f"==============================")
    return nfc_uid_clear


def ultrasonic_setup():
    print(f"==============================")
    print(f"Ultrasonic Sensor Setup")
    TRIG = 23
    ECHO = 24

    GPIO.setup(TRIG, GPIO.OUT)  # Trigger Pin Setup
    GPIO.setup(ECHO, GPIO.IN)  # Echo Pin Setup
    GPIO.output(TRIG, False)  # Trigger Initialize

    print("Ultrasonic Sensor Initialize")
    time.sleep(1)
    print(f"==============================")


def ultrasonic_read(_range: float) -> bool:
    TRIG = 23
    ECHO = 24
    start: float = 0.0
    stop: float = 0.0

    GPIO.output(TRIG, True)  # Trigger Pulse 10us
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        stop = time.time()

    check_time: float = stop - start
    distance: float = check_time * 34300 / 2
    result: bool = True if (distance < _range) else False

    return result


def rgb_setup():
    print(f"==============================")
    print(f"RGB LED Setup")
    RED = 17
    GREEN = 27
    BLUE = 22

    GPIO.setup(RED, GPIO.OUT)  # RED Pin Setup
    GPIO.setup(GREEN, GPIO.OUT)  # GREEN Pin Setup
    GPIO.setup(BLUE, GPIO.OUT)  # BLUE Pin Setup
    GPIO.output(RED, True)  # RED Pin Initialize
    GPIO.output(GREEN, True)  # GREEN Pin Initialize
    GPIO.output(BLUE, True)  # BLUE Pin Initialize

    print("RGB LED Initialize")
    time.sleep(1)
    print(f"==============================")


def rgb_write(red: bool, green: bool, blue: bool):
    RED = 17
    GREEN = 27
    BLUE = 22

    GPIO.output(RED, not red)
    GPIO.output(GREEN, not green)
    GPIO.output(BLUE, not blue)


def fan_setup():
    print(f"==============================")
    print(f"Fan Setup")
    INA = 9
    INB = 10

    GPIO.setup(INA, GPIO.OUT)  # Direction A Pin Setup
    GPIO.setup(INB, GPIO.OUT)  # Direction B Pin Setup
    GPIO.output(INA, False)  # Direction A Pin Initialize
    GPIO.output(INB, False)  # Direction B Pin Initialize

    print("Fan Initialize")
    time.sleep(1)
    print(f"==============================")


def fan_write(control: bool, direction: bool):
    INA = 9
    INB = 10

    if direction:
        GPIO.output(INA, control)
        GPIO.output(INB, False)
    else:
        GPIO.output(INA, False)
        GPIO.output(INB, control)


def sensor_read():
    print(f"==============================")
    print(f"Sensor Data Read")
    DHT_PIN = 25

    sensor = Adafruit_DHT.DHT11
    humi, temp = Adafruit_DHT.read_retry(sensor, DHT_PIN)
    print("Temp => {0:0.1f}°C, Humi => {1:0.1f}%".format(temp, humi))

    discomfort = discomfort_index(humi, temp)
    data: dict = {"temperature": temp, "humidity": humi, "discomfort_index": discomfort}
    mqtt_client.publish("iot/data", data)

    if discomfort >= 80:
        pass  # Todo Extreme
    elif 75 <= discomfort < 80:
        pass  # Todo High
    elif 68 <= discomfort < 75:
        pass  # Todo Moderate
    elif discomfort < 68:
        pass  # Todo Good

    print(f"==============================")


def discomfort_index(humi: float, temp: float) -> int:
    result: float = (9 / 5) * temp - (0.55 * (1 - (humi / 100))) * ((9 / 5) * temp - 26) + 32
    return int(result)


if __name__ == '__main__':
    # initial GPIO Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # MQTT Setup
    mqtt_client = mqtt.Client("raspi_pub")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)

    # OLED Setup
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=24)
    disp.begin()
    width = disp.width
    height = disp.height
    disp.clear()
    disp.display()

    # OLED Initial
    font = ImageFont.truetype('SamsungOne/SamsungOneKorean-700.ttf', 14)
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.text((10, 7), '현재 습도가 높습니다', font=font, fill=255)
    disp.image(image)
    disp.display()
