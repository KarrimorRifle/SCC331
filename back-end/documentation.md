# Accounts
## registration
port: 5001
### POST: `/register`
- **Headers:**
  - `name`: Full name of the user (required)
  - `email`: Email of the user (required, must end with '@fakecompany.co.uk')
  - `password`: Password of the user (required)
  - `super`: If set to "yes" will set the user to super admin
  - `bypass`: If set to "yes" will set the user to admin
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
  - `200`: Login successful, sets a `session_id` cookie and returns:
    ```json
    {
      "message": "Login successful",
      "expires": "2024-01-01T12:00:00Z"
    }
    ```
  - `400`: Missing email or password
  - `401`: Invalid email or password
  - `500`: Database connection failed or other server error

### GET: `/validate_cookie`
- **Headers or Cookies:**
  - `session-id`: Session ID cookie (required)
- **Responses:**
  - `200`: Cookie is valid, returns user: `email`, `authority`, `uid` 
  - `400`: No session cookie or header provided
  - `401`: Invalid cookie
  - `500`: Database connection failed or other server error

### POST: `/refresh_cookie`
- **Headers or Cookies:**
  - `session-id`: Session ID cookie (required)
- **Responses:**
  - `200`: Cookie refreshed, sets a new `session_id` cookie and returns:
    ```json
    {
      "message": "Cookie refreshed",
      "expires": "2024-01-01T12:00:00Z"
    }
    ```
  - `400`: No session cookie or header provided
  - `401`: Invalid session
  - `500`: Database connection failed or other server error

### POST: `/logout`
- **Headers or Cookies:**
  - `session-id`: Session ID cookie (required)
- **Responses:**
  - `200`: Logout successful, removes `session_id` cookie
  - `400`: No session cookie or header provided
  - `500`: Database connection failed or other server error

### GET: `/get_users`
- **Headers or Cookies:**
  - `session-id`: Session ID cookie (required)
- **Responses:**
  - `200`: Returns a list of users (requires admin authority)
    - **Example:**
      ```json
      {
        "users": [
          {
            "uid": 1,
            "email": "user1@fakecompany.co.uk",
            "name": "User One"
          },
          {
            "uid": 2,
            "email": "user2@fakecompany.co.uk",
            "name": "User Two"
          }
        ]
      }
      ```
  - `400`: No session cookie or header provided
  - `401`: Unauthorized access or insufficient permission
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
  Data is CSV string where: "<Sound>,<Light>,<temp>,<IAQ>,<Pressure>,<Humidity>"

For PicoType 2 (luggage) & 3 (Users):
  Data variable is currently negligible

For PicoType 4 (staff) & 5 (guard):
  Data variable is currently negligible

## Reader
port: 5003

### GET: `/pico/<string:PICO>`
- **Description:** Gets session of Pico ID where the time is in ISO 8601 format.
- **Headers:**
  - `session-id`: Session ID cookie (required)
- **Request:**
  - `time`: Select time in which the period covers
- **Responses:**
  - `200`: Returns the most recent session logs for the specified PicoID
    - **Example:**
      ```json
      {
        "type": "guard | staff | user | luggage",
        "movement": {
          "2023-10-01T12:00:00Z": "RoomID",
          // ... More entries
        }
      }
      ```
  - `401`: Invalid cookie
  - `404`: No session found for the specified PicoID
  - `500`: Database connection failed or other server error

### GET: `/summary`
- **Headers:**
  - `session-id`: Session ID cookie (required)
- **Request:**
  - `time`: Time in which you want to get the exact data for (optional)
  - `mode`: ENUM: "all" | "picos" | "environment": grabd either all the data, pico data or environment data (optional)
