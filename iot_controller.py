import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD


def send_iot_command(topic: str, payload: str):
    """Publish an MQTT message to control a smart device"""
    try:
        client = mqtt.Client()

        if MQTT_USERNAME:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=10)
        client.publish(topic, payload)
        client.disconnect()

        print(f"IoT: {topic} -> {payload}")

    except Exception as e:
        print(f"MQTT error: {e}")
