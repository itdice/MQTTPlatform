#
# mqtt.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Connected => {str(rc)}")
    client.subscribe("test/test")


def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode('utf-8')}")


mqtt_client = mqtt.Client("raspi_pub")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.publish("test/test", "Hello from Server!!")
mqtt_client.loop_forever()

