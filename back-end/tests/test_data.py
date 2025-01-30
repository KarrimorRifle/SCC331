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
    ACCOUNTS_URL = "http://localhost:5001"
    LOGIN_URL = "http://localhost:5002"
    READER_URL = "http://localhost:5003"

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
            {"PicoID": 205, "RoomID": 1, "PicoType": 1, "Data": "10,12,34"},
            {"PicoID": 209, "RoomID": 2, "PicoType": 1, "Data": "21,30,12"},
            {"PicoID": 200, "RoomID": 3, "PicoType": 1, "Data": "13,17,9"}
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

    def publish_data(self, data):
        client = mqtt.Client()
        client.username_pw_set(self.MQTT_TOKEN, None)
        client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
        client.loop_start()
        for item in data:
            payload = json.dumps(item)
            client.publish(self.MQTT_TOPIC, payload)
            time.sleep(1)  # Sleep to ensure messages are sent
        client.loop_stop()
        client.disconnect()

    def test_1_populate_and_check_rooms(self):
        # Publish luggage data
        self.publish_data(self.luggage)
        # Publish users data
        self.publish_data(self.users)
        # Publish room data
        self.publish_data(self.room)

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
                    "light": 34
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
                    "light": 12
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
                    "light": 9
                }
            }
        }

        # Simulate fetching the summary from the server
        actual_summary = self.fetch_summary_from_server()

        self.assertEqual(expected_summary, actual_summary)

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