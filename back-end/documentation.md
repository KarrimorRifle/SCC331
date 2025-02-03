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

For PicoType 4 (staff) & 5 (guard):
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
          "staff": {
            "count": 1,
            "id": [301]
          },
          "guard": {
            "count": 1,
            "id": [401]
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
          "staff": {
            "count": 2,
            "id": [302, 303]
          },
          "guard": {
            "count": 1,
            "id": [402]
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