- **Responses:**
  - `200`: Returns a summary of the current state of all rooms
    - **Example:**
      ```json
      {
        "1": {
          "users": {
            "count": 2,
            "id": ["101", "102"]
          },
          "luggage": {
            "count": 1,
            "id": ["201"]
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
            "id": ["103"]
          },
          "luggage": {
            "count": 2,
            "id": ["202", "203"]
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

### GET: `/summary/average`
- **Headers:**
  - `session-id`: Session ID cookie (required)
  - `time_start`: Start time for the summary (optional)
  - `time_end`: End time for the summary (optional)
- **Request:**
  ```json
  {
    "start_time": "startTime", // if not provided past 24 hours will be given
    "end_time": "endtime", // if not provided will provide up to present
    "time_periods": "1hr", // defaults to one hour, will select the times to average
    "rooms": ["20", "49"] // IF NOTHING or EMPTY will send everything
  }
  ```
- **Responses:**
  - `200`: Returns a summary of the average state of all rooms
    - **Example:**
      ```json
      {
        "2023-01-01T20:20:20Z": {
          "roomID": { // Room ID
            "users": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "luggage": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "guards": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "staff": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "light": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "IAQ": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "temperature": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "sound": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "pressure": {
              "average": 20,
              "peak": 45,
              "trough": 10
            },
            "humidity": {
              "average": 20,
              "peak": 45,
              "trough": 10
            }
          }
          // ... More room IDs
        }
        // ... More Times
      }
      ```
  - `400`: Invalid request parameters
  - `401`: Unauthorized
  - `500`: Database connection failed or other server error

### GET: `/movement`
- **Headers:**
  - `session-id`: Session ID cookie (required)
  - `time_start`: Start time for the movement data (optional) // will give past 3 hours if not given
  - `time_end`: End time for the movement data (optional)
- **Responses:**
  - `200`: Returns a list of movements
    - Time data will be per minute
    - **Example:**
      ```json
      {
        "2023-01-01T20:20:20Z": {
          "roomID1": {
            "PicoID1": "Staff",
            "PicoID2": "Luggage"
          },
          "roomID2": {
            "PicoID3": "User",
            "PicoID4": "Guard"
          }
          // ... More room IDs
        }
        // ... More Times
      }
      ```
  - `400`: Invalid request parameters
  - `401`: Unauthorized
  - `500`: Database connection failed or other server error

# Warning System
The warning system will utilise the MQTT server to communicate and will send messages in this format:
```JSON
{
  "Title": "A string with the name of the warning",
  "Location": "RoomID",
  "Severity": "ENUM['doomed','danger','warning','notification']",
  "Summary": "String with summary",
  "ID": 302, // ID of the warning
}
```

## Authorisation and Topics utilised
\# will be used as the warning ID
- Staff admins only: `warnings/admin`
- Staff security only: `warnings/security`
- Staff only: `warnings/staff`
- Users only: `warnings/users`'
- Everyone: `warninsg/everyone`

Warnings can range from telling staff there is a lack of people in a room, too many people in a room, or fires are going etc.
## Editor (Port: 5004)
This service will allow admins of the page to add new rules that will activate messages

### Endpoints

#### Get warnings
- **GET**: `/warnings`
- **Cookies:**
  - `session_id`: Valid Admin session
- **Responses**:
  - `200`:
    -
    ```json
    [
      {
        "id": 38, //id of the rule
        "name": "string",
        "rooms": ["12dawd", "42afwafaw"], // All room id's involved with this rule
        "messages": [
          {
            "title": "string",
            "authority": "admin" // ONE OF admin, security, staff, users, everyone
          }
          // ... More message summaries
        ],
        "last_test": {
          "type": "full | messages | none",
          "status": "success | failure" // if none status will be failure
        }
      }
      // ... More warning rule summaries
    ]
    ```
  - `401`: Unauthorized.
  - `500`: Server error.

#### Get warning
- **GET**: `/warnings/<id>`
- **Cookies:**
  - `session_id`: Valid Admin session
- **Responses:**
  - `200`: Warning details.
    - 
    ```json
    {
      "name": "string", // needs to be a unique name
      "id": 20,
      "conditions": [
        {
          "roomID": "valid room id",
          "conditions": [
            {
              "variable": "temperature | UAQ | light etc...", //valid room variable
              "lower_bound": 19, //lower bound number for activation (inclusive)
              "upper_bound": 50, //upper bound number for activation (inclusive)
            },
            // ... additional variables to check, will work as "AND"
          ]
        }
        // ... additional variables to check in each room, will work as "AND"
      ],
      "messages": [
        {
          "Authority": "admin | security | staff | users | everyone", // Sends message to respective channel
          "Title": "A string with the name of the warning",
          "Location": "RoomID",
          "Severity": "ENUM['doomed','danger','warning','notification']",
          "Summary": "String with summary"
        }
        // ... Additional messages to send out at the same time
      ],
      "last_test": {
        "type": "full | messages | none",
        "status": "success | failure" // if none status will be failure
      }
    }
    ```
  - `401`: Unauthorized.
  - `500`: Server error.

#### Create Warning
- **POST:** `/warnings`
- **Cookies:**
  - `session_id`: Valid Admin session
- **Request Body (JSON)**
  ```json
  {
    "name": "name of the warning", // has to be a unique name
    "test_only": true, //(NOT REQUIRED) Boolean value of whether this is for testing only or not
  }
  ```
- **Responses:**
  - `201`: Warning created.
    - ```json
      {
        "message": "Successfully created rule",
        "id": 29 //ID of the newly created warning
      }
      ```
  - `400`: Invalid warning data.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Update Warning
- **PATCH:** `/warnings/<id>`
  - `id`: id of the warning rule you want to change
- **Cookies:**
  - `session_id`: Valid Admin session
- **Request Body (JSON)**
  ```json
  {
    "name": "string", // needs to be a unique name
    "conditions": [
      {
        "roomID": "valid room id",
        "conditions": [
          {
            "variable": "temperature | UAQ | light etc...", //valid room variable
            "lower_bound": 19, //lower bound number for activation (inclusive)
            "upper_bound": 50, //upper bound number for activation (inclusive)
          },
          // ... additional variables to check, will work as "AND"
        ]
      }
      // ... additional variables to check in each room, will work as "AND"
    ],
    "messages": [
      {
        "Authority": "admin | security | staff | users | everyone", // Sends message to respective channel
        "Title": "A string with the name of the warning",
        "Location": "RoomID",
        "Severity": "ENUM['doomed','danger','warning','notification']",
        "Summary": "String with summary"
      }
      // ... Additional messages to send out at the same time
    ]
  }
  ```
- **Responses:**
  - `200`: Warning updated.
    - ```json
      {
        "message": "Successfully updated rule",
      }
      ```
  - `400`: Invalid warning data.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Delete Warning
- **DELETE**: `/warnings/<id>`
  - `id`: id of the warning rule you want to delete
- **Cookies:**
  - `session_id`: Valid Admin session
- **Responses:**
  - `200`: Warning deleted.
    - ```json
      {
        "message": "Successfully deleted rule",
      }
      ```
  - `400`: Invalid rule id.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Test Warning
- **POST:** `/warnings/test`
- **Cookies:**
  - `session_id`: Valid Admin session
- **Request Body (JSON):**
  ```json
  {
    "id": 29, // ID of the warning rule to test
    "mode": "full | messages" // How you want the test to occur, test everything including the environment variables or just message sending
  }
  ```
- **Responses:**
  - `200`: Test successfully queued.
    ```json
    {
      "message": "Test queued successfully",
      "test_id": 39 //ID of the test queued
    }
    ```
  - `400`: Invalid warning ID.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Get Test Results
- **GET:** `/warnings/test/result/<id>`
  - `id`: id of the test you want to grab
- **Cookies:**
  - `session_id`: Valid Admin session
- **Responses:**
  - `200`: Returns the result of the last test.
    ```json
    {
      "id": 29, // ID of the warning rule
      "type": "full | messages",
      "status": "success | failure",
      "result": "Conditions met | Conditions not met | Messages sent",
      "environment": {
        "ifhawifw": [// The room ID
          {
            "variable": "name of the variable", // For counts, just use the name for the count e.g. "users", "luggage"
            "value_read": 30, //what we read at the time
            "upper_bound": 40, // Upper bound activation
            "lower_bound": 35, // lower bound activation
          },
          // ... other variables read for that room
        ]
      },
      "messages": [
        {
          "Authority": "admin | security | staff | staff | everyone", // Sends message to respective channel
          "Title": "A string with the name of the warning",
          "Location": "RoomID",
          "Severity": "ENUM['doomed','danger','warning','notification']",
          "Summary": "String with summary"
        }
        // ... Additional messages to send out at the same time
      ]
    }
    ```
  - `400`: Invalid warning ID.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Get Logs
- **GET:** `/warnings/logs`
- **Cookies:**
  - `session_id`: Valid Admin session
- **Responses:**
  - `200`: Returns a list of logs.
    ```json
    [
      {
        "id": 39, //Rule id,
        "name": "ruleSet name",
        "timestamp": "2023-10-01T12:00:00Z",
        "variables": {
          "temperature": {
            "value": 20,
            "upper_bound": 25,
            "lower_bound": 19,
          },
          "users": {
            "value": 50,
            "lower_bound": 50,
            "upper_bound": 900,
          },
          // ... more environment variables
        }, 
        "messages": [
          {
            "Authority": "admin | security | staff | staff | everyone", // Sends message to respective channel
            "Title": "A string with the name of the warning",
            "Location": "RoomID",
            "Severity": "ENUM['doomed','danger','warning','notification']",
            "Summary": "String with summary"
          }
          // ... Additional messages to send out at the same time
        ]
      }
      // ... more logs ...
    ]
    ```
  - `401`: Unauthorized.
  - `500`: Server error.

#### Acknowledge Warning
- **POST:** `/warnings/<id>/acknowledge`
  - `id`: id of the warning rule to acknowledge
- **Cookies:**
  - `session_id`: Valid session
- **Request Body (JSON)**
  ```json
  {
    "response": "acknowledged | denied | ignored"
  }
  ```
- **Responses:**
  - `200`: Response sent.
    ```json
    {
      "message": "Response sent"
    }
    ```
  - `400`: Invalid warning ID.
  - `401`: Unauthorized.
  - `500`: Server error.
- **Message:**
  - MQTT response on channel `response/#` where # is the ruleID
    ```json
    {
      "response": "acknowledged | denied | ignored",
      "name": "Lissandra Winter", // Name of user responding
      "medium": "Web" // response method
    }
    ```

