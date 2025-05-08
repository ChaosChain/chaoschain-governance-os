#!/bin/bash
# Script to run the ChaosChain demo with streaming logs

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Echo with color
echo_color() {
  echo -e "${1}${2}${NC}"
}

# Create the directory structure for the API if it doesn't exist
mkdir -p api/rest/routers

# Start the frontend in the background
echo_color $YELLOW "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Sleep to allow the frontend to start
sleep 2

# Start the FastAPI server in the background
echo_color $YELLOW "Starting API server..."
export ENABLE_STREAM=1
export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2)
export ETHEREUM_RPC_URL=$(grep ETHEREUM_RPC_URL .env | cut -d '=' -f2)
cd api
uvicorn rest.app:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!
cd ..

echo_color $GREEN "API server started on http://localhost:8000"
echo

# Wait for the API to be ready
echo_color $YELLOW "Waiting for API to be ready..."
attempt=0
max_attempts=10
until $(curl --output /dev/null --silent --head --fail http://localhost:8000/health); do
  if [ ${attempt} -eq ${max_attempts} ]; then
    echo_color $RED "API service not ready after ${max_attempts} attempts. Exiting."
    kill $FRONTEND_PID
    kill $API_PID
    exit 1
  fi
  
  attempt=$((attempt+1))
  echo_color $YELLOW "API not ready yet. Waiting... (${attempt}/${max_attempts})"
  sleep 2
done

echo_color $GREEN "API service is ready."
echo

# Run the demo with streaming
echo_color $YELLOW "Running governance demo with streaming logs..."
python -m agent.runtime.demo --stream --verbose

# Display URLs
echo_color $CYAN "================================="
echo_color $CYAN " ChaosChain Demo is Running"
echo_color $CYAN "================================="
echo
echo_color $GREEN "📊 Frontend UI:      http://localhost:5173"
echo_color $GREEN "🚀 API Documentation: http://localhost:8000/docs"
echo
echo_color $YELLOW "Press Ctrl+C to stop all services"

# Wait for Ctrl+C, then clean up
trap "kill $FRONTEND_PID; kill $API_PID; echo_color $GREEN 'All services stopped.'; exit" INT
wait 