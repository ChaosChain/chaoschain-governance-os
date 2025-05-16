#!/bin/bash
# Setup script for ChaosCore development environment

# Create virtual environment if it doesn't exist
if [ ! -d "env" ]; then
  echo "Creating virtual environment..."
  python -m venv env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .
pip install ecdsa pycryptodome web3

echo "Setup complete. You can now run the demos with:"
echo "python examples/agent_registry_demo.py" 