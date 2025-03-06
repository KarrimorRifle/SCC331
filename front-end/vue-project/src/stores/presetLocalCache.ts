import { defineStore } from "pinia";
import { ref, watch, computed } from "vue";
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

const testPresetStoreData = {
  "1": {
      "box": {
          "top": 10,
          "left": 10,
          "width": 429,
          "height": 101,
          "colour": "#ada330"
      },
      "label": "1",
      
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
  const localCache = ref<Record<string, any>>({...testPresetData});

  watch(localCache, (newVal) => {
    console.log("Updated Local Cache:", newVal);
  }, { deep: true, immediate: true });

  watch(
    () => presetStore.boxes_and_data,
    (newData) => {
      if (Object.keys(newData).length > 0) {
        Object.entries(newData).forEach(([key, area]) => {
          if (!localCache.value[key]) {
            // ✅ If new area appears, add it completely
            localCache.value[key] = { ...area };
          } else {
            // ✅ Preserve box & label, only overwrite tracker
            localCache.value[key] = {
              ...localCache.value[key], // Keep existing box & label
              tracker: area.tracker || localCache.value[key].tracker // Keep old tracker if missing
            };
          }
        });
      }
    },
    { deep: true, immediate: true }
  );

  const disconnectedSensors = computed(() => {
    const disconnected = new Map<string, Set<string>>(); // ✅ Use a Map to store per-area disconnections
  
    Object.entries(localCache.value).forEach(([areaKey, area]) => {
      if (!area.tracker) return; // Skip areas without trackers
  
      const latestTracker = testPresetStoreData[areaKey]?.tracker || {}; // ✅ Get latest tracker
  
      Object.entries(area.tracker).forEach(([sensorType, sensorValue]) => {
        if (sensorType === "environment" && typeof sensorValue === "object") {
          // ✅ Check each environmental sensor separately
          Object.keys(sensorValue).forEach(envKey => {
            if (
              !latestTracker.environment || // If environment tracker is missing
              !(envKey in latestTracker.environment) || // If specific sensor is missing
              latestTracker.environment[envKey] === undefined // If sensor is explicitly undefined
            ) {
              console.log(`Environmental Sensor ${envKey} in area ${areaKey} is disconnected.`);
              if (!disconnected.has(areaKey)) {
                disconnected.set(areaKey, new Set());
              }
              disconnected.get(areaKey)?.add(envKey.toLowerCase());
            }
          });
        } else {
          // ✅ Check general sensors (users, luggage, staff, etc.)
          if (
            !(sensorType in latestTracker) || // If the sensor type is missing
            latestTracker[sensorType] === undefined // If it is explicitly undefined
          ) {
            console.log(`Sensor ${sensorType} in area ${areaKey} is disconnected.`);
            if (!disconnected.has(areaKey)) {
              disconnected.set(areaKey, new Set());
            }
            disconnected.get(areaKey)?.add(sensorType);
          }
        }
      });
    });
  
    return disconnected;
  });
  
  
  return { localCache, disconnectedSensors };
});

