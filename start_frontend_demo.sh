#!/bin/bash
# Simple script to start the frontend demo without Docker

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored message
echo_color() {
  echo -e "${1}${2}${NC}"
}

# Print header
echo_color $CYAN "====================================="
echo_color $CYAN " ChaosChain Governance OS Demo"
echo_color $CYAN "====================================="
echo

# Start frontend in development mode
echo_color $YELLOW "Starting frontend in development mode..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo_color $GREEN "Frontend started successfully at http://localhost:5173/"
echo

# Show URLs
echo_color $CYAN "====================================="
echo_color $CYAN " Demo is now running!"
echo_color $CYAN "====================================="
echo
echo_color $GREEN "📊 UI Dashboard: http://localhost:5173/"
echo
echo_color $YELLOW "Press Ctrl+C to stop the demo"
echo
echo_color $CYAN "Open your browser to view the dashboard: http://localhost:5173/"
echo_color $CYAN "====================================="

# Wait for Ctrl+C
trap "kill $FRONTEND_PID; echo_color $YELLOW 'Demo stopped.'; exit" INT
wait 