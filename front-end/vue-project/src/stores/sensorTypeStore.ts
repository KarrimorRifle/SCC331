import { ref } from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faUser, faEye, faUsers, faTemperatureLow, faTint, faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf, faSuitcaseRolling } from '@fortawesome/free-solid-svg-icons';
library.add(faUser, faEye, faUsers, faTemperatureLow, faTint, faLightbulb, faArrowDown, faVolumeUp, faThermometerHalf, faSuitcaseRolling);

/**
 * This is the mapping for all the sensors (in the future, can add whatever over here)
 */
export const sensorMapping = {
    "users": { name: "User", icon: faUser },
    "luggage": { name: "Luggage", icon: faSuitcaseRolling },
    "guard": { name: "Guard", icon: faEye },
    "staff": { name: "Staff", icon: faUsers },
    "iaq": { name: "IAQ Sensor", icon: faTemperatureLow },
    "humidity": { name: "Humidity Sensor", icon: faTint },
    "light": { name: "Light Sensor", icon: faLightbulb },
    "pressure": { name: "Pressure Sensor", icon: faArrowDown },
    "sound": { name: "Sound Sensor", icon: faVolumeUp },
    "temperature": { name: "Temperature Sensor", icon: faThermometerHalf },
};

/**
 * This is the list of all the sensors we have, which can be changed when converted to supermarket
 */
export const sensors = ref([
  { name: "users", displayName: sensorMapping["users"].name, icon: sensorMapping["users"].icon.iconName, checked: true, disconnected: true},
  { name: "luggage", displayName: sensorMapping["luggage"].name, icon: sensorMapping["luggage"].icon.iconName, checked: true, disconnected: true},
  { name: "guard", displayName: sensorMapping["guard"].name, icon: sensorMapping["guard"].icon.iconName, checked: true, disconnected: true},
  { name: "staff", displayName: sensorMapping["staff"].name, icon: sensorMapping["staff"].icon.iconName, checked: true, disconnected: true},
  { name: "iaq", displayName: sensorMapping["iaq"].name, icon: sensorMapping["iaq"].icon.iconName, checked: true, disconnected: true},
  { name: "humidity", displayName: sensorMapping["humidity"].name, icon: sensorMapping["humidity"].icon.iconName, checked: true, disconnected: true},
  { name: "light", displayName: sensorMapping["light"].name, icon: sensorMapping["light"].icon.iconName, checked: true, disconnected: true},
  { name: "pressure", displayName: sensorMapping["pressure"].name, icon: sensorMapping["pressure"].icon.iconName, checked: true, disconnected: true},
  { name: "sound", displayName: sensorMapping["sound"].name, icon: sensorMapping["sound"].icon.iconName, checked: true, disconnected: true},
  { name: "temperature", displayName: sensorMapping["temperature"].name, icon: sensorMapping["temperature"].icon.iconName, checked: true, disconnected: true}
]);
