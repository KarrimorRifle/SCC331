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