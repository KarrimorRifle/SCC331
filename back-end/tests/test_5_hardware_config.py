import unittest
import paho.mqtt.client as mqtt
import json
import time
import os
import requests
import random
import string
from datetime import datetime, timedelta

class SubscriptionResponse:
    def __init__(self, route, message):
        self.route = route
        self.message = message


class TestData(unittest.TestCase):
    MQTT_BROKER = "mqtt.flespi.io"
    MQTT_PORT = 1883
    MQTT_SERVER_TOPIC = "hardware_config/server_message/"
    MQTT_HARDWARE_TOPIC = "hardware_config/hardware_message/"
    MQTT_TOKEN = os.getenv("mqtt_token")  # Replace with your actual MQTT token
    HARDWARE_EDITING_URL = "http://hardware_editing:5006"
    UNASSIGNED_PICO = 0
    ENVIRONMENT_PICO = 1
    TRACKER_PICO = 2


    def setUp(self):
        self.email = self.generate_random_email()
        self.session_cookie = self.register_and_login()
        self.subscribed_mqtt_messages = []


    def generate_random_email(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"{random_string}@fakecompany.co.uk"


    def register_and_login(self):
        # Register a new user
        register_response = requests.post(
            f"{self.ACCOUNTS_URL}/register",
            headers={
                "name": "Test User",
                "email": self.email,
                "password": "password123"
            }
        )
        self.assertEqual(register_response.status_code, 201)

        # Login with the new user
        login_response = requests.post(
            f"{self.LOGIN_URL}/login",
            headers={
                "email": self.email,
                "password": "password123"
            }
        )
        self.assertEqual(login_response.status_code, 200)
        return login_response.cookies.get("session_id")
            

    def set_up_mqtt_client(self):
        def on_mqtt_message(client, user_data, message):
            payload_str = message.payload.decode("utf-8", errors="ignore")

            self.subscribed_mqtt_messages.append(SubscriptionResponse(message.topic, json.loads(payload_str)))
        
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.on_message = on_mqtt_message
        client.username_pw_set(self.MQTT_TOKEN, None)
        client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
        client.loop_start()
        return client


    def end_mqtt_client(self, client):
        client.loop_stop()
        client.disconnect()


    def publish_data(self, client, data, topic):
        for item in data:
            payload = json.dumps(item)
            client.publish(topic, payload)
            time.sleep(1)  # Sleep to ensure messages are sent


    def fetch_device_summary_from_server(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.get(
                f"{self.READER_URL}/get/device/configs",
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to fetch summary from server after 5 attempts.")


    def patch_device_in_server(self, device_id, new_details):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.patch(
                f"{self.READER_URL}/patch/device/config/" + device_id,
                json=new_details,
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to patch device in server after 5 attempts.")


    def delete_device_from_server(self, device_id):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.get(
                f"{self.READER_URL}/delete/device/config/" + device_id,
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to delete device from server after 5 attempts.")


    def test_01_populate_and_get_devices(self):
        pico_details = [
            { "picoID" : "Test1", "readablePicoID" : "Test1", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test2", "readablePicoID" : "Test2", "picoType" : 0, "trackingGroupID" : None}
        ]

        mqtt_client = self.set_up_mqtt_client()

        for pico in pico_details:
            mqtt_client.subscribe(self.MQTT_SERVER_TOPIC + pico["picoID"])
    
        # Publish 2 test devices
        for pico in pico_details:
            self.publish_data(mqtt_client, {"PicoID" : pico["picoID"]}, self.MQTT_HARDWARE_TOPIC)

        max_attempts = 5
        for attempt in range(max_attempts):
            if len(self.subscribed_mqtt_messages) == 2:
                break
            time.sleep(2)

        self.assertEqual(len(self.subscribed_mqtt_messages), 2, "Expected for 2 messages to be sent to hardware")
        
        for i in range(len(self.subscribed_mqtt_messages)):
            server_mqtt_message = self.subscribed_mqtt_messages.pop()
            found = False
            for pico in pico_details:
                if (server_mqtt_message.route == self.MQTT_SERVER_TOPIC + pico["picoID"]):
                    found = True
                    self.assertEqual(server_mqtt_message.message, json.dumps({"ReadableID" :  pico["picoID"], "BluetoothID" : 0, "PicoType" : self.UNASSIGNED_PICO, "TrackerGroup" : ""}), "Unexpeceted message sent to hardware")
            self.assertEqual(found, True, "Expected for message topics to match descibed topics")

        server_http_response = self.fetch_device_summary_from_server()
        self.assertEqual(server_http_response.status_code, 200, "Expected 200 OK from /get/device/configs")
        server_data = server_http_response.json()

        self.assertEqual(len(server_data["configs"]), 2, "Expected 2 configs in response from /get/device/configs")

        picos_found = []
        for i in range(len(server_data["configs"])):
            found = False
            for pico in pico_details:
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    found = True
                    picos_found.append(pico["picoID"])
                    self.assertDictEqual(server_data["configs"][i], pico, "unexpected response from /get/device/configs")
            self.assertEqual(found, True, "Expected for pico ID to be found in response from /get/device/configs")
        
        for pico in pico_details:
            self.assertEqual(pico["picoID"] in picos_found, True, "Expected both picos to be represented in /get/device/configs")

        for pico in pico_details:
            self.delete_device_from_server(pico["picoID"])

        self.end_mqtt_client(mqtt_client)
        

    def test_02_patch_devices(self):
        print("TODO")
        # Publish 3 test devices
        pico_details = [
            { "picoID" : "Test3", "readablePicoID" : "Test3", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test4", "readablePicoID" : "Test4", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test5", "readablePicoID" : "Test5", "picoType" : 0, "trackingGroupID" : None},
        ]

        mqtt_client = self.set_up_mqtt_client()

        for pico in pico_details:
            mqtt_client.subscribe(self.MQTT_SERVER_TOPIC + pico["picoID"])

        for pico in pico_details:
            self.publish_data(mqtt_client, {"PicoID" : pico["picoID"]}, self.MQTT_HARDWARE_TOPIC)


        max_attempts = 5
        for attempt in range(max_attempts):
            if len(self.subscribed_mqtt_messages) == len(pico_details):
                break
            time.sleep(2)

        self.assertEqual(len(self.subscribed_mqtt_messages), len(pico_details), "Expected for 3 messages to be sent to hardware")

        #discard messages as we arent testing them here
        for i in range(self.subscribed_mqtt_messages):
            self.subscribed_mqtt_messages[i].pop()

        # Patch the 3 test devices

        new_pico_details = [
            { "picoID" : "Test3", "readablePicoID" : "Test6", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test4", "readablePicoID" : "Test7", "picoType" : 1, "trackingGroupID" : None},
            { "picoID" : "Test5", "readablePicoID" : "Test8", "picoType" : 2, "trackingGroupID" : 0},
        ]
        
        self.patch_device_in_server(pico_details[0], {"readablePicoID" : "Test6"});
        self.patch_device_in_server(pico_details[1], {"readablePicoID" : "Test7", "picoType" : 1});
        self.patch_device_in_server(pico_details[2], {"readablePicoID" : "Test8", "picoType" : 2});

        # check the relevant mqtt messages are sent out
        max_attempts = 5
        for attempt in range(max_attempts):
            if len(self.subscribed_mqtt_messages) == len(pico_details):
                break
            time.sleep(2)

        self.assertEqual(len(self.subscribed_mqtt_messages), len(pico_details), "Expected for 3 messages to be sent to hardware")

        for i in range(len(self.subscribed_mqtt_messages)):
            hardware_message = self.subscribed_mqtt_messages.pop()
            for pico in new_pico_details:
                if (hardware_message.route == self.MQTT_SERVER_TOPIC + pico["picoID"]):
                    found = True
                    if (pico["picoID"] == "Test3"):
                        self.assertDictEqual(hardware_message.message, {"ReadableID" : "Test6"}, "unexpected response from /get/device/configs after patch")

                    elif (pico["picoID"] == "Test4"):
                        btID = server_data["configs"][i].pop("BluetoothID", None)
                        self.assertNotEqual(btID, None, "Expected a bluetooth id to be supplied for test 4");
                        self.assertDictEqual(hardware_message, {"ReadableID" : "Test7", "PicoType" : 1})

                    elif (pico["picoID"] == "Test5"):
                        btID = server_data["configs"][i].pop("BluetoothID", None)
                        self.assertNotEqual(btID, None, "Expected a bluetooth id to be supplied for test 5");
                        self.assertDictEqual(hardware_message, {"ReadableID" : "Test8", "PicoType" : 2})

            self.assertEqual(found, True, "Expected for pico ID to be found in response from /get/device/configs after patch")


        #check the server reflects the change
        server_http_response = self.fetch_device_summary_from_server()
        self.assertEqual(server_http_response.status_code, 200, "Expected 200 OK from /get/device/configs after patch")
        server_data = server_http_response.json()
        
        for i in range(len(server_data["configs"])):
            found = False
            for pico in new_pico_details:
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    found = True
                    self.assertDictEqual(server_data["configs"][i], pico, "unexpected response from /get/device/configs after patch")
            self.assertEqual(found, True, "Expected for pico ID to be found in response from /get/device/configs after patch")


    def test_03_delete_devices(self):
        print("TODO")
        # Publish 2 test devices
        pico_details = [
            { "picoID" : "Test9", "readablePicoID" : "Test3", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test10", "readablePicoID" : "Test4", "picoType" : 0, "trackingGroupID" : None},
        ]

        mqtt_client = self.set_up_mqtt_client()

        for pico in pico_details:
            self.publish_data(mqtt_client, {"PicoID" : pico["picoID"]}, self.MQTT_HARDWARE_TOPIC)

        # check the 2 test devices are inside the database
        server_http_response = self.fetch_device_summary_from_server()
        self.assertEqual(server_http_response.status_code, 200, "Expected 200 OK from /get/device/configs")
        server_data = server_http_response.json()

        self.assertEqual(len(server_data["configs"]), 2, "Expected 2 configs in response from /get/device/configs")

        picos_found = []
        for i in range(len(server_data["configs"])):
            found = False
            for pico in pico_details:
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    found = True
                    picos_found.append(pico["picoID"])
                    self.assertEqual(json.dumps(server_data["configs"][i]), json.dumps(pico), "unexpected response from /get/device/configs")
            self.assertEqual(found, True, "Expected for pico ID to be found in response from /get/device/configs")
        
        for pico in pico_details:
            self.assertEqual(pico["picoID"] in picos_found, True, "Expected both picos to be represented in /get/device/configs")

        #delete the first device
        self.delete_device_from_server(pico_details[0]["picoID"])

        # check that only the second test device is still inside the database
        server_http_response = self.fetch_device_summary_from_server()
        self.assertEqual(server_http_response.status_code, 200, "Expected 200 OK from /get/device/configs")
        server_data = server_http_response.json()

        self.assertEqual(len(server_data["configs"]), 1, "Expected 1 config in response from /get/device/configs")

        picos_found = []
        for i in range(len(server_data["configs"])):
            found = False
            for pico in pico_details:
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    found = True
                    picos_found.append(pico["picoID"])
                    self.assertEqual(json.dumps(server_data["configs"][i]), json.dumps(pico), "unexpected response from /get/device/configs")
            self.assertEqual(found, True, "Expected for pico ID to be found in response from /get/device/configs")
        
        self.assertEqual(pico_details[0]["picoID"] in picos_found, False, "Expected both picos to be represented in /get/device/configs")
        self.assertEqual(pico_details[1]["picoID"] in picos_found, True, "Expected both picos to be represented in /get/device/configs")

        # delete the second device
        self.delete_device_from_server(pico_details[1]["picoID"])

        server_http_response = self.fetch_device_summary_from_server()
        self.assertEqual(server_http_response.status_code, 200, "Expected 200 OK from /get/device/configs")
        server_data = server_http_response.json()

        self.assertEqual(len(server_data["configs"]), 0, "Expected 0 configs in response from /get/device/configs")


    def test_04_add_and_get_tracking_groups(self):
        # add a tracking group

        # get the tracking groups list

        # check the group has been added

        # add another

        # check both are listed
        print("TODO")


    def test_05_patch_tracking_group(self):
        print("TODO")
        # add 2 tracking groups

        #patch the first

        #check that the first and only the first has been altered


    def test_06_delete_tracking_groups(self):
        print("TODO")
        # Publish 2 test groups

        # check the 2 test groups are inside the database

        # delete the first group

        # check the second test group is still inside the database

        # delete the second group

        # check the database is empty


if __name__ == '__main__':

    unittest.main()
