# Sensors JSON Output Documentation

## User_Luggage_Sensor

### JSON Structure
The `User_Luggage_Sensor` sends the following JSON structure to the server:

```json
{
  "PicoID": 2,
  "RoomID": <int>,  // The major ID of the strongest BLE signal detected
  "PicoType": 2,    // 2 indicates luggage, 3 indicates user
  "Data": <int>     // The major ID of the strongest BLE signal detected
}
```

### Example
```json
{
  "PicoID": 2,
  "RoomID": 1,
  "PicoType": 2,
  "Data": 1
}
```

## Room_Sensor

### JSON Structure
The `Room_Sensor` sends the following JSON structure to the server:

```json
{
  "PicoID": 1,
  "RoomID": 1,
  "PicoType": 1,
  "Data": "<Sound>,<Light>,<Temperature>"  // CSV string with sound, light, and temperature readings
}
```

### Example
```json
{
  "PicoID": 1,
  "RoomID": 1,
  "PicoType": 1,
  "Data": "45.3,300,22.5"
}
```
