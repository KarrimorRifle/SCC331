#!/bin/bash

echo "Running tests..."

# Wait for MySQL server to be available
/wait-for-it.sh mysql_server 3306 -- echo "MySQL server is up"

# Wait for account_registration service to be available
/wait-for-it.sh account_registration 5001 -- echo "account_registration is up"

# Wait for account_login service to be available
/wait-for-it.sh account_login 5002 -- echo "account_login is up"

# Wait for assets_reader service to be available
/wait-for-it.sh assets_reader 5010 -- echo "assets_reader is up"

# Wait for assets_editor service to be available
/wait-for-it.sh assets_editor 5011 -- echo "assets_editor is up"

# Wait for warning_editor service to be available
/wait-for-it.sh warning_editor 5004 -- echo "warning_editor is up"

# Wait for hardware_editing service to be available
/wait-for-it.sh hardware_editing 5006 -- echo "hardware_editing is up"


# Grab the test target(s) from the first argument (default to "all" if none provided)
TEST_TARGETS=$1
if [ -z "$TEST_TARGETS" ]; then
  TEST_TARGETS="all"
fi

# Split comma-separated targets into an array
IFS=',' read -ra TARGET_ARRAY <<< "$TEST_TARGETS"

# If "all" is in the list, run all tests and exit
if [[ " ${TARGET_ARRAY[*]} " == *" all "* ]]; then
  echo "Running ALL tests..."
  python -m unittest discover -s tests -v
  exit 0
fi

# Otherwise, loop over each target in the array
for TARGET in "${TARGET_ARRAY[@]}"; do
  case "$TARGET" in
    "accounts")
      echo "Running accounts tests..."
      python -m unittest discover -s tests -p "test_1_accounts.py" -v
      ;;
    "assets")
      echo "Running assets tests..."
      python -m unittest discover -s tests -p "test_2_assets.py" -v
      ;;
    "warnings")
      echo "Running warnings tests..."
      python -m unittest discover -s tests -p "test_3_warnings.py" -v
      ;;
    "data")
      echo "Running data tests..."
      python -m unittest discover -s tests -p "test_4_data.py" -v
      ;;
    "hardware_config")
      echo "Running data tests..."
      python -m unittest discover -s tests -p "test_5_hardware_config.py" -v
      ;;
    *)
      echo "Invalid test target: $TARGET"
      echo "Valid targets: all,accounts,assets,warnings,data,hardware_config"
      ;;
  esac
done
