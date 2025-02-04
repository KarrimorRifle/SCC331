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
            {"PicoID": 1, "RoomID": 2, "PicoType": 2, "Data": 1},
            {"PicoID": 1, "RoomID": 1, "PicoType": 2, "Data": 1}, # Adding a duplicate of the same luggage, making sure it doesnt pop up in two areas
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

        # Expected summary with explicit float values for environment data
        expected_summary = {
            "1": {
                "users": {
                    "id": ["8", "9"]
                },
                "luggage": {
                    "id": ["1", "2", "3"]
                },
                "environment": {
                    "sound": 10.0,
                    "light": 12.0,
                    "temperature": 34.0,
                    "IAQ": 11.0,
                    "pressure": 20.0,
                    "humidity": 20.0
                }
            },
            "2": {
                "users": {
                    "id": ["10", "11", "12"]
                },
                "luggage": {
                    "id": ["4", "5"]
                },
                "environment": {
                    "sound": 21.0,
                    "light": 30.0,
                    "temperature": 12.0,
                    "IAQ": 23.0,
                    "pressure": 15.0,
                    "humidity": 12.0
                }
            },
            "3": {
                "users": {
                    "id": ["13", "14"]
                },
                "luggage": {
                    "id": ["6","7"]
                },
                "environment": {
                    "sound": 13.0,
                    "light": 17.0,
                    "temperature": 9.0,
                    "IAQ": 53.0,
                    "pressure": 23.0,
                    "humidity": 63.0
                }
            }
        }

        # Fetch the summary from the server
        actual_summary = self.fetch_summary_from_server()

        # Normalize room keys to strings in actual response
        normalized_actual = {str(k): v for k, v in actual_summary.items()}

        # For each room in expected summary, check individual attributes.
        for room_id, expected_room in expected_summary.items():
            self.assertIn(str(room_id), normalized_actual,
                        f"Room {room_id} missing in actual summary")
            actual_room = normalized_actual[str(room_id)]

            # Check users data
            self.assertIn("users", actual_room, f"Users key missing for room {room_id}")
            # self.assertEqual(expected_room["users"]["count"], int(actual_room["users"]["count"]),
            #                 f"Users count mismatch for room {room_id}")
            # Compare sorted lists for users ids.
            self.assertEqual(sorted(expected_room["users"]["id"]), sorted(actual_room["users"]["id"]),
                            f"Users ids mismatch for room {room_id}")

            # Check luggage data
            self.assertIn("luggage", actual_room, f"Luggage key missing for room {room_id}")
            # self.assertEqual(expected_room["luggage"]["count"], int(actual_room["luggage"]["count"]),
            #                 f"Luggage count mismatch for room {room_id}")
            self.assertEqual(sorted(expected_room["luggage"]["id"]), sorted(actual_room["luggage"]["id"]),
                            f"Luggage ids mismatch for room {room_id}")

            # Check environment data (convert actual values to float and compare)
            self.assertIn("environment", actual_room, f"Environment key missing for room {room_id}")
            for attr, expected_value in expected_room["environment"].items():
                self.assertIn(attr, actual_room["environment"],
                            f"Attribute {attr} missing in environment data for room {room_id}")
                try:
                    actual_value = float(actual_room["environment"][attr])
                except (ValueError, TypeError):
                    self.fail(f"Attribute {attr} in room {room_id} is not convertible to float")
                self.assertAlmostEqual(expected_value, actual_value, places=1,
                                    msg=f"Environment attribute '{attr}' mismatch for room {room_id}")

    def test_2_session_validation(self):
        # Publish session data
        for item in self.session:
            self.publish_data([item], "feeds/hardware-data/test2_sessions")
            time.sleep(2)  # Sleep to ensure messages are sent

        # Fetch the session logs for PicoID 1
        response = requests.get(
            f"{self.READER_URL}/pico/59",
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)

        expected_logs = [
            {"roomID": "1"},
            {"roomID": "2"},
            {"roomID": "3"},
            {"roomID": "2"}
        ]

        actual_logs = response.json()
        self.assert_logs_contain(expected_logs, actual_logs)

    def test_3_session_expiry_and_republish(self):
        # # Wait for 2.5 minutes
        # time.sleep(150) # undo when the other test works

        # Publish session2 data
        for item in self.session2:
            self.publish_data([item], "feeds/hardware-data/test3_sessions")
            time.sleep(2)  # Sleep to ensure messages are sent

        # Fetch the session logs for PicoID 59
        response = requests.get(
            f"{self.READER_URL}/pico/59",
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)

        expected_logs = [
            {"roomID": "3"},
            {"roomID": "1"},
            {"roomID": "2"},
            {"roomID": "3"}
        ]

        actual_logs = response.json()
        self.assert_logs_contain(expected_logs, actual_logs)

    def fetch_summary_from_server(self):
        import time
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.get(
                f"{self.READER_URL}/summary",
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)  # Wait for 2 seconds before retrying
        self.fail("Failed to fetch summary from server after 5 attempts.")

    def assert_summary_contains(self, expected, actual):
        # Normalize room keys to strings for comparison
        normalized_actual = {str(k): v for k, v in actual.items()}
        for room_id, expected_data in expected.items():
            self.assertIn(str(room_id), normalized_actual)
            actual_room = normalized_actual[str(room_id)]
            for key, value in expected_data.items():
                self.assertIn(key, actual_room)
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        self.assertIn(sub_key, actual_room[key])
                        # For list type values, compare sorted lists
                        if isinstance(sub_value, list):
                            self.assertEqual(sorted(sub_value), sorted(actual_room[key][sub_key]))
                        else:
                            self.assertEqual(sub_value, actual_room[key][sub_key])
                elif isinstance(value, list):
                    # Compare lists irrespective of order
                    self.assertEqual(sorted(value), sorted(actual_room[key]))
                else:
                    self.assertEqual(value, actual_room[key])

    def assert_logs_contain(self, expected, actual):
        actual_simplified = [{"roomID": log["roomID"]} for log in actual]
        for expected_log in expected:
            self.assertIn(expected_log, actual_simplified)

if __name__ == '__main__':
    unittest.main()