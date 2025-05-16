#!/bin/bash

# Setup environment variables for testing
export SQLITE_TEST_MODE=true
export SGX_MOCK=true
export ETHEREUM_MOCK=true
export CHAOSCORE_ENV=test
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the tests
pytest -v tests/api 