# Assets

## Assets Editor Microservice (Port: 5011)
This service handles the creation, modification, and deletion of asset presets, boxes, and related images. Endpoints below require a valid `session_id` cookie with admin privileges.

### Endpoints

#### Create Preset
- **POST:** `/presets`
- **Cookies:**  
  - `session_id`: Valid admin session.
- **Request Body (JSON):**
  ```json
  {
    "name": "Preset Name",
    "trusted": [203, 01]
  }
  ```
- **Responses:**
  - `201`: Preset created.
  - `400`: Invalid preset data.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Upload Preset Image
- **POST:** `/presets/<preset_id>/image`
- **Cookies:**  
  - `session_id`: Valid admin session.
- **Request Body (JSON):**
  ```json
  {
    "name": "Image Name",
    "data": "Base64 encoded image data"
  }
  ```
- **Responses:**
  - `201`: Image uploaded.
  - `400`: Invalid image data.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Patch Boxes in Preset
- **PATCH:** `/presets/<preset_id>/boxes`
- **Cookies:**  
  - `session_id`: Valid admin session.
- **Request Body (JSON):**
  ```json
  {
    "boxes": [
      {
        "roomID": "Room ID",
        "label": "Display label",
        "top": "Top position in pixels",
        "left": "Left position in pixels",
        "width": "Box width in pixels",
        "height": "Box height in pixels",
        "colour": "#HEX"
      }
      // ... additional boxes ...
    ]
  }
  ```
