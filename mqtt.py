#
# mqtt.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client("raspi_pub")
mqtt_client.connect("192.168.0.86", 1833)

send_data = {"type": "test", "data": 10.123, "door": True}
mqtt_client.publish("test/test",send_data)
