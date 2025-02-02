# Accounts
## registration
port: 5001
### POST: `/register`
- **Headers:**
  - `name`: Full name of the user (required)
  - `email`: Email of the user (required, must end with '@fakecompany.co.uk')
  - `password`: Password of the user (required)
- **Responses:**
  - `201`: User registered successfully
  - `400`: Missing or invalid fields
  - `500`: Database connection failed or other server error

## login
port: 5002
### POST: `/login`
- **Headers:**
  - `email`: Email of the user (required)
  - `password`: Password of the user (required)
- **Responses:**
  - `200`: Login successful, sets a `session_id` cookie
  - `400`: Missing email or password
  - `401`: Invalid email or password
  - `500`: Database connection failed or other server error

### GET: `/validate_cookie`
- **Headers or Cookies:**
  - `session-id`: Session ID cookie (required)
- **Responses:**
  - `200`: Cookie is valid, returns user email
  - `400`: No session cookie or header provided
  - `401`: Invalid cookie
  - `500`: Database connection failed or other server error

# Data
## Warning System
The warning system will utilise the MQTT server to communicate and will send messages in this format:
```JSON
{
  "Title": "A string with the name of the warning",
  "Location": "RoomID",
  "Severity": "ENUM['doomed','danger','warning','notification']",
  "Summary": "String with summary"
}
```

### Authorisation and Topics utilised
\# will be used as the warning ID
- Staff seniors only: `warning/senior/#`
- Staff only: `warning/staff/#`
- Everyone: `warning/everyone/#`

Warnings can range from telling staff there is a lack of people in a room, too many people in a room, or fires are going etc.

## processing
All messages are to be sent through the MQTT server on topic: `feeds/hardware-data/#`

Format is as follows:
```JSON
{
  "PicoID": <int>,
  "RoomID": <int>,
  "PicoType": <int>,
  "Data": <int | CSV String>
}
```
For PicoType 1 (rooms):
  Data is CSV string where: "<Sound>,<Light>,<temp>"

For PicoType 2 (luggage) & 3 (Users):
  Data variable is currently negligible

## Reader
port: 5003

### GET: `/pico/<int:PICO>`
- **Headers:**
  - `session-id`: Session ID cookie (required)
- **Responses:**
  - `200`: Returns the most recent session logs for the specified PicoID
    - **Example:**
      ```json
      [
        {
          "roomID": 1,
          "logged_at": "2023-10-01T12:00:00Z"
        },
        {
          "roomID": 2,
          "logged_at": "2023-10-01T12:05:00Z"
        }
      ]
      ```
  - `401`: Invalid cookie
  - `404`: No session found for the specified PicoID
  - `500`: Database connection failed or other server error

### GET: `/summary`
- **Headers:**
  - `session-id`: Session ID cookie (required)
- **Responses:**
  - `200`: Returns a summary of the current state of all rooms
    - **Example:**
      ```json
      {
        "1": {
          "users": {
            "count": 2,
            "id": [101, 102]
          },
          "luggage": {
            "count": 1,
            "id": [201]
          },
          "environment": {
            "temperature": 22.5,
            "sound": 45.3,
            "light": 300,
            "IAQ": 50.0,
            "pressure": 1013.25,
            "humidity": 40.0
          }
        },
        "2": {
          "users": {
            "count": 1,
            "id": [103]
          },
          "luggage": {
            "count": 2,
            "id": [202, 203]
          },
          "environment": {
            "temperature": 23.0,
            "sound": 50.1,
            "light": 320,
            "IAQ": 55.0,
            "pressure": 1012.50,
            "humidity": 42.0
          }
        }
      }
      ```
  - `401`: Invalid cookie
  - `500`: Database connection failed or other server error
