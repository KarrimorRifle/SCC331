# Back-end

Welcome to the back end. We are running a micro service architecture with minimum trust—one container per service and one account per container with the minimum permissions required to run its service.

## Services

**Accounts:**
- Registration
- Login / Authentication
- Messages

**Warnings:**
- Editor (Allows rule creation)
- Processor (sends messages)

**Data:**
- Processor (Grabs data from MQTT topic)
- Reader (Allows user to grab data)

**Assets:**
- Editor (Allows editing, admin access only)
- Reader (Allows anyone to read the data with valid cookie)

## Running the Backend

### Prerequisites

- **Docker**: Make sure Docker Desktop is installed and running. Create an account if needed.

### Build and Run the Containers

Within the `back-end` directory, run:

- **Build the images:**
  ```bash
  docker-compose build
  ```
- **Spin up the containers in detached mode:**
  ```bash
  docker-compose up -d
  ```

> **Note:** The test service is now configured to not run automatically on boot. It is built along with the rest of the services but will only run when you explicitly invoke it.

### Stopping the Containers

To stop and remove the containers, run:
```bash
docker-compose down
```

## Running the Tests

Tests will not run automatically when the containers start. Instead, you can run tests on demand using the test service.
Tests need to be build before running:

```bash
docker-compose build test
```

### Running Tests On Demand

The `test` service uses a modular test runner script (`run_tests.sh`) that allows you to select which tests to run. The script accepts a comma-separated list of test targets. Available targets include:
- `accounts`
- `assets`
- `warnings`
- `data`
- `all` (to run every test)

For example, to run tests:

- **Run all tests:**
  ```bash
  docker-compose run test all
  ```

- **Run only accounts tests:**
  ```bash
  docker-compose run test accounts
  ```

- **Run multiple test groups (e.g., accounts and assets):**
  ```bash
  docker-compose run test accounts,assets
  ```

The test runner script also includes wait-for-service commands (using `wait-for-it.sh`) to ensure that dependent services (such as MySQL, account registration, account login, assets, and warnings) are up before executing tests.

## Creating New Tests

- Create a new test file following the naming format: `test_<service>.py`.
- Import `requests` and `unittest` and follow the structure used in `test_accounts.py` for your tests.
- If test ordering is important, name your test functions using the format: `test_<order>_<name>` (all test function names must start with `test`).
- **Remember to update the `run_tests.sh` script** with any new targets and their corresponding dependent services to ensure the tests run correctly.