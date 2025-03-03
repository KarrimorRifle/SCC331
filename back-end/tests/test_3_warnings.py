import unittest
import paho.mqtt.client as mqtt
import json
import time
import os
import requests
import random
import string

class TestWarnings(unittest.TestCase):
    # MQTT configuration (using the same broker as in test_3_data.py)
    MQTT_BROKER = "mqtt.flespi.io"
    MQTT_PORT = 1883
    MQTT_TOKEN = os.getenv("mqtt_token")
    
    # Service endpoints – note these use container names as in test_3_data.py
    ACCOUNTS_URL = "http://account_registration:5001"
    LOGIN_URL = "http://account_login:5002"
    WARNINGS_URL = "http://warning_editor:5004"

    def setUp(self):
        # Register and log in an admin user using the admin bypass header.
        self.admin_session_cookie = self.register_and_login_admin()
        self.created_warnings = []  # Track created warnings for cleanup
        # Reset any MQTT received message storage.
        self.received_warning_message = None

    def tearDown(self):
        # Cleanup: delete any warnings created during tests.
        for warning_id in self.created_warnings:
            try:
                requests.delete(
                    f"{self.WARNINGS_URL}/warnings/{warning_id}",
                    cookies={"session_id": self.admin_session_cookie}
                )
            except Exception as e:
                print(f"Cleanup failed for warning {warning_id}: {e}")

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

    def publish_data(self, data, topic):
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.username_pw_set(self.MQTT_TOKEN, None)
        client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
        client.loop_start()
        payload = json.dumps(data)
        client.publish(topic, payload)
        time.sleep(1)  # Allow time for the message to be sent
        client.loop_stop()
        client.disconnect()

    def on_message(self, client, userdata, msg):
        self.received_warning_message = json.loads(msg.payload.decode())

    def subscribe_to_warning_topic(self, topic):
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.username_pw_set(self.MQTT_TOKEN, None)
        client.on_message = self.on_message
        client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
        client.subscribe(topic)
        client.loop_start()
        return client

    def create_valid_warning_rule(self, suffix=""):
        """
        Helper to create a valid warning rule with conditions and messages.
        The rule monitors room id "101" with temperature condition.
        """
        name = "ValidRule_" + self.random_string(5) + suffix
        # Create the rule
        create_response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json={"name": name, "test_only": True},
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(create_response.status_code, 201)
        warning_id = create_response.json()["id"]
        self.created_warnings.append(warning_id)  # Record created warning
        # Update the rule with conditions and messages for validity.
        payload = {
            "name": name,
            "conditions": [
                {
                    "roomID": "101",
                    "conditions": [
                        {"variable": "temperature", "lower_bound": 10, "upper_bound": 30}
                    ]
                }
            ],
            "messages": [
                {
                    "Authority": "everyone",
                    "Title": "Triggered Warning",
                    "Location": "101",
                    "Severity": "warning",
                    "Summary": "Room 101 temperature out of range!"
                }
            ]
        }
        update_response = requests.patch(
            f"{self.WARNINGS_URL}/warnings/{warning_id}",
            json=payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(update_response.status_code, 200)
        return warning_id

    # 1. Create Warning Success
    def test_01_create_warning_success(self):
        unique_name = "TestWarning_" + self.random_string(5)
        payload = {"name": unique_name, "test_only": True}
        response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json=payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(response.status_code, 201)
        json_resp = response.json()
        self.created_warnings.append(json_resp["id"])  # Record created warning
        self.assertIn("message", json_resp)
        self.assertIn("id", json_resp)
        self.assertEqual(json_resp["message"], "Successfully created rule")

    # 2. Create Warning Unauthorized (missing session cookie)
    def test_02_create_warning_unauthorized(self):
        unique_name = "UnauthorizedWarning_" + self.random_string(5)
        payload = {"name": unique_name, "test_only": True}
        response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json=payload  # No cookies provided
        )
        self.assertEqual(response.status_code, 401)

    # 3. Create Warning Invalid Data (missing required "name")
    def test_03_create_warning_invalid_data(self):
        payload = {}  # Missing "name"
        response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json=payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(response.status_code, 400)

    # 4. Get Warnings List
    def test_04_get_warnings(self):
        # Create a warning to ensure one exists.
        unique_name = "ListWarning_" + self.random_string(5)
        create_response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json={"name": unique_name, "test_only": True},
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(create_response.status_code, 201)
        warning_id = create_response.json()["id"]
        self.created_warnings.append(warning_id)  # Record created warning

        response = requests.get(
            f"{self.WARNINGS_URL}/warnings",
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        warnings_list = response.json()
        self.assertTrue(any(w.get("id") == warning_id for w in warnings_list))

    # 5. Get Warning Details
    def test_05_get_warning_details(self):
        unique_name = "DetailWarning_" + self.random_string(5)
        create_response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json={"name": unique_name, "test_only": True},
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(create_response.status_code, 201)
        warning_id = create_response.json()["id"]
        self.created_warnings.append(warning_id)  # Record created warning

        response = requests.get(
            f"{self.WARNINGS_URL}/warnings/{warning_id}",
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        warning_details = response.json()
        self.assertEqual(warning_details.get("name"), unique_name)
        self.assertEqual(warning_details.get("id"), warning_id)

    # 6. Update Warning
    def test_06_update_warning(self):
        unique_name = "UpdateWarning_" + self.random_string(5)
        create_response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json={"name": unique_name, "test_only": True},
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(create_response.status_code, 201)
        warning_id = create_response.json()["id"]
        self.created_warnings.append(warning_id)  # Record created warning

        new_name = "Updated_" + unique_name
        update_payload = {
            "name": new_name,
            "conditions": [
                {
                    "roomID": "101",
                    "conditions": [
                        {"variable": "temperature", "lower_bound": 10, "upper_bound": 30}
                    ]
                }
            ],
            "messages": [
                {
                    "Authority": "admin",
                    "Title": "Updated Warning",
                    "Location": "101",
                    "Severity": "warning",
                    "Summary": "Temperature out of range!"
                }
            ]
        }
        update_response = requests.patch(
            f"{self.WARNINGS_URL}/warnings/{warning_id}",
            json=update_payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(update_response.status_code, 200)
        # Fetch the updated warning to verify changes.
        get_response = requests.get(
            f"{self.WARNINGS_URL}/warnings/{warning_id}",
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(get_response.status_code, 200)
        warning_details = get_response.json()
        self.assertEqual(warning_details.get("name"), new_name)

    # 7. Delete Warning
    def test_07_delete_warning(self):
        unique_name = "DeleteWarning_" + self.random_string(5)
        create_response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json={"name": unique_name, "test_only": True},
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(create_response.status_code, 201)
        warning_id = create_response.json()["id"]
        self.created_warnings.append(warning_id)  # Record created warning

        delete_response = requests.delete(
            f"{self.WARNINGS_URL}/warnings/{warning_id}",
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(delete_response.status_code, 200)
        # Attempt to fetch the deleted warning; expecting a 404.
        get_response = requests.get(
            f"{self.WARNINGS_URL}/warnings/{warning_id}",
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(get_response.status_code, 404)

    # 8. Test Warning with Invalid ID
    def test_08_test_warning_invalid_id(self):
        payload = {"id": 999999, "mode": "full"}  # Likely an invalid id
        response = requests.post(
            f"{self.WARNINGS_URL}/warnings/test",
            json=payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(response.status_code, 400)

    # 9. Test Warning with Invalid Mode
    def test_09_test_warning_invalid_mode(self):
        unique_name = "ModeWarning_" + self.random_string(5)
        create_response = requests.post(
            f"{self.WARNINGS_URL}/warnings",
            json={"name": unique_name, "test_only": True},
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(create_response.status_code, 201)
        warning_id = create_response.json()["id"]
        self.created_warnings.append(warning_id)  # Record created warning

        payload = {"id": warning_id, "mode": "invalid_mode"}
        response = requests.post(
            f"{self.WARNINGS_URL}/warnings/test",
            json=payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(response.status_code, 400)

    # 10. Warning MQTT Publish and Receive (using valid rule & room data)
    def test_10_warning_mqtt_publish_and_receive(self):
        warning_id = self.create_valid_warning_rule("_MQTT")
        topic = f"test/warning/everyone/{warning_id}"
        client = self.subscribe_to_warning_topic(topic)
        # Publish room data to trigger the rule.
        # Room data with PicoType 1, RoomID 101, and a temperature of 35 (above the upper_bound 30)
        room_data = {
            "PicoID": 300,
            "RoomID": 101,
            "PicoType": 1,
            "Data": "12,50,25,20,1013,40"
        }
        self.publish_data(room_data, "feeds/hardware-data/test_room")
        # Wait a few seconds to allow the warning system to process the room data
        time.sleep(5)
        client.loop_stop()
        client.disconnect()
        self.assertIsNotNone(self.received_warning_message, "No warning message received via MQTT")
        self.assertEqual(self.received_warning_message.get("Title"), "Triggered Warning", "Warning Title mismatch")
        self.assertEqual(self.received_warning_message.get("Severity"), "warning", "Warning Severity mismatch")

    # 11. Acknowledge Warning Success (using valid rule)
    def test_11_acknowledge_warning_success(self):
        warning_id = self.create_valid_warning_rule("_Ack")
        ack_payload = {"response": "acknowledged"}
        ack_response = requests.post(
            f"{self.WARNINGS_URL}/warnings/{warning_id}/acknowledge",
            json=ack_payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(ack_response.status_code, 200)
        self.assertEqual(ack_response.json().get("message"), "Response sent")

    # 12. Acknowledge Warning Unauthorized (missing session cookie)
    def test_12_acknowledge_warning_unauthorized(self):
        warning_id = self.create_valid_warning_rule("_NoAuth")
        ack_payload = {"response": "acknowledged"}
        ack_response = requests.post(
            f"{self.WARNINGS_URL}/warnings/{warning_id}/acknowledge",
            json=ack_payload  # No cookies provided
        )
        self.assertEqual(ack_response.status_code, 401)

    # 13. Get Test Results for a Warning (with room data trigger and delay)
    def test_13_get_test_results(self):
        warning_id = self.create_valid_warning_rule("_Test")
        # Publish room data to trigger the rule (using same room id "101")
        room_data = {
            "PicoID": 400,
            "RoomID": 101,
            "PicoType": 1,
            "Data": "12,50,35,20,1013,40"  # Temperature 35 out of valid range
        }
        self.publish_data(room_data, "feeds/hardware-data/test_room")
        
        # Invoke the test endpoint to queue a test run for this rule.
        test_payload = {"id": warning_id, "mode": "messages"}
        test_response = requests.post(
            f"{self.WARNINGS_URL}/warnings/test",
            json=test_payload,
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(test_response.status_code, 200)
        test_id = test_response.json()["test_id"]

        # Wait 2 seconds before sending new MQTT message for environment data
        time.sleep(2)
        new_room_data = {
            "PicoID": 401,
            "RoomID": 101,
            "PicoType": 1,
            "Data": "15,55,25,22,1015,45"  # New environment data
        }
        self.publish_data(new_room_data, "feeds/hardware-data/test_room")

        # Wait 5 seconds to allow test results to be generated
        time.sleep(5)
        result_response = requests.get(
            f"{self.WARNINGS_URL}/warnings/test/result/{test_id}",
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(result_response.status_code, 200)
        result_json = result_response.json()
        self.assertEqual(result_json.get("result"), "messages_sent")

    # 14. Get Warning Logs (authorized)
    def test_14_get_logs(self):
        response = requests.get(
            f"{self.WARNINGS_URL}/warnings/logs",
            cookies={"session_id": self.admin_session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        logs = response.json()
        self.assertIsInstance(logs, list)

    # 15. Get Warning Logs Unauthorized (missing session cookie)
    def test_15_get_logs_unauthorized(self):
        response = requests.get(f"{self.WARNINGS_URL}/warnings/logs")
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
