import unittest
import paho.mqtt.client as mqtt
import json
import time
import os
import requests
import random
import string

class TestData(unittest.TestCase):
    MQTT_BROKER = "mqtt.flespi.io"
    MQTT_PORT = 1883
    MQTT_TOPIC = "feeds/hardware-data/test"
    MQTT_TOKEN = os.getenv("mqtt_token")  # Replace with your actual MQTT token
    ACCOUNTS_URL = "http://account_registration:5001"
    LOGIN_URL = "http://account_login:5002"
    READER_URL = "http://data_reader:5003"

    def setUp(self):
        self.luggage = [
            {"PicoID": 1, "RoomID": 1, "PicoType": 2, "Data": 1},
            {"PicoID": 2, "RoomID": 1, "PicoType": 2, "Data": 1},
            {"PicoID": 3, "RoomID": 1, "PicoType": 2, "Data": 1},
            {"PicoID": 4, "RoomID": 2, "PicoType": 2, "Data": 1},
            {"PicoID": 5, "RoomID": 2, "PicoType": 2, "Data": 1},
            {"PicoID": 6, "RoomID": 3, "PicoType": 2, "Data": 1},
            {"PicoID": 7, "RoomID": 3, "PicoType": 2, "Data": 1}
        ]
        self.users = [
            {"PicoID": 8, "RoomID": 1, "PicoType": 3, "Data": 1},
            {"PicoID": 9, "RoomID": 1, "PicoType": 3, "Data": 1},
            {"PicoID": 10, "RoomID": 2, "PicoType": 3, "Data": 1},
            {"PicoID": 11, "RoomID": 2, "PicoType": 3, "Data": 1},
            {"PicoID": 12, "RoomID": 2, "PicoType": 3, "Data": 1},
            {"PicoID": 13, "RoomID": 3, "PicoType": 3, "Data": 1},
            {"PicoID": 14, "RoomID": 3, "PicoType": 3, "Data": 1}
        ]
        self.room = [
            {"PicoID": 205, "RoomID": 1, "PicoType": 1, "Data": "10,12,34,11,20,20"},
            {"PicoID": 209, "RoomID": 2, "PicoType": 1, "Data": "21,30,12,23,15,12"},
            {"PicoID": 200, "RoomID": 3, "PicoType": 1, "Data": "13,17,9,53,23,63"}
        ]
        self.session = [
            {"PicoID": 59, "RoomID": 1, "PicoType": 2, "Data": 1},
            {"PicoID": 59, "RoomID": 2, "PicoType": 2, "Data": 1},
            {"PicoID": 59, "RoomID": 3, "PicoType": 2, "Data": 1},
            {"PicoID": 59, "RoomID": 2, "PicoType": 2, "Data": 1},
        ]
        self.session2 = [
            {"PicoID": 59, "RoomID": 3, "PicoType": 2, "Data": 1},
            {"PicoID": 59, "RoomID": 1, "PicoType": 2, "Data": 1},
            {"PicoID": 59, "RoomID": 2, "PicoType": 2, "Data": 1},
            {"PicoID": 59, "RoomID": 3, "PicoType": 2, "Data": 1},
        ]
        self.email = self.generate_random_email()
        self.session_cookie = self.register_and_login()

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

    def publish_data(self, data, topic):
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.username_pw_set(self.MQTT_TOKEN, None)
        client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
        client.loop_start()
        for item in data:
            payload = json.dumps(item)
            client.publish(topic, payload)
            time.sleep(1)  # Sleep to ensure messages are sent
        client.loop_stop()
        client.disconnect()

    def test_1_populate_and_check_rooms(self):
        # Publish luggage data
        self.publish_data(self.luggage, "feeds/hardware-data/test1_luggage")
        # Publish users data
        self.publish_data(self.users, "feeds/hardware-data/test1_users")
        # Publish room data
        self.publish_data(self.room, "feeds/hardware-data/test1_rooms")

        # Add assertions or checks here to verify the data was processed correctly
        expected_summary = {
            "1": {
                "users": {
                    "count": 2,
                    "id": [8, 9]
                },
                "luggage": {
                    "count": 3,
                    "id": [1, 2, 3]
                },
                "environment": {
                    "temperature": 10,
                    "sound": 12,
                    "light": 34,
                    "IAQ": 11,
                    "pressure": 20,
                    "humidity": 20
                }
            },
            "2": {
                "users": {
                    "count": 3,
                    "id": [10, 11, 12]
                },
                "luggage": {
                    "count": 2,
                    "id": [4, 5]
                },
                "environment": {
                    "temperature": 21,
                    "sound": 30,
                    "light": 12,
                    "IAQ": 23,
                    "pressure": 15,
                    "humidity": 12
                }
            },
            "3": {
                "users": {
                    "count": 2,
                    "id": [13, 14]
                },
                "luggage": {
                    "count": 1,
                    "id": [6]
                },
                "environment": {
                    "temperature": 13,
                    "sound": 17,
                    "light": 9,
                    "IAQ": 53,
                    "pressure": 23,
                    "humidity": 63
                }
            }
        }

        # Simulate fetching the summary from the server
        actual_summary = self.fetch_summary_from_server()

        self.assertEqual(expected_summary, actual_summary)

    def test_2_session_validation(self):
        # Publish session data
        for item in self.session:
            self.publish_data([item], "feeds/hardware-data/test2_sessions")
            time.sleep(2)  # Sleep to ensure messages are sent

        # Fetch the session logs for PicoID 1
        response = requests.get(
            f"{self.READER_URL}/pico/59",
            cookies={"session-id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)

        expected_logs = [
            {"roomID": 1},
            {"roomID": 2},
            {"roomID": 3},
            {"roomID": 2}
        ]

        actual_logs = response.json()
        actual_logs_simplified = [{"roomID": log["roomID"]} for log in actual_logs]
        self.assertEqual(expected_logs, actual_logs_simplified)

    def test_3_session_expiry_and_republish(self):
        # Wait for 2.5 minutes
        time.sleep(150)

        # Publish session2 data
        for item in self.session2:
            self.publish_data([item], "feeds/hardware-data/test3_sessions")
            time.sleep(2)  # Sleep to ensure messages are sent

        # Fetch the session logs for PicoID 59
        response = requests.get(
            f"{self.READER_URL}/pico/59",
            cookies={"session-id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)

        expected_logs = [
            {"roomID": 3},
            {"roomID": 1},
            {"roomID": 2},
            {"roomID": 3}
        ]

        actual_logs = response.json()
        actual_logs_simplified = [{"roomID": log["roomID"]} for log in actual_logs]
        self.assertEqual(expected_logs, actual_logs_simplified)

    def fetch_summary_from_server(self):
        # Fetch the summary from the server using the session cookie
        response = requests.get(
            f"{self.READER_URL}/summary",
            cookies={"session-id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

if __name__ == '__main__':
    unittest.main()