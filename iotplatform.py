#
# iotplatform.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/07.
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

DOOR: bool = False
FAN: bool = False
CUR_DOOR: bool = False
CUR_FAN: bool = False
FIX_FAN: bool = False
SCREEN: str = "반갑습니다"
HUMI_HIGH: bool = False
TEMP_HIGH: bool = False


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

    global DOOR, FIX_FAN, SCREEN

    if topic_data == "iot/door":
        if payload_data == "open":
            DOOR = True
        elif payload_data == "close":
            DOOR = False
    elif topic_data == "iot/fan":
        if payload_data == "on":
            FIX_FAN = True
        elif payload_data == "off":
            FIX_FAN = False
    elif topic_data == "iot/screen":
        SCREEN = payload_data

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
    TRIG = 12
    ECHO = 24

    GPIO.setup(TRIG, GPIO.OUT)  # Trigger Pin Setup
    GPIO.setup(ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Echo Pin Setup
    GPIO.output(TRIG, False)  # Trigger Initialize

    print("Ultrasonic Sensor Initialize")
    time.sleep(1)
    print(f"==============================")


def ultrasonic_read(_range: float) -> bool:
    TRIG = 12
    ECHO = 24

    GPIO.output(TRIG, True)  # Trigger Pulse 10us
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        start = time.time()

    while GPIO.input(ECHO) == 1:
        stop = time.time()

    check_time: float = stop - start
    distance: float = check_time * 34300 / 2
    print("Distance : %.1f cm" % distance)
    time.sleep(0.4)

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


def sensor_read(mqtt_client: mqtt.Client):
    print(f"==============================")
    print(f"Sensor Data Read")
    DHT_PIN = 25

    global HUMI_HIGH, TEMP_HIGH

    sensor = Adafruit_DHT.DHT11
    humi, temp = Adafruit_DHT.read_retry(sensor, DHT_PIN)
    print("Temp => {0:0.1f}°C, Humi => {1:0.1f}%".format(temp, humi))

    discomfort = discomfort_index(humi, temp)
    data: dict = {"temperature": temp, "humidity": humi, "discomfort_index": discomfort}
    mqtt_client.publish("iot/data", str(data))

    if discomfort >= 80:
        rgb_write(True, False, False)  # RED
    elif 75 <= discomfort < 80:
        rgb_write(True, True, False)  # YELLOW
    elif 68 <= discomfort < 75:
        rgb_write(False, True, False)  # GREEN
    elif discomfort < 68:
        rgb_write(False, True, True)  # CYAN

    if humi >= 65.0:
        HUMI_HIGH = True
    else:
        HUMI_HIGH = False

    if temp >= 30.0:
        TEMP_HIGH = True
    else:
        TEMP_HIGH = False

    print(f"==============================")


def discomfort_index(humi: float, temp: float) -> int:
    result: float = (9 / 5) * temp - (0.55 * (1 - (humi / 100))) * ((9 / 5) * temp - 26) + 32
    return int(result)


if __name__ == '__main__':
    # initial GPIO Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    rgb_setup()
    fan_setup()

    # MQTT Setup
    mqtt_client = mqtt.Client("raspi_pub")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_forever()

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
    draw.text((5, 5), 'Welcome To', font=font, fill=255)
    draw.text((5, 25), 'IT DICE IoT', font=font, fill=255)
    draw.text((5, 45), 'Platform', font=font, fill=255)
    disp.image(image)
    disp.display()

    # Loop Section
    try:
        while True:
            # Sensor Part
            sensor_read(mqtt_client)

            if HUMI_HIGH and TEMP_HIGH and not FAN:
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), '현재 습도가 높습니다', font=font, fill=255)
                draw.text((5, 25), '현재 온도가 높습니다', font=font, fill=255)
                draw.text((5, 45), '선풍기를 작동합니다', font=font, fill=255)
                disp.image(image)
                disp.display()
                FAN = True
                time.sleep(1)
            elif HUMI_HIGH and not TEMP_HIGH and FAN:
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), '현재 습도가 높습니다', font=font, fill=255)
                draw.text((5, 25), '현재 온도가 낮습니다', font=font, fill=255)
                draw.text((5, 45), '선풍기를 중지합니다', font=font, fill=255)
                disp.image(image)
                disp.display()
                FAN = False
                time.sleep(1)
            elif not HUMI_HIGH and TEMP_HIGH and not FAN:
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), '현재 습도가 낮습니다', font=font, fill=255)
                draw.text((5, 25), '현재 온도가 높습니다', font=font, fill=255)
                draw.text((5, 45), '선풍기를 작동합니다', font=font, fill=255)
                disp.image(image)
                disp.display()
                FAN = True
                time.sleep(1)
            elif not HUMI_HIGH and not TEMP_HIGH and FAN:
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), '현재 습도가 낮습니다', font=font, fill=255)
                draw.text((5, 25), '현재 온도가 낮습니다', font=font, fill=255)
                draw.text((5, 45), '선풍기를 중지합니다', font=font, fill=255)
                disp.image(image)
                disp.display()
                FAN = False
                time.sleep(1)

            # Ultrasonic Part
            ultrasonic_setup()
            if ultrasonic_read(30.0):
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), SCREEN, font=font, fill=255)
                draw.text((5, 25), '==============', font=font, fill=255)
                draw.text((5, 45), 'NFC 입력 대기중...', font=font, fill=255)
                disp.image(image)
                disp.display()
                read_data: str = nfc_read()

                if read_data == "313cb0e0" and not DOOR:
                    image = Image.new('1', (width, height))
                    draw = ImageDraw.Draw(image)
                    draw.text((5, 5), "사용자님 반갑습니다.", font=font, fill=255)
                    draw.text((5, 25), '==============', font=font, fill=255)
                    draw.text((5, 45), '출입문이 열립니다..', font=font, fill=255)
                    disp.image(image)
                    disp.display()
                    DOOR = True
                    time.sleep(1)
                elif read_data == "313cb0e0" and DOOR:
                    image = Image.new('1', (width, height))
                    draw = ImageDraw.Draw(image)
                    draw.text((5, 5), "안녕히 가십시오.", font=font, fill=255)
                    draw.text((5, 25), '==============', font=font, fill=255)
                    draw.text((5, 45), '출입문이 닫힙니다.', font=font, fill=255)
                    disp.image(image)
                    disp.display()
                    DOOR = False
                    time.sleep(1)
                elif read_data != "313cb0e0":
                    image = Image.new('1', (width, height))
                    draw = ImageDraw.Draw(image)
                    draw.text((5, 5), "등록되지 않은 사용자", font=font, fill=255)
                    draw.text((5, 25), '==============', font=font, fill=255)
                    draw.text((5, 45), '다시 시도해 주세요.', font=font, fill=255)
                    disp.image(image)
                    disp.display()
                    time.sleep(1)

            # Door Part
            if DOOR and not CUR_DOOR:
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), "==============", font=font, fill=255)
                draw.text((5, 25), '출입문이 열렸습니다.', font=font, fill=255)
                draw.text((5, 45), '==============', font=font, fill=255)
                disp.image(image)
                disp.display()
                CUR_DOOR = True
                time.sleep(1)
            elif not DOOR and CUR_DOOR:
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), "==============", font=font, fill=255)
                draw.text((5, 25), '출입문이 닫혔습니다.', font=font, fill=255)
                draw.text((5, 45), '==============', font=font, fill=255)
                disp.image(image)
                disp.display()
                CUR_DOOR = False
                time.sleep(1)

            # Fan Part
            if (FAN and DOOR and not CUR_FAN) or (FIX_FAN and DOOR and not CUR_FAN):
                fan_write(True, True)
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), "==============", font=font, fill=255)
                draw.text((5, 25), '선풍기를 켭니다.', font=font, fill=255)
                draw.text((5, 45), '==============', font=font, fill=255)
                disp.image(image)
                disp.display()
                CUR_FAN = True
                time.sleep(1)
            elif (not FAN and CUR_FAN) or (not DOOR and CUR_FAN) or (not FIX_FAN and CUR_FAN):
                fan_write(False, True)
                image = Image.new('1', (width, height))
                draw = ImageDraw.Draw(image)
                draw.text((5, 5), "==============", font=font, fill=255)
                draw.text((5, 25), '선풍기를 끕니다.', font=font, fill=255)
                draw.text((5, 45), '==============', font=font, fill=255)
                disp.image(image)
                disp.display()
                CUR_FAN = False
                time.sleep(1)



    except KeyboardInterrupt:
        pass
    finally:
        pass
