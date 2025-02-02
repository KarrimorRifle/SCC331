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
        # Track created presets for cleanup
        self.created_presets = []

    def tearDown(self):
        # Clean up any presets created in this test
        for preset in self.created_presets:
            try:
                self.delete_preset(preset['preset_id'])
            except Exception:
                pass

    # Helper functions
    def create_preset(self, name, trusted=None):
        url = f"{BASE_URL_EDITOR}/presets"
        data = {"name": name, "trusted": trusted or []}
        response = requests.post(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 201, msg=f"Failed to create preset '{name}'")
        preset = response.json()
        preset['name'] = name  # keep name for reference
        self.created_presets.append(preset)
        return preset

    def list_presets(self):
        url = f"{BASE_URL_READER}/presets"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to list presets")
        return response.json()

    def delete_preset(self, preset_id):
        url = f"{BASE_URL_EDITOR}/presets/{preset_id}"
        response = requests.delete(url, headers=self.headers, cookies=self.cookies)
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
        return response.json()

    def patch_boxes(self, preset_id, boxes):
        url = f"{BASE_URL_EDITOR}/presets/{preset_id}/boxes"
        data = {"boxes": boxes}
        response = requests.patch(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to patch boxes")
        return response.json()

    def upload_image(self, preset_id, image_name, image_data):
        url = f"{BASE_URL_EDITOR}/presets/{preset_id}/image"
        data = {"name": image_name, "data": image_data}
        response = requests.post(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 201, msg="Failed to upload image")
        return response.json()

    # Test cases

    def test_01_create_preset_and_verify(self):
        preset = self.create_preset("Test Preset 1")
        presets = self.list_presets()
        preset_ids = [p['preset_id'] for p in presets.get("presets", [])]
        self.assertIn(preset['preset_id'], preset_ids,
                      msg="Preset not found in list after creation")

    def test_02_create_two_presets(self):
        preset1 = self.create_preset("Test Preset 2")
        preset2 = self.create_preset("Test Preset 3")
        presets = self.list_presets()
        preset_ids = [p['preset_id'] for p in presets.get("presets", [])]
        self.assertIn(preset1['preset_id'], preset_ids, msg="First preset is missing")
        self.assertIn(preset2['preset_id'], preset_ids, msg="Second preset is missing")

    def test_03_delete_preset(self):
        preset = self.create_preset("Preset To Delete")
        self.delete_preset(preset['preset_id'])
        self.created_presets = [p for p in self.created_presets if p['preset_id'] != preset['preset_id']]
        presets = self.list_presets()
        preset_ids = [p['preset_id'] for p in presets.get("presets", [])]
        self.assertNotIn(preset['preset_id'], preset_ids, msg="Preset was not deleted")

    def test_04_rename_preset(self):
        preset = self.create_preset("Old Preset Name")
        self.rename_preset(preset['preset_id'], "New Preset Name")
        presets = self.list_presets()
        renamed = next((p for p in presets.get("presets", []) if p['preset_id'] == preset['preset_id']), None)
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

    def test_06_get_preset_details(self):
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
        url = f"{BASE_URL_READER}/presets/{preset['preset_id']}"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to retrieve preset details")
        data = response.json()
        self.assertIn("boxes", data, msg="Preset details missing boxes field")
        self.assertIn("permission", data, msg="Preset details missing permission field")
        self.assertIn("image", data, msg="Preset details missing image field")

    def test_07_upload_preset_image(self):
        # Create a preset, then upload an image
        preset = self.create_preset("Preset With Image")
        dummy_image_data = "Base64DummyString=="
        self.upload_image(preset['preset_id'], "background.png", dummy_image_data)
        # Retrieve details to check image field
        url = f"{BASE_URL_READER}/presets/{preset['preset_id']}"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to retrieve preset details after image upload")
        data = response.json()
        self.assertIn("image", data, msg="Preset details missing image after upload")
        self.assertEqual(data["image"].get("name"), "background.png", msg="Image name mismatch")
        self.assertEqual(data["image"].get("data"), dummy_image_data, msg="Image data mismatch")

    def test_08_rename_and_move_boxes(self):
        preset = self.create_preset("Preset for Box Modify")
        # Add an initial box using add_boxes
        initial_box = [{
            "roomID": "Room1",
            "label": "Original Box",
            "top": 10,
            "left": 20,
            "width": 100,
            "height": 150,
            "colour": "#FF0000"
        }]
        add_result = self.add_boxes(preset['preset_id'], initial_box)
        self.assertTrue(add_result.get("boxes"), "Initial box not added")
        
        # Update the box: rename it and change coordinates (move top and left)
        updated_box = [{
            "roomID": "Room1",
            "label": "Modified Box",
            "top": 30,
            "left": 40,
            "width": 100,
            "height": 150,
            "colour": "#FF0000"
        }]
        self.patch_boxes(preset['preset_id'], updated_box)
        
        # Retrieve preset details to verify the update
        url = f"{BASE_URL_READER}/presets/{preset['preset_id']}"
        response = requests.get(url, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to retrieve preset details after patching boxes")
        data = response.json()
        boxes_list = data.get("boxes", [])
        matched = any(b.get("label") == "Modified Box" and b.get("top") == 30 and b.get("left") == 40 for b in boxes_list)
        self.assertTrue(matched, msg="Box update not reflected in preset details")

    def test_09_set_default_preset(self):
        preset1 = self.create_preset("Default Preset Test 1")
        preset2 = self.create_preset("Default Preset Test 2")
        url = f"{BASE_URL_EDITOR}/presets/default"
        
        # Set default to preset1
        data = {"preset_id": preset1['preset_id']}
        response = requests.patch(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to set default preset to preset1")
        
        # Verify default is preset1
        list_response = requests.get(f"{BASE_URL_READER}/presets", cookies=self.cookies)
        self.assertEqual(list_response.status_code, 200, msg="Failed to list presets after setting default")
        json_data = list_response.json()
        self.assertEqual(str(json_data.get("default")), str(preset1['preset_id']),
                         msg="Default preset not set correctly to preset1")
        
        # Change default to preset2
        data = {"preset_id": preset2['preset_id']}
        response = requests.patch(url, headers=self.headers, json=data, cookies=self.cookies)
        self.assertEqual(response.status_code, 200, msg="Failed to update default preset to preset2")
        
        # Verify default is now preset2
        list_response = requests.get(f"{BASE_URL_READER}/presets", cookies=self.cookies)
        self.assertEqual(list_response.status_code, 200, msg="Failed to list presets after changing default")
        json_data = list_response.json()
        self.assertEqual(str(json_data.get("default")), str(preset2['preset_id']),
                         msg="Default preset not updated correctly to preset2")

if __name__ == '__main__':
    unittest.main()