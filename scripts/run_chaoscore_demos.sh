#!/bin/bash
# ChaosCore Demo Runner
# This script runs the available ChaosCore demos

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "ChaosCore Demo Runner"
echo "====================="
echo 

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check that Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check if virtual environment exists, create if not
VENV_DIR="$ROOT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install requirements if not already installed
if [ ! -f "$VENV_DIR/lib/python3.*/site-packages/chaoscore/__init__.py" ]; then
    echo -e "${BLUE}Installing ChaosCore package...${NC}"
    cd "$ROOT_DIR"
    pip install -e ./chaoscore
fi

# Run agent registry demo
echo -e "\n${GREEN}Running Agent Registry Demo${NC}"
echo "-------------------------------"
python3 "$ROOT_DIR/chaoscore/examples/agent_registry_demo.py"

# Run proof of agency demo
echo -e "\n${GREEN}Running Proof of Agency Demo${NC}"
echo "----------------------------------"
python3 "$ROOT_DIR/chaoscore/examples/proof_of_agency_demo.py"

# Deactivate virtual environment
deactivate

echo -e "\n${GREEN}All demos completed${NC}"
echo 
echo "These demos showcase the core components of the ChaosCore platform:"
echo "1. Agent Registry - for managing agent identity and discovery"
echo "2. Proof of Agency - for tracking, verifying, and rewarding agent actions"
echo
echo "Next steps in the dual-track development approach:"
echo "- Continue governance development in chaoscore/governance/"
echo "- Extract more core components into chaoscore/core/"
echo "- Run 'python -m chaoscore.examples.proof_of_agency_demo' for additional testing" 