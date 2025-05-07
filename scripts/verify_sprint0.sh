#!/bin/bash
# Sprint-0 verification script
# Checks that all required components are properly set up

set -e

echo "🚀 ChaosChain Governance OS - Sprint-0 Verification"
echo "=================================================="
echo

# Check directory structure
echo "📂 Checking directory structure..."
REQUIRED_DIRS=(
  "agent/runtime"
  "agent/crew/researcher"
  "agent/crew/developer"
  "agent/tools"
  "verification/tee"
  "verification/attestation"
  "verification/audit"
  "ethereum/client"
  "ethereum/contracts"
  "ethereum/monitoring"
  "simulation/harness"
  "simulation/metrics"
  "simulation/scenarios"
  "reputation/db"
  "reputation/scoring"
  "reputation/api"
  "api/rest"
  "api/auth"
  "api/docs"
  "tests/unit"
  "tests/integration"
  "tests/e2e"
  "docs/architecture"
)

MISSING=0
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "❌ Missing directory: $dir"
    MISSING=1
  fi
done

if [ $MISSING -eq 0 ]; then
  echo "✅ Directory structure verified"
else
  echo "❌ Directory structure incomplete"
  exit 1
fi

echo

# Verify configuration files
echo "📝 Checking configuration files..."
REQUIRED_CONFIG=(
  "pyproject.toml"
  "package.json"
  "Cargo.toml"
  "hardhat.config.ts"
)

MISSING=0
for file in "${REQUIRED_CONFIG[@]}"; do
  if [ ! -f "$file" ]; then
    echo "❌ Missing config file: $file"
    MISSING=1
  fi
done

if [ $MISSING -eq 0 ]; then
  echo "✅ Configuration files verified"
else
  echo "❌ Configuration files incomplete"
  exit 1
fi

echo

# Verify CrewAI demo
echo "🤖 Checking CrewAI demo..."
if [ ! -f "agent/crew/quick_demo.py" ]; then
  echo "❌ Missing CrewAI demo script"
  exit 1
else
  if [ ! -x "agent/crew/quick_demo.py" ]; then
    echo "⚠️ CrewAI demo script is not executable"
    chmod +x agent/crew/quick_demo.py
    echo "✅ Made script executable"
  fi
  echo "✅ CrewAI demo script verified"
fi

echo

# Verify Solidity contract
echo "📄 Checking Solidity contract..."
if [ ! -f "ethereum/contracts/ChaosEndpoint.sol" ]; then
  echo "❌ Missing Solidity contract"
  exit 1
else
  echo "✅ Solidity contract verified"
fi

echo

# Verify tests
echo "🧪 Checking test files..."
if [ ! -f "tests/unit/agent/test_quick_demo.py" ]; then
  echo "❌ Missing CrewAI tests"
  exit 1
else
  echo "✅ Python tests verified"
fi

if [ ! -f "tests/ethereum/ChaosEndpoint.test.js" ]; then
  echo "❌ Missing contract tests"
  exit 1
else
  echo "✅ Contract tests verified"
fi

echo

# Verify SGX placeholder
echo "🔒 Checking SGX placeholder..."
if [ ! -f "verification/tee/README.md" ] || [ ! -f "verification/tee/enclave/src/lib.rs" ]; then
  echo "❌ Missing SGX placeholder"
  exit 1
else
  echo "✅ SGX placeholder verified"
fi

echo

# Verify documentation
echo "📚 Checking documentation..."
if [ ! -f "docs/sprint_backlog.md" ]; then
  echo "❌ Missing Sprint-1 backlog"
  exit 1
else
  echo "✅ Documentation verified"
fi

echo
echo "✨ Sprint-0 verification complete!"
echo "All required components are in place."
echo
echo "Next steps:"
echo "1. Install dependencies: pip install -e \".[dev]\" && npm install"
echo "2. Run tests: pytest tests/ && npx hardhat test"
echo "3. Run CrewAI demo: python agent/crew/quick_demo.py --rpc <YOUR_RPC_URL>"
echo 