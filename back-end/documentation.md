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
