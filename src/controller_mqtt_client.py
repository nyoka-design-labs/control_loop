import paho.mqtt.client as mqtt
import json

class ControllerMQTTClient:
    def __init__(self, broker_address="localhost"):
        self.client = mqtt.Client("controller")
        self.client.on_message = self.on_message
        self.client.connect(broker_address, 1883, 60)
        self.client.loop_start()
        self.data_received = None

    def on_message(self, client, userdata, message):
        self.data_received = json.loads(message.payload.decode("utf-8"))
        print("Data received from sensor unit:", self.data_received)

    def request_data(self):
        self.client.subscribe("sensor_data")
        self.client.publish("get_data", json.dumps({"request": "send_data"}))

    def init_device_manager(self, init_data):
        self.client.publish("init_device_manager", json.dumps(init_data))

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()