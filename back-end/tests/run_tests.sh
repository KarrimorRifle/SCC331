#!/bin/bash

echo "Running tests..."

# Wait for MySQL server to be available
/wait-for-it.sh mysql_server 3306 -- echo "MySQL server is up"

# Wait for account_registration service to be available
/wait-for-it.sh account_registration 5001 -- echo "account_registration is up"

# Wait for account_login service to be available
/wait-for-it.sh account_login 5002 -- echo "account_login is up"

# Wait for asset_reader service to be available
/wait-for-it.sh assets_reader 5010 -- echo "asset_reader is up"

# Wait for asset_editor service to be available
/wait-for-it.sh assets_editor 5011 -- echo "asset_editor is up"

# Run the tests with verbose output
python -m unittest discover -s tests -v