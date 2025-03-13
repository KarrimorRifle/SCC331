import { ref } from 'vue';
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
    guard: ["Guard"],
    staff: ["Staff"],
    iaq: ["IAQ Sensor"],
    humidity: ["Humidity Sensor"],
    light: ["Light Sensor"],
    pressure: ["Pressure Sensor"],
    sound: ["Sound Sensor"],
    temperature: ["Temperature Sensor"]
  },
  supermarket: {
    // For supermarket, we want the canonical default to be the first value:
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
 * Map an incoming readablePicoID to a canonical sensor key.
 * This ensures that names like "Passengers" or "Users" always map to "user".
 */
function mapReadablePicoID(readablePicoID: string): string {
  const normalizedInput = toSingular(readablePicoID.toLowerCase());
  const domainMap = domainOverrides[currentDomain.value] || {};

  for (const canonicalKey in domainMap) {
    const normalizedCanonical = toSingular(canonicalKey.toLowerCase());
    const normalizedOverrides = domainMap[canonicalKey].map(name => toSingular(name.toLowerCase()));
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
 * Reactive sensor mapping and sensor list.
 */
export const sensorMapping = ref<Record<string, Sensor>>({ ...baseSensorMapping });
export const sensors = ref<Sensor[]>([]);

/**
 * Apply domain overrides first.
 * For the "supermarket" domain, force the displayName to be the default override if the current value equals the base default.
 */
const applyDomainOverrides = async () => {
  const overrides = domainOverrides[currentDomain.value] || {};
  const icons = domainIcons[currentDomain.value] || {};
  const updatedMapping: Record<string, Sensor> = {};

  Object.keys(sensorMapping.value).forEach((key) => {
    const currentSensor = sensorMapping.value[key];
    // For supermarket, if the current displayName equals the base default, use the override default.
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
};

/**
 * Fetch and update sensor mappings dynamically from API.
 * We first apply the domain overrides, then merge in API names.
 */
export const updateSensorMappings = async () => {
  try {
    // Apply domain overrides as baseline.
    await applyDomainOverrides();

    const response = await axios.get("/data.json");
    const data: { configs: DeviceConfig[] } = response.data;
    if (!data.configs) return;

    // Start with current mapping (which has domain defaults).
    const updatedMapping: Record<string, Sensor> = { ...sensorMapping.value };

    data.configs.forEach((device: DeviceConfig) => {
      let { readablePicoID, picoType } = device;
      const mappedKey = mapReadablePicoID(readablePicoID);
      if (picoType === 0) return;

      if (!updatedMapping[mappedKey]) {
        updatedMapping[mappedKey] = {
          name: mappedKey,
          displayName: readablePicoID,
          icon: domainIcons[currentDomain.value]?.[mappedKey] || faTowerBroadcast,
          type: picoType,
        };
      } else {
        // If the current displayName is still the default from the override, update it from API.
        const defaultOverride = domainOverrides[currentDomain.value]?.[mappedKey]?.[0] || baseSensorMapping[mappedKey]?.displayName;
        if (updatedMapping[mappedKey].displayName === defaultOverride) {
          updatedMapping[mappedKey].displayName = readablePicoID;
        }
      }
    });

    sensorMapping.value = updatedMapping;
    await applyDomainOverrides();

    sensors.value = Object.entries(sensorMapping.value).map(([key, sensor]) => ({
      name: key,
      displayName: sensor.displayName,
      icon: sensor.icon.iconName,
      checked: true,
      disconnected: true,
      type: sensor.type
    }));
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
  console.log("Sensors:", sensors.value);
};
