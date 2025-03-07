import { defineStore } from "pinia";
import { computed } from "vue";
import { usePresetStore } from "../utils/useFetchPresets";

const testPresetData = {
  "1": {
      "box": {
          "top": 10,
          "left": 10,
          "width": 429,
          "height": 101,
          "colour": "#ada330"
      },
      "label": "1",
      "tracker": {
          "environment": {
              "IAQ": 11,
              "humidity": 20,
              "light": 12,
              "pressure": 20,
              "sound": 10,
              "temperature": 34
          },
          "guard": {
              "count": 0,
              "id": []
          },
          "luggage": {
              "count": 3,
              "id": [
                  "1",
                  "2",
                  "3"
              ]
          },
          "staff": {
              "count": 2,
              "id": [
                  "15",
                  "16"
              ]
          },
          "users": {
              "count": 2,
              "id": [
                  "8",
                  "9"
              ]
          }
      }
  },
  "2": {
      "box": {
          "top": 48,
          "left": 518,
          "width": 100,
          "height": 100,
          "colour": "#b158ad"
      },
      "label": "2",
      "tracker": {
          "environment": {
              "IAQ": 23,
              "humidity": 12,
              "light": 30,
              "pressure": 15,
              "sound": 21,
              "temperature": 12
          },
          "guard": {
              "count": 0,
              "id": []
          },
          "luggage": {
              "count": 2,
              "id": [
                  "4",
                  "5"
              ]
          },
          "staff": {
              "count": 1,
              "id": [
                  "17"
              ]
          },
          "users": {
              "count": 3,
              "id": [
                  "10",
                  "11",
                  "12"
              ]
          }
      }
  },
  "3": {
      "box": {
          "top": 134,
          "left": 10,
          "width": 100,
          "height": 100,
          "colour": "#3ee110"
      },
      "label": "3",
      "tracker": {
          "environment": {
              "IAQ": 53,
              "humidity": 63,
              "light": 17,
              "pressure": 23,
              "sound": 13,
              "temperature": 9
          },
          "guard": {
              "count": 0,
              "id": []
          },
          "luggage": {
              "count": 2,
              "id": [
                  "6",
                  "7"
              ]
          },
          "staff": {
              "count": 0,
              "id": []
          },
          "users": {
              "count": 2,
              "id": [
                  "13",
                  "14"
              ]
          }
      }
  },
  "101": {
      "box": {
          "top": 187,
          "left": 456,
          "width": 288,
          "height": 166,
          "colour": "#8B572A"
      },
      "label": "101",
      "tracker": {
          "environment": {
              "IAQ": 22,
              "humidity": 45,
              "light": 55,
              "pressure": 1015,
              "sound": 15,
              "temperature": 25
          },
          "guard": {
              "count": 0,
              "id": []
          },
          "luggage": {
              "count": 0,
              "id": []
          },
          "staff": {
              "count": 0,
              "id": []
          },
          "users": {
              "count": 0,
              "id": []
          }
      }
  }
}

export const usePresetLocalCache = defineStore("presetLocalCache", () => {
  const presetStore = usePresetStore();

  /**
   * Computes the currently available sensors dynamically based on tracker data.
   * Each area key contains a `Set<string>` of sensors that are present.
   */
  const connectedSensors = computed(() => {
    const availableSensors = new Map<string, Set<string>>(); // Stores available sensors per area

    // Object.entries(testPresetData).forEach(([areaKey, area]) => {
    Object.entries(presetStore.boxes_and_data).forEach(([areaKey, area]) => {
      if (!area.tracker) {
        // No tracker data at all → Set is empty (no sensors available)
        availableSensors.set(areaKey, new Set());
        return;
      }

      const activeSensors = new Set<string>();

      // Check environmental sensors
      if (area.tracker.environment && typeof area.tracker.environment === "object") {
        Object.keys(area.tracker.environment).forEach(envKey => {
          if (area.tracker.environment[envKey] !== undefined) {
            activeSensors.add(envKey.toLowerCase());
          }
        });
      }

      // Check general sensors (users, luggage, staff, guard, etc.)
      Object.entries(area.tracker).forEach(([sensorType, sensorValue]) => {
        if (sensorType !== "environment") {
          if (sensorValue && sensorValue.count > 0) {
            activeSensors.add(sensorType.toLowerCase());
          }
        }
      });

      // Store the active sensors for this area
      availableSensors.set(areaKey, activeSensors);
    });

    return availableSensors;
  });

  return { connectedSensors };
});