import { ref, nextTick } from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faUser, faShoppingCart, faUsers, faTemperatureLow, faTint,
  faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf,
  faSuitcaseRolling, faClipboardCheck, faShieldHalved, faTowerBroadcast
} from '@fortawesome/free-solid-svg-icons';
import { fetchDomainConfig, domainConfig } from '@/constants/HomeConfig';
import axios from 'axios';

library.add(
  faUser, faShoppingCart, faUsers, faTemperatureLow, faTint,
  faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf,
  faSuitcaseRolling, faClipboardCheck, faShieldHalved, faTowerBroadcast
);

/**
 * Interfaces for device configs and sensors.
 */
interface DeviceConfig {
  picoID: string;
  readablePicoID: string;
  picoType: number;
  trackingGroupID: number;
}

interface Sensor {
  /** Canonical key – remains unchanged and used for mapping icons */
  name: string;
  /** Admin‑editable display name; if not modified, defaults to domain override. */
  displayName?: string;
  icon: any; // FontAwesome icon type
  type: number;
}

/**
 * Reactive state for the current domain.
 */
export const currentDomain = ref<string>(domainConfig.value.config.domain.toLowerCase());

/**
 * Domain-specific sensor name overrides.
 * Each key maps to an array of allowed default names.
 */
const domainOverrides: Record<string, Record<string, string[]>> = {
  airport: {
    user: ["User", "Passenger"],
    luggage: ["Luggage"],
    guard: ["Guard", "Security"],
    staff: ["Staff"],
    iaq: ["IAQ Sensor"],
    humidity: ["Humidity Sensor"],
    light: ["Light Sensor"],
    pressure: ["Pressure Sensor"],
    sound: ["Sound Sensor"],
    temperature: ["Temperature Sensor"]
  },
  supermarket: {
    user: ["Customer", "User", "Passenger"],
    luggage: ["Trolley"],
    guard: ["Security"],
    staff: ["Employee"],
    iaq: ["Air Quality Sensor"],
    humidity: ["Humidity Sensor"],
    light: ["Lighting Sensor"],
    pressure: ["Pressure Sensor", "Air Conditioning Sensor"],
    sound: ["Sound Sensor"],
    temperature: ["Temperature Sensor"]
  }
};

/**
 * Domain-specific icons.
 */
const domainIcons: Record<string, Record<string, any>> = {
  airport: {
    user: faUser,
    luggage: faSuitcaseRolling,
    guard: faShieldHalved,
    staff: faClipboardCheck,
    pressure: faArrowDown
  },
  supermarket: {
    user: faUser,
    luggage: faShoppingCart,
    guard: faShieldHalved,
    staff: faClipboardCheck,
    pressure: faThermometerHalf
  }
};

/**
 * Utility: convert a word to its singular form.
 */
function toSingular(word: string): string {
  if (word.endsWith("ies")) return word.slice(0, -3) + "y";
  if (word.endsWith("es") && !["oes", "ses", "xes"].some(suffix => word.endsWith(suffix))) return word.slice(0, -2);
  if (word.endsWith("s") && !word.endsWith("ss")) return word.slice(0, -1);
  return word;
}

/**
 * Utility: extract the canonical part of a sensor name.
 * Instead of simply splitting on '-', we check if the name contains one of the canonical keywords
 * (e.g. "luggage", "user", etc.) and return that keyword.
 */
function extractCanonicalName(name: string): string {
  const lowerName = name.toLowerCase();
  // Check the domainOverrides first.
  const overridesForDomain = domainOverrides[currentDomain.value] || {};
  for (const canonicalKey in overridesForDomain) {
    const allowedNames = overridesForDomain[canonicalKey]?.map(n => n.toLowerCase()) || [];
    for (const allowed of allowedNames) {
      if (lowerName.includes(allowed)) {
        return canonicalKey;
      }
    }
  }
  // Fallback: check base sensor mapping keys.
  for (const key in baseSensorMapping) {
    if (lowerName.includes(key)) {
      return key;
    }
  }
  return name;
}

/**
 * Map an incoming readablePicoID to a canonical sensor key.
 * This ensures that names like "Passengers", "Users", or "luggage-01" always map to "user" or "luggage" respectively.
 */
function mapReadablePicoID(readablePicoID: string): string {
  const baseName = extractCanonicalName(readablePicoID);
  const normalizedInput = toSingular(baseName.toLowerCase());
  const domainMap = domainOverrides[currentDomain.value] || {};

  for (const canonicalKey in domainMap) {
    const normalizedCanonical = toSingular(canonicalKey.toLowerCase());
    const normalizedOverrides = domainMap[canonicalKey]?.map(name => toSingular(name.toLowerCase())) || [];
    if (normalizedInput === normalizedCanonical || normalizedOverrides.includes(normalizedInput)) {
      return canonicalKey;
    }
  }
  return normalizedInput;
}


/**
 * Base sensor mapping (canonical defaults).
 */
const baseSensorMapping: Record<string, Sensor> = {
  user: { name: "user", displayName: "User", icon: faUser, type: 2 },
  luggage: { name: "luggage", displayName: "Luggage", icon: faSuitcaseRolling, type: 2 },
  guard: { name: "guard", displayName: "Guard", icon: faShieldHalved, type: 2 },
  staff: { name: "staff", displayName: "Staff", icon: faClipboardCheck, type: 2 },
  iaq: { name: "iaq", displayName: "IAQ Sensor", icon: faTemperatureLow, type: 1 },
  humidity: { name: "humidity", displayName: "Humidity Sensor", icon: faTint, type: 1 },
  light: { name: "light", displayName: "Light Sensor", icon: faLightbulb, type: 1 },
  pressure: { name: "pressure", displayName: "Pressure Sensor", icon: faArrowDown, type: 1 },
  sound: { name: "sound", displayName: "Sound Sensor", icon: faVolumeUp, type: 1 },
  temperature: { name: "temperature", displayName: "Temperature Sensor", icon: faThermometerHalf, type: 1 }
};

