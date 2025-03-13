import { ref, nextTick } from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faUser, faShoppingCart, faUsers, faTemperatureLow, faTint,
  faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf,
  faSuitcaseRolling, faClipboardCheck, faShieldHalved, faTowerBroadcast
} from '@fortawesome/free-solid-svg-icons';
import { fetchDomainConfig, domainConfig } from '@/constants/HomeConfig';
import axios from 'axios';

// Add icons to the library.
library.add(
  faUser, faShoppingCart, faUsers, faTemperatureLow, faTint,
  faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf,
  faSuitcaseRolling, faClipboardCheck, faShieldHalved, faTowerBroadcast
);

/**
 * Types for summary response.
 */
interface SensorSummary {
  count: number;
  id: string[];
}

interface RoomSummary {
  // Each key corresponds to a sensor summary.
  [sensorKey: string]: any;
}

/**
 * Reactive state for the current domain.
 */
export const currentDomain = ref<string>(domainConfig.value.config.domain.toLowerCase());

/**
 * Domain-specific sensor name overrides.
 * (Only applied for non-environment sensors in this example)
 */
const domainOverrides: Record<string, Record<string, string[]>> = {
  airport: {
    user: ["User", "Passenger"],
    luggage: ["Luggage"],
    guard: ["Guard", "Security"],
    staff: ["Staff"]
  },
  supermarket: {
    user: ["Customer", "User", "Passenger"],
    luggage: ["Trolley"],
    guard: ["Security"],
    staff: ["Employee"]
  }
};

/**
 * Domain-specific icons.
 * Expanded to include environment sensors.
 */
const domainIcons: Record<string, Record<string, any>> = {
  airport: {
    user: faUser,
    luggage: faSuitcaseRolling,
    guard: faShieldHalved,
    staff: faClipboardCheck,
    iaq: faTemperatureLow,
    humidity: faTint,
    light: faLightbulb,
    pressure: faArrowDown,
    sound: faVolumeUp,
    temperature: faThermometerHalf
  },
  supermarket: {
    user: faUser,
    luggage: faShoppingCart,
    guard: faShieldHalved,
    staff: faClipboardCheck,
    iaq: faTemperatureLow,
    humidity: faTint,
    light: faLightbulb,
    pressure: faArrowDown,
    sound: faVolumeUp,
    temperature: faThermometerHalf
  }
};

/**
 * Base sensor mapping: provides default display names.
 * Expanded to include environment sensors.
 */
const baseSensorMapping: Record<string, { displayName: string, icon: any }> = {
  user: { displayName: "User", icon: faUser },
  luggage: { displayName: "Luggage", icon: faSuitcaseRolling },
  guard: { displayName: "Guard", icon: faShieldHalved },
  staff: { displayName: "Staff", icon: faClipboardCheck },
  iaq: { displayName: "IAQ Sensor", icon: faTemperatureLow },
  humidity: { displayName: "Humidity Sensor", icon: faTint },
  light: { displayName: "Light Sensor", icon: faLightbulb },
  pressure: { displayName: "Pressure Sensor", icon: faArrowDown },
  sound: { displayName: "Sound Sensor", icon: faVolumeUp },
  temperature: { displayName: "Temperature Sensor", icon: faThermometerHalf },
};

/**
 * Reactive state to hold the complete summary from the API.
 */
export const sensorSummaries = ref<Record<string, RoomSummary>>({});

/**
 * Reactive sensor list that consolidates sensor data across rooms.
 * - For non-environment sensors, each item contains:
 *    - room: the room ID
 *    - sensor: the sensor key
 *    - displayName: sensor name (domain overrides applied if available)
 *    - icon: the sensor icon name
 *    - count: number of sensors
 *    - ids: array of sensor/device IDs
 * - For environment sensors, the sensor object includes a "value" property.
 * - For user sensors, we aggregate them across all rooms and return a single sensor object.
 */
export const sensors = ref<any[]>([]);

/**
 * Updates the sensor mappings using the summary API.
 * Fetches data from `/api/reader/summary` and processes each room to extract sensor information.
 */
export const updateSensorMappings = async () => {
  try {
    const response = await axios.get('/api/reader/summary', { withCredentials: true });
    const summaryData = response.data;
    // Store the full summary data.
    sensorSummaries.value = summaryData;
    console.log("Full summary:", sensorSummaries.value);
    
    let newSensors: any[] = [];
    // Aggregator for user sensor (consolidated across all rooms)
    let aggregatedUser = { count: 0, id: [] as string[] };
    
    // Process each room in the summary.
    Object.keys(summaryData).forEach(roomId => {
      const roomSummary: RoomSummary = summaryData[roomId];
      
      // Process non-environment sensors.
      Object.keys(roomSummary).forEach(key => {
        if (key === 'environment') return;
        
        // Check if the key is 'users' (or 'user') — case insensitive.
        if (key.toLowerCase() === 'users' || key.toLowerCase() === 'user') {
          const sensorData = roomSummary[key] as SensorSummary;
          aggregatedUser.count += sensorData.count;
          aggregatedUser.id.push(...sensorData.id);
        } else {
          const sensorData = roomSummary[key] as SensorSummary;
          const defaultName = baseSensorMapping[key]?.displayName || key;
          const overrideName = domainOverrides[currentDomain.value]?.[key]?.[0] || defaultName;
          const displayName = overrideName;
          const icon = domainIcons[currentDomain.value]?.[key] || faTowerBroadcast;
  
          newSensors.push({
            room: roomId,
            sensor: key,
            displayName,
            icon: icon?.iconName || "default-icon",
            count: sensorData.count,
            ids: sensorData.id
          });
        }
      });
      
      // Process environment sensors for each room.
      if (roomSummary.environment) {
        const envData = roomSummary.environment;
        Object.keys(envData).forEach(envKey => {
          const normalizedKey = envKey.toLowerCase();
          const defaultName = baseSensorMapping[normalizedKey]?.displayName || envKey;
          const icon = domainIcons[currentDomain.value]?.[normalizedKey] || faTowerBroadcast;
          newSensors.push({
            room: roomId,
            sensor: normalizedKey,
            displayName: defaultName,
            icon: icon?.iconName || "default-icon",
            // For environment sensors we provide the value directly.
            value: envData[envKey]
          });
        });
      }
    });
        
    sensors.value = newSensors;
    await nextTick();
  } catch (error) {
    console.error("Failed to fetch sensor summary:", error);
  }
};

/**
 * Initialization function.
 * Fetches domain configuration, sets the current domain, and retrieves the latest sensor summary.
 */
export const initializeSensors = async () => {
  await fetchDomainConfig();
  currentDomain.value = domainConfig.value.config.domain.toLowerCase();
  await updateSensorMappings();
};