- **Responses:**
  - `200`: Boxes updated successfully.
  - `400`: Invalid data.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Update Preset
- **PATCH:** `/presets/<preset_id>`
- **Cookies:**
  - `session_id`: Valid admin session.
- **Request Body (JSON):**
  ```json
  {
    "name": "New Preset Name",
    "trusted": [019, 380, 28]
  }
  ```
- **Responses:**
  - `200`: Preset updated.
  - `400`: Invalid data.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Delete Preset
- **DELETE:** `/presets/<preset_id>`
- **Cookies:**
  - `session_id`: Valid session of the preset owner.
- **Responses:**
  - `200`: Preset deleted.
  - `400`: Invalid preset ID.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Set Default Preset
- **PATCH:** `/presets/default`
- **Cookies:**  
  - `session_id`: Valid admin session.
- **Request Body (JSON):**
  ```json
  {
    "preset_id": <preset_id>
  }
  ```
- **Responses:**
  - `200`: Default preset updated.
  - `400`: Invalid preset ID.
  - `401`: Unauthorized.
  - `500`: Server error.

#### Set front page
Note that all items need to be present, if something is missing, that is what will be returned on the get
- **PATCH:** `/home`
- **Cookies:**
  - `session_id`: Valid "Super Admin" session
- **Request Body (JSON):**
  ```json
  {
    "config": {
      "domain": "string",
      "loginText": "Image description",
      "hero": {
        "title": "title of the stuff",
        "subtitle": "Description",
        "image": {
          "name": "Name of image.jpg",
          "data": "adiabfwafbawu==" // BASE64 image
        }
      }
    },
    "features": [
      {
        "icon": "validFontAwesomeIcon",
        "title": "feature title",
        "description": "Description of said title"
      },
      //... More of this
    ],
    "howItWorks": [
      {
        "step": 1, //Number
        "title": "title of the step",
        "description": "udbaudiwaifiaifawifhiwa"
      },
      // ... More of this
    ],
    "theme": {
      "primaryDarkBg": "#003865",
      "primaryDarkText": "#003865",
      "primarySecondaryBg": "lightgray",
      "primarySecondaryText": "lightgray",
      "primaryLightBg": "white",
      "primaryLightText": "white",
      "accent": "#FFD700",
      "accentHover": "#E6C200"
    }
  }
  ```
