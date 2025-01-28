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
  "Temperature": <int>  // The current temperature reading
}
```

### Example
```json
{
  "Temperature": 25
}
```
