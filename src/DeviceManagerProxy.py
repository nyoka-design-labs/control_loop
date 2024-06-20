# device_manager_proxy.py
import paho.mqtt.client as mqtt
import json
import threading
import time

class DeviceManagerProxy:
    def __init__(self, mqtt_broker_ip):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(mqtt_broker_ip, 1883, 60)
        self.client.subscribe("sensor_unit/response")
        self.client.loop_start()
        self.response = None
        self.lock = threading.Lock()
    def on_message(self, client, userdata, message):
        self.lock.acquire()
        try:
            self.response = json.loads(message.payload.decode())
        finally:
            self.lock.release()

    def call_remote_method(self, method, params=None):
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": 1
        }
        self.client.publish("sensor_unit/request", json.dumps(request))
        self.wait_for_response()
        return self.response

    def wait_for_response(self):
        start_time = time.time()
        while self.response is None and (time.time() - start_time) < 5:  # Wait for 5 seconds
            time.sleep(0.1)
        if self.response is None:
            raise TimeoutError("No response from sensor unit")
        response = self.response
        self.response = None
        return response

    def get_measurement(self):
        return self.call_remote_method("get_measurement")

    def test_get_measurement(self, test_name):
        return self.call_remote_method("test_get_measurement", [test_name])