- **Responses:**
  - `200`: Front page updated.
  - `401`: Unauthorized.
  - `500`: Server error.

## Assets Reader Microservice (Port: 5010)
This service is dedicated to delivering asset preset details to staff users. Its endpoints require a valid `session_id` cookie with appropriate staff privileges.

### Endpoints

#### List Presets
- **GET:** `/presets`
- **Cookies:**
  - `session_id`: Valid staff session.
- **Responses:**
  - `200`: Returns a JSON array of presets (preset ID and name).
    ```json
    {
      "default": "presetID",
      "presets": [
        {
          "name": "name",
          "id": "int"
        },
        ...
      ]
    }
    ```
  - `401`: Unauthorized.
  - `500`: Server error.

#### Get Preset Details
- **GET:** `/presets/<preset_id>`
- **Cookies:**
  - `session_id`: Valid staff session.
- **Responses:**
  - `200`: Returns a JSON object with details for the specified preset. Example:
    ```json
    {
      "id": 123,
      "name": "Office Layout",
      "trusted": [01, 02, 03], //UIDs
      "boxes": [
        {
          "roomID": "101",
          "label": "Reception",
          "top": 50,
          "left": 100,
          "width": 200,
          "height": 150,
          "colour": "#FF5733"
        },
        {
          "roomID": "102",
          "label": "Conference",
          "top": 220,
          "left": 80,
          "width": 180,
          "height": 140,
          "colour": "#33A2FF"
        }
      ],
      "image": {
        "name": "background.png",
        "data": "Base64EncodedString"
      },
      "permission": "read"
    }
    ```
  - `400`: Invalid preset ID.
  - `401`: Unauthorized.
  - `404`: Preset not found.
  - `500`: Server error.

#### Get front page
- **GET:** `/home`
- **Cookies:**
  - `session_id`: Valid cookie session
- **Request Body (JSON):**
  ```json
  {
    "config": {
      "domain": "string",
      "loginText": "Image description",
      "hero": {
        "title": "title of the stuff",
        "subtitle": "Description",
        "image": {
          "name": "Name of image.jpg",
          "data": "adiabfwafbawu==" // BASE64 image
        }
      }
    },
    "features": [
      {
        "icon": "validFontAwesomeIcon",
        "title": "feature title",
        "description": "Description of said title"
      },
      //... More of this
    ],
    "howItWorks": [
      {
        "step": 1, //Number
        "title": "title of the step",
        "description": "udbaudiwaifiaifawifhiwa"
      },
      // ... More of this
    ],
    "theme": {
      "primaryDarkBg": "#003865",
      "primaryDarkText": "#003865",
      "primarySecondaryBg": "lightgray",
      "primarySecondaryText": "lightgray",
      "primaryLightBg": "white",
      "primaryLightText": "white",
      "accent": "#FFD700",
      "accentHover": "#E6C200"
    }
  }
  ```
- **Responses:**
  - `200`: Front page retrieved.
  - `401`: Unauthorized.
  - `500`: Server error.