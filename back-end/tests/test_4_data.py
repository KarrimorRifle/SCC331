import unittest
import paho.mqtt.client as mqtt
import json
import time
import os
import requests
import random
import string
from datetime import datetime, timedelta

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
        self.staff = [
            {"PicoID": 15, "RoomID": 1, "PicoType": 4, "Data": 1},
            {"PicoID": 16, "RoomID": 1, "PicoType": 4, "Data": 1},
            {"PicoID": 17, "RoomID": 2, "PicoType": 4, "Data": 1},
            {"PicoID": 18, "RoomID": 3, "PicoType": 4, "Data": 1},
            {"PicoID": 19, "RoomID": 3, "PicoType": 4, "Data": 1},
        ]
        self.guard = [
            {"PicoID": 20, "RoomID": 1, "PicoType": 5, "Data": 1},
            {"PicoID": 21, "RoomID": 2, "PicoType": 5, "Data": 1},
            {"PicoID": 22, "RoomID": 3, "PicoType": 5, "Data": 1},
            {"PicoID": 23, "RoomID": 3, "PicoType": 5, "Data": 1},
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

    def test_01_populate_and_check_rooms(self):
        # Publish luggage, users, room, staff and guard data
        self.publish_data(self.luggage, "feeds/hardware-data/test1_luggage")
        self.publish_data(self.users, "feeds/hardware-data/test1_users")
        self.publish_data(self.room, "feeds/hardware-data/test1_rooms")
        self.publish_data(self.staff, "feeds/hardware-data/test1_staff")
        self.publish_data(self.guard, "feeds/hardware-data/test1_guard")

        # Updated expected summary with staff and guard dummy data
        expected_summary = {
            "1": {
                "users": {"id": ["8", "9"]},
                "luggage": {"id": ["1", "2", "3"]},
                "staff": {"id": ["15", "16"]},
                "guard": {"id": ["20"]},
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
                "users": {"id": ["10", "11", "12"]},
                "luggage": {"id": ["4", "5"]},
                "staff": {"id": ["17"]},
                "guard": {"id": ["21"]},
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
                "users": {"id": ["13", "14"]},
                "luggage": {"id": ["6", "7"]},
                "staff": {"id": ["18", "19"]},
                "guard": {"id": ["22", "23"]},
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

        actual_summary = self.fetch_summary_from_server()
        normalized_actual = {str(k): v for k, v in actual_summary.items()}

        # For each room, verify that all expected keys and values exactly match.
        for room_id, expected_room in expected_summary.items():
            self.assertIn(str(room_id), normalized_actual,
                          f"Room {room_id} missing in actual summary")
            actual_room = normalized_actual[str(room_id)]
            # Verify that all top-level keys exist.
            expected_keys = set(expected_room.keys())
            actual_keys = set(actual_room.keys())
            self.assertEqual(expected_keys, actual_keys,
                             f"Mismatch in keys for room {room_id}")

            # Check each section for both count and id values.
            for section in ["users", "luggage", "staff", "guard"]:
                self.assertIn("count", actual_room[section],
                              f"Missing 'count' key in {section} for room {room_id}")
                self.assertIn("id", actual_room[section],
                              f"Missing 'id' key in {section} for room {room_id}")
                self.assertEqual(expected_room[section]["id"], actual_room[section]["id"],
                                 f"Mismatch in {section} ids for room {room_id}")
                self.assertEqual(actual_room[section]["count"], len(actual_room[section]["id"]),
                                 f"Mismatch in {section} count for room {room_id}")

            # Check environment keys and values.
            self.assertEqual(set(expected_room["environment"].keys()),
                            set(actual_room["environment"].keys()),
                            f"Mismatch in environment keys for room {room_id}")
            for attr in expected_room["environment"]:
                expected_value = expected_room["environment"][attr]
                actual_value = actual_room["environment"][attr]
                if isinstance(expected_value, list):
                    # Check that each item in expected_value is in actual_value.
                    self.assertTrue(set(expected_value).issubset(set(actual_value)),
                                    f"For {attr} in room {room_id}, expected items {expected_value} to be subset of {actual_value}")
                else:
                    try:
                        actual_value = float(actual_value)
                    except (ValueError, TypeError):
                        self.fail(f"Environment attribute {attr} in room {room_id} is not convertible to float")
                    self.assertAlmostEqual(expected_value, actual_value, places=1,
                                        msg=f"Environment attribute '{attr}' mismatch for room {room_id}")

    def test_02_session_validation(self):
        # Publish session data in the known order.
        for item in self.session:
            self.publish_data([item], "feeds/hardware-data/test2_sessions")
            time.sleep(2)  # Ensure messages are processed

        response = requests.get(
            f"{self.READER_URL}/pico/59",
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn("movement", response_json, "Missing 'movement' key in response")
        movement = response_json["movement"]
        self.assertTrue(isinstance(movement, dict), "'movement' should be a dictionary")
        # Sort movement entries by timestamp (assuming ISO 8601 order)
        sorted_timestamps = sorted(movement.keys())
        ordered_rooms = [movement[t] for t in sorted_timestamps]
        expected_order = ["1", "2", "3", "2"]
        self.assertEqual(ordered_rooms, expected_order,
                         f"Expected movement order {expected_order}, got {ordered_rooms}")

    def test_03_session_expiry_and_republish(self):
        # Wait to simulate expiry (2.5 minutes)
        # time.sleep(150)
        for item in self.session2:
            self.publish_data([item], "feeds/hardware-data/test3_sessions")
            time.sleep(2)
        response = requests.get(
            f"{self.READER_URL}/pico/59",
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn("movement", response_json, "Missing 'movement' key in response")
        movement = response_json["movement"]
        self.assertTrue(isinstance(movement, dict), "'movement' should be a dictionary")
        sorted_timestamps = sorted(movement.keys())
        ordered_rooms = [movement[t] for t in sorted_timestamps]
        expected_order = ["3", "1", "2", "3"]
        self.assertEqual(ordered_rooms, expected_order,
                         f"Expected movement order {expected_order}, got {ordered_rooms}")

    def test_04_movement_endpoint(self):
        # Publish two batches of movement data with a delay
        movement_data_1 = [
            {"PicoID": 30, "RoomID": 1, "PicoType": 2, "Data": 1},
            {"PicoID": 31, "RoomID": 2, "PicoType": 2, "Data": 1}
        ]
        movement_data_2 = [
            {"PicoID": 32, "RoomID": 3, "PicoType": 2, "Data": 1},
            {"PicoID": 33, "RoomID": 1, "PicoType": 2, "Data": 1}
        ]
        self.publish_data(movement_data_1, "feeds/hardware-data/test_movement")
        time.sleep(2)
        self.publish_data(movement_data_2, "feeds/hardware-data/test_movement")
        time.sleep(2)
        
        response = requests.get(
            f"{self.READER_URL}/movement",
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        movement_response = response.json()
        self.assertIsInstance(movement_response, dict, "Movement response should be a dict")
        for timestamp, room_movements in movement_response.items():
            self.assertIsInstance(room_movements, dict,
                                  f"At timestamp {timestamp}, expected room movements as a dict")
            for room_id, status in room_movements.items():
                self.assertIsInstance(status, str,
                                      f"At timestamp {timestamp} for room {room_id}, expected status to be a string")
        self.assertGreaterEqual(len(movement_response), 2, "Expected at least 2 distinct timestamps in movement response")

    def test_05_summary_average(self):
        test_room_data = [
            {"PicoID": 300, "RoomID": 1, "PicoType": 1, "Data": "10,20,30,40,50,60"},
            {"PicoID": 301, "RoomID": 2, "PicoType": 1, "Data": "15,25,35,45,55,65"},
            {"PicoID": 302, "RoomID": 3, "PicoType": 1, "Data": "20,30,40,50,60,70"}
        ]
        self.publish_data(test_room_data, "feeds/hardware-data/test_rooms_average")
        time.sleep(3)
        payload = {
            "start_time": "2023-01-01T00:00:00Z",
            "end_time": "2023-12-31T23:59:59Z",
            "time_periods": "1hr",
            "rooms": ["1", "2", "3"]
        }
        response = requests.get(
            f"{self.READER_URL}/summary/average",
            params=payload,  # Use query parameters for GET requests
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200)
        average_summary = response.json()
        self.assertIsInstance(average_summary, dict, "Expected summary/average response to be a dict")
        for timestamp, room_data in average_summary.items():
            for room_id in ["1", "2", "3"]:
                self.assertIn(room_id, room_data,
                              f"Room {room_id} missing in average summary at timestamp {timestamp}")
                # Check that each room's average data includes expected keys (average, peak, trough)
                for metric in ["users", "luggage", "staff", "guard", "light", "IAQ", "temperature", "sound", "pressure", "humidity"]:
                    self.assertIn(metric, room_data[room_id],
                                  f"Metric '{metric}' missing for room {room_id} at timestamp {timestamp}")
                    for subkey in ["average", "peak", "trough"]:
                        self.assertIn(subkey, room_data[room_id][metric],
                                      f"Subkey '{subkey}' missing for {metric} in room {room_id} at timestamp {timestamp}")

    # --- New Negative Tests ---

    def test_06_invalid_session_on_summary(self):
        """Test fetching summary with an invalid session cookie."""
        response = requests.get(
            f"{self.READER_URL}/summary",
            cookies={"session_id": "invalid_session"}
        )
        self.assertIn(response.status_code, [400, 401],
                      f"Expected 400/401 for invalid session, got {response.status_code}")

    def test_07_invalid_pico_endpoint(self):
        """Test the /pico endpoint with a non-existent PicoID."""
        response = requests.get(
            f"{self.READER_URL}/pico/nonexistent",
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 404,
                         "Expected 404 for non-existent PicoID")

    def test_08_missing_required_payload_summary_average(self):
        """Test summary/average endpoint with missing or invalid payload."""
        headers = {"session-id": self.session_cookie}
        payload = {
            "start_time": "",  # Empty value
            "rooms": []        # No rooms specified
        }
        response = requests.get(
            f"{self.READER_URL}/summary/average",
            headers=headers,
            json=payload,
            cookies={"session_id":self.session_cookie}
        )
        self.assertEqual(response.status_code, 400,
                         "Expected 400 for missing/invalid parameters in summary average")

    def test_09_invalid_movement_query_params(self):
        """Test movement endpoint with invalid time query parameters."""
        params = {
            "time_start": "invalid_time",
            "time_end": "another_invalid_time"
        }
        response = requests.get(
            f"{self.READER_URL}/movement",
            cookies={"session_id": self.session_cookie},
            params=params
        )
        self.assertEqual(response.status_code, 400,
                         "Expected 400 for invalid query parameters in movement endpoint")

    def test_10_post_on_get_endpoint(self):
        """Test that a POST request on a GET-only endpoint returns 405."""
        response = requests.post(
            f"{self.READER_URL}/summary",
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 405,
                         "Expected 405 Method Not Allowed for POST on a GET endpoint")

    def test_11_summary_mode_all(self):
        """
        Publish occupancy data and environment data, then query /summary with a snapshot time
        (using current time). Verify that mode 'all' returns both occupancy and environment data.
        """
        # Publish occupancy data (e.g., from self.users) to simulate pico data.
        self.publish_data(self.users, "feeds/hardware-data/test_summary_picos")
        # Publish environment data (simulate room sensor data) using self.room.
        self.publish_data(self.room, "feeds/hardware-data/test_summary_env")
        # Wait a few seconds to let the data be processed.
        time.sleep(5)
        # Use the current time as snapshot_time.
        snapshot_time = datetime.utcnow().isoformat() + "Z"
        params = {"time": snapshot_time, "mode": "all"}
        response = requests.get(
            f"{self.READER_URL}/summary",
            params=params,
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200, "Expected 200 OK from /summary with mode all")
        summary_data = response.json()
        # Check that each room that has occupancy data also has environment data.
        for room_id, data in summary_data.items():
            # For occupancy, at least one pico should be present in one of the categories.
            pico_present = any(data[occ]["count"] > 0 for occ in ["users", "luggage", "staff", "guard"])
            self.assertTrue(pico_present, f"Expected occupancy data for room {room_id}")
            # And environment data should be non-empty.
            self.assertTrue(data["environment"], f"Expected environment data for room {room_id}")

    def test_12_summary_mode_picos(self):
        """
        Publish occupancy data only, then query /summary with mode "picos".
        Verify that the returned data includes occupancy data but no environment data.
        """
        # Publish occupancy data
        self.publish_data(self.users, "feeds/hardware-data/test_summary_picos")
        # (Do not publish any environment data.)
        time.sleep(5)
        snapshot_time = datetime.utcnow().isoformat() + "Z"
        params = {"time": snapshot_time, "mode": "picos"}
        response = requests.get(
            f"{self.READER_URL}/summary",
            params=params,
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200, "Expected 200 OK from /summary with mode picos")
        summary_data = response.json()
        # Verify that occupancy data is present and that the environment key is empty or missing.
        for room_id, data in summary_data.items():
            pico_present = any(data[occ]["count"] > 0 for occ in ["users", "luggage", "staff", "guard"])
            self.assertTrue(pico_present, f"Expected occupancy data for room {room_id}")
            # Either environment key is an empty dict or not provided.
            self.assertTrue(not data["environment"] or data["environment"] == {},
                            f"Did not expect environment data for room {room_id} in mode picos")

    def test_13_summary_environment_no_data(self):
        """
        Publish environment data older than one minute, then query /summary with a snapshot time 
        that is recent. Verify that no environment data is returned (since no record exists within 
        the last minute).
        """
        # Publish environment data, but simulate it being old by publishing it with a back-dated time.
        # For testing, assume that publishing to "feeds/hardware-data/test_summary_env" uses the current time,
        # so we wait long enough to ensure that record is older than one minute.
        self.publish_data(self.room, "feeds/hardware-data/test_summary_env")
        # Wait for 70 seconds (more than one minute) so that the environment record is now older.
        time.sleep(70)
        # Now query with a snapshot time of 'now' so that no environment data exists in the last minute.
        snapshot_time = datetime.utcnow().isoformat() + "Z"
        params = {"time": snapshot_time, "mode": "environment"}
        response = requests.get(
            f"{self.READER_URL}/summary",
            params=params,
            cookies={"session_id": self.session_cookie}
        )
        self.assertEqual(response.status_code, 200, "Expected 200 OK from /summary with mode environment")
        summary_data = response.json()
        # For each room in the summary, the environment data should be empty (since no record is recent)
        for room_id, data in summary_data.items():
            self.assertFalse(data["environment"],
                            f"Expected no environment data for room {room_id} as records are too old")

    # --- Helper Methods ---

    def fetch_summary_from_server(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            response = requests.get(
                f"{self.READER_URL}/summary",
                cookies={"session_id": self.session_cookie}
            )
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        self.fail("Failed to fetch summary from server after 5 attempts.")

    def assert_logs_contain(self, expected, actual):
        actual_simplified = [{"roomID": log["roomID"]} for log in actual]
        for expected_log in expected:
            self.assertIn(expected_log, actual_simplified)

if __name__ == '__main__':
    unittest.main()
