.PHONY: run test test-verbose lint format clean

# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
UVICORN = uvicorn
PYTEST = pytest
ISORT = isort
BLACK = black
MYPY = mypy
FLAKE8 = flake8

# Main commands
run:
	$(UVICORN) api_gateway.main:app --reload

run-prod:
	$(UVICORN) api_gateway.main:app --host 0.0.0.0 --port 8000

test:
	$(PYTEST) tests/api/

test-verbose:
	$(PYTEST) -v tests/api/

lint:
	$(FLAKE8) api_gateway/
	$(MYPY) api_gateway/

format:
	$(ISORT) api_gateway/
	$(BLACK) api_gateway/

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install dependencies
install:
	$(PIP) install -e .[dev]

install-dev:
	$(PIP) install -e .[dev]
	$(PIP) install -r requirements-dev.txt

# Generate RSA key pair for testing
generate-keys:
	mkdir -p keys
	openssl genpkey -algorithm RSA -out keys/agent_private.pem -pkeyopt rsa_keygen_bits:2048
	openssl rsa -pubout -in keys/agent_private.pem -out keys/agent_public.pem
	@echo "RSA key pair generated in the 'keys' directory"

# Help
help:
	@echo "Available commands:"
	@echo "  run              Run the API Gateway in development mode"
	@echo "  run-prod         Run the API Gateway in production mode"
	@echo "  test             Run tests"
	@echo "  test-verbose     Run tests with verbose output"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code"
	@echo "  clean            Clean temporary files"
	@echo "  install          Install the package"
	@echo "  install-dev      Install development dependencies"
	@echo "  generate-keys    Generate RSA key pair for testing"
	@echo "  help             Display this help message" 