import paho.mqtt.client as mqtt
import json
import time
from resources.logging_config import setup_logger

logger = setup_logger()

class ControllerMQTTClient:
    def __init__(self, broker_address="localhost"):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="controller")        
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()
        self.data_received = None
        self.data_ready = False
        self.client.subscribe("sensor_data")

    def on_message(self, client, userdata, message):
        self.data_received = json.loads(message.payload.decode("utf-8"))
        self.data_ready = True
        logger.info(f"Data received from sensor unit: {self.data_received}")

    def request_data(self, testing=False):
        self.data_ready = False
        request = "send_test_data" if testing else "send_data"
        self.client.publish("get_data", json.dumps({"request": request}))
        while not self.data_ready:
            time.sleep(0.1)
        return self.data_received
    
    def publish_data(self, data, topic):
        self.client.publish(topic, json.dumps(data))
        print(f"published {data} from controller to topic {topic}")

    def init_device_manager(self, init_data):
        self.client.publish("init_device_manager", json.dumps(init_data))

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()