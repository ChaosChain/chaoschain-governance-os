#!/bin/bash
set -e

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Print banner
echo "======================================================"
echo "      ChaosChain Governance OS - Demo Environment     "
echo "======================================================"
echo ""

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
  echo "❌ Docker is not installed. Please install Docker."
  exit 1
fi

if ! docker compose version &> /dev/null; then
  echo "❌ Docker Compose is not installed. Please install Docker Compose."
  exit 1
fi

# Build the Docker images
echo "🔨 Building Docker images..."
docker compose -f scripts/docker-compose.demo.yml build

# Start the services
echo "🚀 Starting demo environment..."
docker compose -f scripts/docker-compose.demo.yml up -d

# Wait for services to be up
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run the demo script
echo "🎮 Running demo script..."
docker compose -f scripts/docker-compose.demo.yml exec api python -m demo

# Display URLs
echo ""
echo "🌐 Services are available at:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:8000/app"
echo "  - Hardhat: http://localhost:8545"
echo ""

# Tail logs if requested
if [ "$1" = "--logs" ]; then
  echo "📜 Showing logs (Ctrl+C to exit)..."
  docker compose -f scripts/docker-compose.demo.yml logs -f
else
  echo "📜 To view logs, run: ./scripts/demo_e2e.sh --logs"
  echo ""
  echo "🛑 To stop the demo, run: docker compose -f scripts/docker-compose.demo.yml down"
fi 