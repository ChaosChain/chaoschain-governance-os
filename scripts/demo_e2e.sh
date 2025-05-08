#!/bin/bash
# End-to-end demo script for ChaosChain Governance OS

# Color definitions
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Echo with color
echo_color() {
  echo -e "${1}${2}${NC}"
}

# Print header
echo_color $CYAN "================================="
echo_color $CYAN " ChaosChain Governance OS Demo"
echo_color $CYAN "================================="
echo

# Build frontend if not already built
if [ ! -d "frontend/dist" ]; then
  echo_color $YELLOW "Building frontend..."
  (cd frontend && npm install && npm run build)
  echo_color $GREEN "Frontend built successfully."
  echo
fi

# Start the Docker services
echo_color $YELLOW "Starting services..."
docker-compose -f scripts/docker-compose.demo.yml build
docker-compose -f scripts/docker-compose.demo.yml up -d
echo_color $GREEN "Services started successfully."
echo

# Wait for the API to be ready
echo_color $YELLOW "Waiting for API to be ready..."
attempt=0
max_attempts=30
until $(curl --output /dev/null --silent --head --fail http://localhost:8000/health); do
  if [ ${attempt} -eq ${max_attempts} ]; then
    echo_color $RED "API service not ready after ${max_attempts} attempts. Exiting."
    exit 1
  fi
  
  attempt=$((attempt+1))
  echo_color $YELLOW "API not ready yet. Waiting... (${attempt}/${max_attempts})"
  sleep 2
done

echo_color $GREEN "API service is ready."
echo

# Run the demo script
echo_color $YELLOW "Executing demo script..."
docker-compose -f scripts/docker-compose.demo.yml exec api python demo.py
echo_color $GREEN "Demo script executed successfully."
echo

# Display the URLs for accessing the services
echo_color $CYAN "================================="
echo_color $CYAN " Demo is now running!"
echo_color $CYAN "================================="
echo
echo_color $GREEN "📊 UI Dashboard:    http://localhost:8080/ui"
echo_color $GREEN "🚀 API Endpoints:   http://localhost:8000/docs"
echo_color $GREEN "⛓️ Ethereum Node:   http://localhost:8545"
echo
echo_color $YELLOW "To view logs, run:"
echo_color $YELLOW "docker-compose -f scripts/docker-compose.demo.yml logs -f"
echo
echo_color $YELLOW "To stop the demo, run:"
echo_color $YELLOW "docker-compose -f scripts/docker-compose.demo.yml down"
echo
echo_color $CYAN "Open your browser to view the dashboard: http://localhost:8080/ui"
echo_color $CYAN "=================================" 