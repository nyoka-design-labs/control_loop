import paho.mqtt.client as mqtt
import json
from DeviceManager_mqtt import DeviceManager
import time

class DeviceManagerMQTTClient:
    def __init__(self, broker_address):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor_unit")        
        self.client.on_message = self.on_message
        self.client.connect(broker_address, 1883, 60)
        self.client.subscribe("init_device_manager")
        self.client.subscribe("get_data")
        self.client.loop_start()
        self.dm = None

    def on_message(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        if message.topic == "init_device_manager":
            print(payload)
            self.dm = self.init_device_manager(payload)
            
        elif message.topic == "get_data":
            if payload.get("request") == "send_data":
                data = self.dm.get_measurement()
            elif payload.get("request") == "send_test_data":
                data = self.dm.test_get_measurement()
            self.publish_data(data)

    def init_device_manager(self, config):
        loop_id = config["loop_id"]
        control_id = config["control_id"]
        data_types = config["data_types"]
        loop_devices = config["loop_devices"]
        csv_name = config["csv_name"]
        test_name = config.get("test_name", "")
        devices = config.get("devices", True)

        # Check if a DeviceManager with the same specifications already exists
        if self.dm and self.dm.loop_id == loop_id and self.dm.control_id == control_id and \
        self.dm.data_types == data_types + ["time", "date", "time_of_day", "type"] and \
        self.dm.devices == devices:
            # Update fields that can be overwritten
            self.dm.csv_name = csv_name
            self.dm.test_name = test_name
            return self.dm

        # Create a new DeviceManager if not existing
        self.dm = DeviceManager(loop_id, control_id, data_types, loop_devices, csv_name, test_name, devices)
        return self.dm

    def publish_data(self, data):
        self.client.publish("sensor_data", json.dumps(data))

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    broker_address = "192.168.0.25"  # Replace with your MQTT broker address
    mqtt_client = DeviceManagerMQTTClient(broker_address)
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        mqtt_client.stop()