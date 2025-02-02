import unittest
import requests

BASE_URL_EDITOR = "http://localhost:5011"
BASE_URL_READER = "http://localhost:5010"

class TestAssets(unittest.TestCase):
    headers = {'Content-Type': 'application/json'}
    cookies = {'session_id': 'dummy_admin'}  # Dummy admin session cookie

    @classmethod
    def setUpClass(cls):
        # Optionally, perform any global API cleanup if supported
        pass

    def setUp(self):
        # Keep track of presets created during each test for cleanup
        self.created_presets = []

    def tearDown(self):
        # Clean up any presets created in this test
        for preset in self.created_presets:
            try:
                self.delete_preset(preset['preset_id'], preset['name'])
            except Exception as e:
                # Preset might have been already deleted; skip error.
                pass

    # Helper functions
    def create_preset(self, name, trusted=None):
        url = f"{BASE_URL_EDITOR}/presets"
        data = {"name": name, "trusted": trusted or []}
        response = requests.post(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 201, msg=f"Failed to create preset '{name}'")
        preset = response.json()
        # Record created preset for cleanup.
        preset['name'] = name  # Ensure the name is stored
        self.created_presets.append(preset)
        return preset

    def list_presets(self):
        url = f"{BASE_URL_READER}/preset"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to list presets")
        return response.json()  # Expected: list of preset dicts

    def delete_preset(self, preset_id, preset_name):
        url = f"{BASE_URL_EDITOR}/preset"
        data = {"preset-id": preset_id, "preset-name": preset_name}
        response = requests.delete(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to delete preset")

    def rename_preset(self, preset_id, new_name):
        url = f"{BASE_URL_EDITOR}/presets/{preset_id}"
        data = {"name": new_name}
        response = requests.patch(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to rename preset")

    def add_boxes(self, preset_id, boxes):
        url = f"{BASE_URL_EDITOR}/presets/{preset_id}/boxes"
        data = {"boxes": boxes}
        response = requests.post(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 201, msg="Failed to add boxes")
        return response.json()  # Expected: { "boxes": [ { "box_id": ..., ... }, ... ] }

    def rename_box(self, box_id, new_label):
        url = f"{BASE_URL_EDITOR}/boxes/{box_id}"
        data = {"label": new_label}
        response = requests.patch(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to rename box")

    def delete_box(self, box_id):
        url = f"{BASE_URL_EDITOR}/boxes/{box_id}"
        response = requests.delete(url, headers=self.headers, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to delete box")

    # Test cases with numbered methods for desired order

    def test_01_create_preset_and_verify(self):
        preset = self.create_preset("Test Preset 1")
        presets = self.list_presets()
        preset_ids = [p['preset_id'] for p in presets]
        self.assertIn(preset['preset_id'], preset_ids, msg="Preset not found in list after creation")

    def test_02_create_two_presets(self):
        preset1 = self.create_preset("Test Preset 2")
        preset2 = self.create_preset("Test Preset 3")
        presets = self.list_presets()
        preset_ids = [p['preset_id'] for p in presets]
        self.assertIn(preset1['preset_id'], preset_ids, msg="First preset is missing")
        self.assertIn(preset2['preset_id'], preset_ids, msg="Second preset is missing")

    def test_03_delete_preset(self):
        preset = self.create_preset("Preset To Delete")
        # Explicit deletion
        self.delete_preset(preset['preset_id'], "Preset To Delete")
        # Remove preset from created_presets to avoid tearDown error
        self.created_presets = [p for p in self.created_presets if p['preset_id'] != preset['preset_id']]
        presets = self.list_presets()
        preset_ids = [p['preset_id'] for p in presets]
        self.assertNotIn(preset['preset_id'], preset_ids, msg="Preset was not deleted")

    def test_04_rename_preset(self):
        preset = self.create_preset("Old Preset Name")
        self.rename_preset(preset['preset_id'], "New Preset Name")
        presets = self.list_presets()
        renamed = next((p for p in presets if p['preset_id'] == preset['preset_id']), None)
        self.assertIsNotNone(renamed, msg="Renamed preset not found")
        self.assertEqual(renamed['name'], "New Preset Name", msg="Preset name did not update correctly")

    def test_05_populate_preset_with_boxes(self):
        preset = self.create_preset("Preset With Boxes")
        boxes = [
            {
                "roomID": "Room1",
                "label": "Box 1",
                "top": 10,
                "left": 20,
                "width": 100,
                "height": 150,
                "colour": "#FF0000"
            },
            {
                "roomID": "Room2",
                "label": "Box 2",
                "top": 15,
                "left": 25,
                "width": 110,
                "height": 160,
                "colour": "#00FF00"
            }
        ]
        result = self.add_boxes(preset['preset_id'], boxes)
        self.assertTrue(len(result.get('boxes', [])) >= 2, msg="Boxes were not added properly")

    def test_06_rename_box(self):
        preset = self.create_preset("Preset For Box Rename")
        boxes = [{
            "roomID": "Room1",
            "label": "Original Box",
            "top": 10,
            "left": 20,
            "width": 100,
            "height": 150,
            "colour": "#0000FF"
        }]
        result = self.add_boxes(preset['preset_id'], boxes)
        box = result['boxes'][0]
        self.rename_box(box['box_id'], "Renamed Box")
        # Retrieve preset details to verify box label update
        url = f"{BASE_URL_READER}/preset/{preset['preset_id']}"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to retrieve preset details after box rename")
        data = response.json()
        updated_box = next((b for b in data.get('boxes', []) if b['box_id'] == box['box_id']), None)
        self.assertIsNotNone(updated_box, msg="Updated box not found")
        self.assertEqual(updated_box['label'], "Renamed Box", msg="Box label did not update properly")

    def test_07_delete_box(self):
        preset = self.create_preset("Preset For Box Deletion")
        boxes = [{
            "roomID": "Room1",
            "label": "Box to Delete",
            "top": 10,
            "left": 20,
            "width": 100,
            "height": 150,
            "colour": "#123456"
        }]
        result = self.add_boxes(preset['preset_id'], boxes)
        box = result['boxes'][0]
        self.delete_box(box['box_id'])
        # Retrieve preset details to verify deletion
        url = f"{BASE_URL_READER}/preset/{preset['preset_id']}"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to retrieve preset details after box deletion")
        data = response.json()
        remaining = [b for b in data.get('boxes', []) if b['box_id'] == box['box_id']]
        self.assertEqual(len(remaining), 0, msg="Box was not deleted")

    # Additional test: Get preset details including boxes, permissions, and image
    def test_08_get_preset_details(self):
        preset = self.create_preset("Detailed Preset")
        boxes = [{
            "roomID": "RoomDetail",
            "label": "Detail Box",
            "top": 5,
            "left": 5,
            "width": 50,
            "height": 50,
            "colour": "#ABCDEF"
        }]
        self.add_boxes(preset['preset_id'], boxes)
        url = f"{BASE_URL_READER}/preset/{preset['preset_id']}"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to retrieve detailed preset")
        data = response.json()
        self.assertIn("boxes", data, msg="Preset details missing boxes field")
        self.assertIn("permission", data, msg="Preset details missing permission field")
        self.assertIn("image", data, msg="Preset details missing image field")

if __name__ == '__main__':
    unittest.main()