/**
 * Reactive sensor mapping (grouped) and sensor lists.
 */
export const sensorMapping = ref<Record<string, Sensor>>({ ...baseSensorMapping });
export const sensors = ref<Sensor[]>([]);           // Grouped sensors list
export const separatedSensors = ref<Sensor[]>([]);    // Separated (ungrouped) sensor list

/**
 * Group devices from API by canonical key.
 */
function groupDevicesByCanonicalKey(devices: DeviceConfig[]): Record<string, DeviceConfig[]> {
  const groups: Record<string, DeviceConfig[]> = {};
  devices.forEach(device => {
    const baseName = extractCanonicalName(device.readablePicoID);
    const key = mapReadablePicoID(baseName);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(device);
  });
  return groups;
}

/**
 * Merge grouped devices with the base sensor mapping.
 * If more than one device exists in a group, append the count to the displayName.
 */
function updateSensorMappingWithGroups(groups: Record<string, DeviceConfig[]>): Record<string, Sensor> {
  const newMapping: Record<string, Sensor> = { ...baseSensorMapping };
  for (const key in groups) {
    const devices = groups[key];
    const count = devices.length;
    const defaultName = domainOverrides[currentDomain.value]?.[key]?.[0] || baseSensorMapping[key]?.displayName || key;

    const displayName = count > 1 ? `${defaultName} (${count})` : devices[0]?.readablePicoID || defaultName;
    const icon = domainIcons[currentDomain.value]?.[key] || baseSensorMapping[key]?.icon || faTowerBroadcast;
    const type = devices[0]?.picoType;

    newMapping[key] = {
      name: key,
      displayName,
      icon,
      type,
    };
  }
  return newMapping;
}

/**
 * Map each device config individually (ungrouped) into a Sensor.
 */
function mapDeviceToSensor(device: DeviceConfig): Sensor {
  const baseName = extractCanonicalName(device.readablePicoID);
  const canonicalKey = mapReadablePicoID(baseName);
  return {
    name: canonicalKey,
    displayName: device.readablePicoID,
    icon: domainIcons[currentDomain.value]?.[canonicalKey] || faTowerBroadcast,
    type: device.picoType,
  };
}

/**
 * Apply domain overrides.
 * For the "supermarket" domain, if the current displayName equals the base default,
 * then use the override default.
 */
const applyDomainOverrides = async () => {
  const overrides = domainOverrides[currentDomain.value] || {};
  const icons = domainIcons[currentDomain.value] || {};
  const updatedMapping: Record<string, Sensor> = {};

  Object.keys(sensorMapping.value).forEach((key) => {
    const currentSensor = sensorMapping.value[key];
    updatedMapping[key] = {
      name: currentSensor.name,
      displayName:
        currentDomain.value === 'supermarket'
          ? (currentSensor.displayName === baseSensorMapping[key].displayName
               ? (overrides[key]?.[0] || currentSensor.name)
               : currentSensor.displayName)
          : (currentSensor.displayName || (overrides[key]?.[0] || currentSensor.name)),
      icon: icons[key] || currentSensor.icon,
      type: currentSensor.type
    };
  });
  sensorMapping.value = updatedMapping;
  await nextTick();
};

/**
 * Fetch and update sensor mappings dynamically from API.
 * We update two lists:
 *  - "separatedSensors": each device mapped individually.
 *  - "sensors": grouped by canonical key with counts appended.
 */
export const updateSensorMappings = async () => {
  try {
    const response = await axios.get("/api/hardware/get/device/configs", { withCredentials: true });
    const data: { configs?: DeviceConfig[] } = response.data;    
    if (!data.configs || !Array.isArray(data.configs) || data.configs.length === 0) {
      console.warn("No device configs found, skipping update.");
      return;
    }

    console.log("Fetched configs:", data.configs);

    separatedSensors.value = data.configs.map(device => mapDeviceToSensor(device));
    console.log("Separated Sensors:", separatedSensors.value);

    const groups = groupDevicesByCanonicalKey(data.configs);
    console.log("Grouped Devices:", groups);

    const newMapping = updateSensorMappingWithGroups(groups);
    sensorMapping.value = newMapping;

    await applyDomainOverrides();

    sensors.value = Object.entries(sensorMapping.value).map(([key, sensor]) => ({
      name: key,
      displayName: sensor.displayName,
      icon: sensor.icon?.iconName || "default-icon",
      checked: true,
      disconnected: true,
      type: sensor.type
    }));

    console.log("Final Grouped Sensors:", sensors.value);
  } catch (error) {
    console.error("Failed to fetch sensor mappings:", error);
  }
};

/**
 * Initialization function.
 */
export const initializeSensors = async () => {
  await fetchDomainConfig();
  currentDomain.value = domainConfig.value.config.domain.toLowerCase();
  await updateSensorMappings();
  console.log("Initialized Domain:", currentDomain.value);
  console.log("Grouped Sensors after initialization:", sensors.value);
  console.log("Separated Sensors after initialization:", separatedSensors.value);
};
