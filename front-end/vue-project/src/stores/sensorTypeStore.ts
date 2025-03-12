import { ref } from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faUser, faEye, faUsers, faTemperatureLow, faTint, faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf, faSuitcaseRolling, faClipboardCheck, faShieldHalved} from '@fortawesome/free-solid-svg-icons';
library.add(faUser, faEye, faUsers, faTemperatureLow, faTint, faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf, faSuitcaseRolling, faClipboardCheck, faShieldHalved);

/**
 * This is the mapping for all the sensors (in the future, can add whatever over here)
 */
export const sensorMapping = ref({
  "users": { name: "User", icon: faUser, type: 2 },
  "luggage": { name: "Luggage", icon: faSuitcaseRolling, type: 2 },
  "guard": { name: "Guard", icon: faShieldHalved, type: 2 },
  "staff": { name: "Staff", icon: faClipboardCheck, type: 2 },
  "iaq": { name: "IAQ Sensor", icon: faTemperatureLow, type: 1 },
  "humidity": { name: "Humidity Sensor", icon: faTint, type: 1 },
  "light": { name: "Light Sensor", icon: faLightbulb, type: 1 },
  "pressure": { name: "Pressure Sensor", icon: faArrowDown, type: 1 },
  "sound": { name: "Sound Sensor", icon: faVolumeUp, type: 1 },
  "temperature": { name: "Temperature Sensor", icon: faThermometerHalf, type: 1 }
});

/**
 * This is the list of all the sensors we have, which can be changed when converted to supermarket
 */
export const sensors = ref([
  { name: "users", displayName: sensorMapping.value["users"].name, icon: sensorMapping.value["users"].icon.iconName, checked: true, disconnected: true, type: 2 },
  { name: "luggage", displayName: sensorMapping.value["luggage"].name, icon: sensorMapping.value["luggage"].icon.iconName, checked: true, disconnected: true, type: 2 },
  { name: "guard", displayName: sensorMapping.value["guard"].name, icon: sensorMapping.value["guard"].icon.iconName, checked: true, disconnected: true, type: 2 },
  { name: "staff", displayName: sensorMapping.value["staff"].name, icon: sensorMapping.value["staff"].icon.iconName, checked: true, disconnected: true, type: 2 },
  { name: "iaq", displayName: sensorMapping.value["iaq"].name, icon: sensorMapping.value["iaq"].icon.iconName, checked: true, disconnected: true, type: 1 },
  { name: "humidity", displayName: sensorMapping.value["humidity"].name, icon: sensorMapping.value["humidity"].icon.iconName, checked: true, disconnected: true, type: 1 },
  { name: "light", displayName: sensorMapping.value["light"].name, icon: sensorMapping.value["light"].icon.iconName, checked: true, disconnected: true, type: 1 },
  { name: "pressure", displayName: sensorMapping.value["pressure"].name, icon: sensorMapping.value["pressure"].icon.iconName, checked: true, disconnected: true, type: 1 },
  { name: "sound", displayName: sensorMapping.value["sound"].name, icon: sensorMapping.value["sound"].icon.iconName, checked: true, disconnected: true, type: 1 },
  { name: "temperature", displayName: sensorMapping.value["temperature"].name, icon: sensorMapping.value["temperature"].icon.iconName, checked: true, disconnected: true, type: 1 }
]);



/**
export const sensors = ref([]);
export const updateSensorMappings = async () => {
  try {
    const response = await fetch('http://localhost:5010/get/device/configs');
    const data = await response.json();

    if (!data.configs) return;

    data.configs.forEach(device => {
      const { readablePicoID, picoType } = device;

      // Skip unassigned devices
      if (picoType === 0) return;

      // If sensor does not exist in mapping, add it
      if (!sensorMapping.value[readablePicoID]) {
        sensorMapping.value[readablePicoID] = {
          name: readablePicoID,
          icon: faQuestion, // Default icon if not mapped
          type: picoType
        };
      }
    });

    // Update reactive `sensors` list
    sensors.value = Object.entries(sensorMapping.value).map(([key, sensor]) => ({
      name: key,
      displayName: sensor.name,
      icon: sensor.icon.iconName,
      checked: true,
      disconnected: true,
      type: sensor.type
    }));

  } catch (error) {
    console.error("Failed to fetch sensor mappings:", error);
  }
};
// Run this function on app startup to load mappings
updateSensorMappings();
 */