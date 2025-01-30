# Back-end
Welcome to the back end, we are running a micro service architecture with minimum trust, with a container per service and one account per each container with the minimum permissions to run its service.

## Services:

Accounts:
- Registration
- Login / Authentication

## Running the backend
### Make sure docker is installed
You will be required to have docker desktop installed. Make an account and make sure docker desktop is running before proceeding

### Run the following commands
Within `back-end` run:
- `docker-compose build`: this will build the images so you can run the containers
- `docker-compose up -d`: this will spin up the containers in detached mode, allowing you to continue using your terminal

The tests will be ran on boot, first test should fail if this isnt the first time spinning up the containers

### Stopping the containers
To stop the containers, run:
- `docker-compose down`: this will stop and remove the containers

### Running the tests
Make sure the shell scripts are all in LF format and not CRLF

If you want to run all tests make sure the containers and volumes are deleted.
Build the containers then spin up the containers.

If you want to just test whilst containers are up use:
- `docker-compose run test`: this will run the tests in the `test` service

The first test on the `test_accounts.py` should fail if the volume wasnt refreshed

## Creating new tests
Create a new file under format of `test_<service>.py`
Import `requests` and `unittest` then follow the required format within `test_accounts.py` to test your items

If ordering is important make sure to call the test function `test_<order>_<name>`
all functions need to start with `test`

within the `run_tests.sh` add your dependent services there, otherwise the test may not go as expected.