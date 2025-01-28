#!/bin/bash

echo "Running tests..."

# Wait for MySQL server to be available
/wait-for-it.sh mysql_server 3306 -- echo "MySQL server is up"

# Wait for account_registration service to be available
/wait-for-it.sh account_registration 5001 -- echo "account_registration is up"

# Wait for account_login service to be available
/wait-for-it.sh account_login 5002 -- echo "account_login is up"

# Run the tests with verbose output
python -m unittest discover -s tests -v