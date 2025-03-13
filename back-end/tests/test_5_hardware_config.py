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

subscribed_mqtt_messages = []

def on_mqtt_message(client, user_data, message):
    global subscribed_mqtt_messages
    payload_str = message.payload.decode("utf-8", errors="ignore")
    subscribed_mqtt_messages.append(SubscriptionResponse(message.topic, json.loads(payload_str)))
        

class TestData(unittest.TestCase):
    MQTT_BROKER = "mqtt.flespi.io"
    MQTT_PORT = 1883
    MQTT_SERVER_TOPIC = "hardware_config/server_message/"
    MQTT_HARDWARE_TOPIC = "hardware_config/hardware_message/"
    MQTT_TOKEN = os.getenv("mqtt_token")  # Replace with your actual MQTT token
    HARDWARE_EDITING_URL = "http://hardware_editing:5006"
    ACCOUNTS_URL = "http://account_registration:5001"
    LOGIN_URL = "http://account_login:5002"
    UNASSIGNED_PICO = 0
    ENVIRONMENT_PICO = 1
    TRACKER_PICO = 2


    def setUp(self):
        self.session_cookie = self.register_and_login_admin()

    def random_string(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def register_and_login_admin(self):
        rand_str = self.random_string()
        email = f"admin_{rand_str}@fakecompany.co.uk"
        headers = {
            "name": "Admin " + rand_str,
            "email": email,
            "password": "adminpass",
            "bypass": "yes"  # Admin bypass header
        }
        reg_response = requests.post(
            f"{self.ACCOUNTS_URL}/register",
            headers=headers
        )
        self.assertEqual(reg_response.status_code, 201)
        login_response = requests.post(
            f"{self.LOGIN_URL}/login",
            headers={
                "email": email,
                "password": "adminpass"
            }
        )
        self.assertEqual(login_response.status_code, 200)
        return login_response.cookies.get("session_id")
            

    def set_up_mqtt_client(self):
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.on_message = on_mqtt_message
        client.username_pw_set(self.MQTT_TOKEN, None)
        client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
        client.loop_start()
        return client


    def end_mqtt_client(self, client):
        client.loop_stop()
        client.disconnect()


    def publish_data_to_mqtt(self, client, data, topic):
        payload = json.dumps(data)
        client.publish(topic, payload, qos=2)


    def fetch_device_summary_from_server(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.get(
                f"{self.HARDWARE_EDITING_URL}/get/device/configs",
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
                f"{self.HARDWARE_EDITING_URL}/patch/device/config/" + device_id,
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
            response = requests.post(
                f"{self.HARDWARE_EDITING_URL}/delete/device/config/" + device_id,
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to delete device from server after 5 attempts.")


    def fetch_tracking_groups_from_server(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.get(
                f"{self.HARDWARE_EDITING_URL}/get/tracking/groups",
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to fetch summary from server after 5 attempts.")


    def add_tracking_group_to_server(self, group_name):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.post(
                f"{self.HARDWARE_EDITING_URL}/add/tracking/group",
                cookies={"session_id": self.session_cookie},
                json={"groupName" : group_name}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to add group to server after 5 attempts.")


    def patch_tracking_group_in_server(self, group_id, new_group_name):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.patch(
                f"{self.HARDWARE_EDITING_URL}/patch/tracking/group/" + str(group_id),
                json={"groupName" : new_group_name},
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to patch group in server after 5 attempts.")


    def delete_tracking_group_from_server(self, group_id):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.post(
                f"{self.HARDWARE_EDITING_URL}/delete/tracking/group/" + str(group_id),
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to delete group from server after 5 attempts.")


    def test_01_populate_and_get_devices(self):
        pico_details = [
            { "picoID" : "Test1", "readablePicoID" : "Test1", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test2", "readablePicoID" : "Test2", "picoType" : 0, "trackingGroupID" : None}
        ]

        for pico in pico_details:
            self.delete_device_from_server(pico["picoID"])

        mqtt_client = self.set_up_mqtt_client()

        for pico in pico_details:
            mqtt_client.subscribe(self.MQTT_SERVER_TOPIC + pico["picoID"])
    
        # Publish 2 test devices
        for pico in pico_details:
            self.publish_data_to_mqtt(mqtt_client, {"PicoID" : pico["picoID"]}, self.MQTT_HARDWARE_TOPIC + pico["picoID"])

        time.sleep(2)

        max_attempts = 5
        for attempt in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == 2:
                break

        self.assertEqual(len(subscribed_mqtt_messages), 2, "Expected for 2 messages to be sent to hardware")
        
        for i in range(len(subscribed_mqtt_messages)):
            server_mqtt_message = subscribed_mqtt_messages.pop(0)
            found = False
            for pico in pico_details:
                if (server_mqtt_message.route == self.MQTT_SERVER_TOPIC + pico["picoID"]):
                    found = True
                    self.assertDictEqual(server_mqtt_message.message, {"ReadableID" :  pico["picoID"], "BluetoothID" : 0, "PicoType" : self.UNASSIGNED_PICO, "TrackerGroup" : ""}, "Unexpeceted message sent to hardware")
            self.assertEqual(found, True, "Expected for message topics to match descibed topics")

        server_data = self.fetch_device_summary_from_server()

        picos_found = []
        for pico in pico_details:
            found = False
            for i in range(len(server_data["configs"])):
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    found = True
                    picos_found.append(pico["picoID"])
                    self.assertDictEqual(server_data["configs"][i], pico, "unexpected response from /get/device/configs")
            self.assertEqual(found, True, "Expected for pico ID " + pico["picoID"] + " to be found in response from /get/device/configs")

        for pico in pico_details:
            self.delete_device_from_server(pico["picoID"])
        # add a tracking group

        server_data = self.fetch_device_summary_from_server()

        picos_found = []
        for pico in pico_details:
            for i in range(len(server_data["configs"])):
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    picos_found.append(pico["picoID"])
                    self.assertDictEqual(server_data["configs"][i], pico, "unexpected response from /get/device/configs")

        self.assertEqual(len(picos_found), 0, "The picos should have been removed from the server")

        self.end_mqtt_client(mqtt_client)
        

    def test_02_patch_devices(self):
        # Publish 3 test devices
        pico_details = [
            { "picoID" : "Test3", "readablePicoID" : "Test3", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test4", "readablePicoID" : "Test4", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test5", "readablePicoID" : "Test5", "picoType" : 0, "trackingGroupID" : None},
        ]

        for pico in pico_details:
            self.delete_device_from_server(pico["picoID"])

        mqtt_client = self.set_up_mqtt_client()

        for pico in pico_details:
            mqtt_client.subscribe(self.MQTT_SERVER_TOPIC + pico["picoID"])
    
        # Publish test devices
        for pico in pico_details:
            self.publish_data_to_mqtt(mqtt_client, {"PicoID" : pico["picoID"]}, self.MQTT_HARDWARE_TOPIC + pico["picoID"])

        max_attempts = 5
        for attempt in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == len(pico_details):
                break

        self.assertEqual(len(subscribed_mqtt_messages), len(pico_details), "Expected for " + str(len(pico_details)) + " messages to be sent to hardware")

        #discard messages as we arent testing them here
        for i in range(len(subscribed_mqtt_messages)):
            subscribed_mqtt_messages.pop(0)

        # # Patch the 3 test devices

        new_pico_details = [        # add a tracking group

            { "picoID" : "Test3", "readablePicoID" : "Test6", "picoType" : 0, "trackingGroupID" : None},
            { "picoID" : "Test4", "readablePicoID" : "Test7", "picoType" : 1, "trackingGroupID" : None},
            { "picoID" : "Test5", "readablePicoID" : "Test8", "picoType" : 2, "trackingGroupID" : None},
        ]
        
        self.patch_device_in_server(pico_details[0]["picoID"], {"readablePicoID" : "Test6"});
        self.patch_device_in_server(pico_details[1]["picoID"], {"readablePicoID" : "Test7", "picoType" : 1});
        self.patch_device_in_server(pico_details[2]["picoID"], {"readablePicoID" : "Test8", "picoType" : 2});

        # check the relevant mqtt messages are sent out
        max_attempts = 5
        for attempt in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == len(pico_details):
                break

        self.assertEqual(len(subscribed_mqtt_messages), len(pico_details), "Expected for 3 messages to be sent to hardware")

        for pico in new_pico_details:
            found = False
            for hardware_message in subscribed_mqtt_messages:
                if (hardware_message.route == self.MQTT_SERVER_TOPIC + pico["picoID"]):
                    found = True
                    if (pico["picoID"] == "Test3"):
                        self.assertDictEqual(hardware_message.message, {"ReadableID" : "Test6"}, "unexpected response from /get/device/configs after patch")

                    elif (pico["picoID"] == "Test4"):
                        btID = hardware_message.message.pop("BluetoothID", None)
                        self.assertNotEqual(btID, None, "Expected a bluetooth id to be supplied for test 4");
                        self.assertEqual(btID >= 1000, True, "Expected bluetooth id of test 4 to be below 1000")
                        self.assertDictEqual(hardware_message.message, {"ReadableID" : "Test7", "PicoType" : 1})

                    elif (pico["picoID"] == "Test5"):
                        btID = hardware_message.message.pop("BluetoothID", None)
                        self.assertNotEqual(btID, None, "Expected a bluetooth id to be supplied for test 5");
                        self.assertEqual(btID >= 1000, True, "Expected bluetooth id of test 5 to be at or above 1000")
                        self.assertDictEqual(hardware_message.message, {"ReadableID" : "Test8", "PicoType" : 2})

            self.assertEqual(found, True, "Expected for pico ID " + pico["picoID"] + " to be found in response from /get/device/configs after patch")

        for i in range(len(subscribed_mqtt_messages)):
            subscribed_mqtt_messages.pop()

        #check the server reflects the change
        server_data = self.fetch_device_summary_from_server()

        for pico in new_pico_details:
            found = False
            for i in range(len(server_data["configs"])):
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    found = True
                    self.assertDictEqual(server_data["configs"][i], pico, "unexpected response from /get/device/configs after patch")
            self.assertEqual(found, True, "Expected for pico ID to be found in response from /get/device/configs after patch")

        for pico in pico_details:
            self.delete_device_from_server(pico["picoID"])

        server_data = self.fetch_device_summary_from_server()

        picos_found = []
        for pico in pico_details:
            for i in range(len(server_data["configs"])):
                if (server_data["configs"][i]["picoID"] == pico["picoID"]):
                    picos_found.append(pico["picoID"])
                    self.assertDictEqual(server_data["configs"][i], pico, "unexpected response from /get/device/configs")

        self.assertEqual(len(picos_found), 0, "The picos should have been removed from the server")


    def test_03_add_and_get_tracking_groups(self):
        # add a tracking group
        server_add_response = self.add_tracking_group_to_server("TestGrp1")
        self.assertNotEqual(server_add_response["groupID"], None, "Expected an ID to be provided by the server")
        
        group_identifier = server_add_response["groupID"]

        # get the tracking groups list
        server_get_response = self.fetch_tracking_groups_from_server()

        # check the group has been added
        found = False
        for group in server_get_response["groups"]:
            if group["groupID"] == group_identifier: 
                found = True
                self.assertEqual(group["groupName"], "TestGrp1", "Name should match the name of the group of the id given by the server")
        
        self.assertEqual(found, True, "Group should be found in result from server")
        
        # add another

        second_server_add_response = self.add_tracking_group_to_server("TestGrp2")
        self.assertNotEqual(second_server_add_response["groupID"], None, "Expected an ID to be provided by the server")
        self.assertNotEqual(second_server_add_response["groupID"], group_identifier, "Expected ID to be unique")
        second_group_identifier = second_server_add_response["groupID"]

        # get the tracking groups list
        server_get_response = self.fetch_tracking_groups_from_server()

        # check the group has been added and that both are still listed
        firstFound = False
        secondFound = False
        for group in server_get_response["groups"]:
            if group["groupID"] == group_identifier: 
                firstFound = True
                self.assertEqual(group["groupName"], "TestGrp1", "Name should match the name of the group of the id given by the server")
            elif group["groupID"] == second_group_identifier:
                secondFound = True
                self.assertEqual(group["groupName"], "TestGrp2", "Name should match the name of the group of the id given by the server")

        self.assertEqual(firstFound and secondFound, True, "Expected both groups to be found")

        #delete both and check that neither is listed
        self.delete_tracking_group_from_server(group_identifier)
        self.delete_tracking_group_from_server(second_group_identifier)

        server_get_response = self.fetch_tracking_groups_from_server()

        firstFound = False
        secondFound = False
        for group in server_get_response["groups"]:
            if group["groupID"] == group_identifier: 
                firstFound = True
                self.assertEqual(group["groupName"], "TestGrp1", "Name should match the name of the group of the id given by the server")
            elif group["groupID"] == second_group_identifier:
                secondFound = True
                self.assertEqual(group["groupName"], "TestGrp2", "Name should match the name of the group of the id given by the server")

        self.assertEqual(firstFound or secondFound, False, "Expected neither group to be found")


    def test_04_add_device_to_tracking_group(self):
        # add a tracking group
        server_add_response = self.add_tracking_group_to_server("TestGrp1")
        self.assertNotEqual(server_add_response["groupID"], None, "Expected an ID to be provided by the server")
        
        group_identifier = server_add_response["groupID"]

        self.delete_device_from_server("Test1")
        
        # send a new device to the db
        pico_device = {"picoID" : "Test1", "readablePicoID" : "Test1", "picoType" : 0, "trackingGroupID" : None}

        mqtt_client = self.set_up_mqtt_client()

        mqtt_client.subscribe(self.MQTT_SERVER_TOPIC + pico_device["picoID"])

        self.publish_data_to_mqtt(mqtt_client, {"PicoID" : pico_device["picoID"]}, self.MQTT_HARDWARE_TOPIC + pico_device["picoID"])

        max_attempts = 5
        for attempt in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == 1:
                break

        subscribed_mqtt_messages.pop(0)

        # configure the new device to be a tracker with the new tracking group
        self.patch_device_in_server(pico_device["picoID"], {"readablePicoID" : "BTTest1", "picoType" : 2, "trackingGroupID" : group_identifier})
        
        max_attempts = 5
        for attempts in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == 1:
                break

        self.assertEqual(len(subscribed_mqtt_messages), 1, "Expected a response from the mqtt server")

        hardware_message = subscribed_mqtt_messages.pop(0)

        found = False
        if (hardware_message.route == self.MQTT_SERVER_TOPIC + pico_device["picoID"]):
            found = True
            btID = hardware_message.message.pop("BluetoothID", None)
            self.assertNotEqual(btID, None, "Expected a bluetooth id to be supplied for device");
            self.assertEqual(btID >= 1000, True, "Expected bluetooth id of test 5 to be at or above 1000")
            self.assertDictEqual(hardware_message.message, {"ReadableID" : "BTTest1", "PicoType" : 2, "TrackerGroup" : "TestGrp1"})
        self.assertEqual(found, True, "Expected for pico ID " + pico_device["picoID"] + " to be found in response from mqtt server after patch")


        # check that an appropriate response is sent to the device 

        self.end_mqtt_client(mqtt_client)

        self.delete_device_from_server(pico_device["picoID"])
        self.delete_tracking_group_from_server(group_identifier)


    def test_05_patch_tracking_group(self):
        # add a tracking group
        server_add_response = self.add_tracking_group_to_server("TestGrp1")
        self.assertNotEqual(server_add_response["groupID"], None, "Expected an ID to be provided by the server")
        
        group_identifier = server_add_response["groupID"]

        self.delete_device_from_server("Test1")
        
        # send a new device to the db
        pico_device = {"picoID" : "Test1", "readablePicoID" : "Test1", "picoType" : 0, "trackingGroupID" : None}

        mqtt_client = self.set_up_mqtt_client()

        mqtt_client.subscribe(self.MQTT_SERVER_TOPIC + pico_device["picoID"])

        self.publish_data_to_mqtt(mqtt_client, {"PicoID" : pico_device["picoID"]}, self.MQTT_HARDWARE_TOPIC + pico_device["picoID"])

        max_attempts = 5
        for attempt in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == 1:
                break

        subscribed_mqtt_messages.pop(0)

        # configure the new device to be a tracker with the new tracking group
        self.patch_device_in_server(pico_device["picoID"], {"readablePicoID" : "BTTest1", "picoType" : 2, "trackingGroupID" : group_identifier})
        
        max_attempts = 5
        for attempts in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == 1:
                break

        self.assertEqual(len(subscribed_mqtt_messages), 1, "Expected a response from the mqtt server")

        hardware_message = subscribed_mqtt_messages.pop(0)

        # change the tracking group name

        self.patch_tracking_group_in_server(group_identifier, "TestGrp2")

        # check the name has changed 

        # get the tracking groups list
        server_get_response = self.fetch_tracking_groups_from_server()

        # check the group has been added and that both are still listed
        found = False
        for group in server_get_response["groups"]:
            if group["groupID"] == group_identifier: 
                found = True
                self.assertEqual(group["groupName"], "TestGrp2", "Name should match the new name")
        self.assertEqual(found, True, "Expected to find group in server")

        # check the new device recieves an appropriate update from the server

        max_attempts = 5
        for attempts in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == 1:
                break

        self.assertEqual(len(subscribed_mqtt_messages), 1, "Expected a response from the mqtt server")

        hardware_message = subscribed_mqtt_messages.pop(0)

        found = False
        if (hardware_message.route == self.MQTT_SERVER_TOPIC + pico_device["picoID"]):
            found = True
            self.assertDictEqual(hardware_message.message, {"TrackerGroup" : "TestGrp2"})
        self.assertEqual(found, True, "Expected for pico ID " + pico_device["picoID"] + " to be found in response from mqtt server after patch")

        #delete tracking group
        self.delete_tracking_group_from_server(group_identifier)

        #ensure an appropriate message is sent to the hardware
        max_attempts = 5
        for attempts in range(max_attempts):
            time.sleep(2)
            if len(subscribed_mqtt_messages) == 1:
                break

        self.assertEqual(len(subscribed_mqtt_messages), 1, "Expected a response from the mqtt server")

        hardware_message = subscribed_mqtt_messages.pop(0)

        found = False
        if (hardware_message.route == self.MQTT_SERVER_TOPIC + pico_device["picoID"]):
            found = True
            self.assertDictEqual(hardware_message.message, {"TrackerGroup" : ""})
        self.assertEqual(found, True, "Expected for pico ID " + pico_device["picoID"] + " to be found in response from mqtt server after patch")

        self.delete_device_from_server(pico_device["picoID"])


if __name__ == '__main__':

    unittest.main()
