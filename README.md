# ChaosChain Governance OS

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Solidity ^0.8.17](https://img.shields.io/badge/solidity-^0.8.17-blue.svg)](https://soliditylang.org/)

<p align="center">
  <img src="https://via.placeholder.com/600x300?text=ChaosChain+Governance+OS" alt="ChaosChain Governance OS" width="600">
</p>

<p align="center">
  <b>A cross-chain, AI-driven governance platform for blockchain networks</b>
</p>

---

## 🔍 What is ChaosChain?

ChaosChain is a cross-chain agentic governance operating system designed to enhance blockchain governance through AI-driven agents. ChaosChain functions as a governance-as-a-service platform that integrates with existing blockchains to augment their governance and core development processes.

### Core Value Proposition

- **Accelerate blockchain evolution** through AI-assisted governance and development
- **Enable cross-chain knowledge sharing** and improvement propagation
- **Provide rigorous simulation-based validation** for protocol changes with full verifiability
- **Cryptographic verification:** agents run inside secure execution environments with attestation
- **Drop‑in for existing DAOs/L1s:** minimal endpoint contract or off‑chain adapter integration
- **Lower the barrier** to quality governance for blockchain ecosystems of any size

```mermaid
flowchart LR
    subgraph "ChaosChain Node"
        A[AI Agents] -->|blockchain metrics| M((DB))
        A --> S[Fork Simulator]
        S --> A
        A --> TEE[SGX Enclave]
        TEE -- attested output --> C(Endpoint Contract)
    end
    C --> Chain[(Ethereum Testnet)]
```

## Project Overview

The ChaosChain Governance OS provides the following core capabilities:

- **Autonomous Governance Agents**: AI-powered agents that analyze blockchain data and execute governance tasks
- **On-Chain Data Analysis**: Real-time analysis of blockchain metrics and governance proposals
- **Transparent Decision Making**: Verifiable decision processes with Proof of Agency receipts
- **Secure Execution**: Execute governance tasks in secure, isolated environments
- **Multi-Chain Compatibility**: Support for different EVM-compatible blockchains

## Key Components

### Autonomous Governance Agent

The platform's cornerstone is the `GovernanceAnalystAgent`, which can:

1. Collect blockchain context data from multiple sources
2. Autonomously decide which governance tasks to execute
3. Securely execute tasks with verifiable outputs
4. Generate cryptographically verifiable Proof of Agency receipts
5. Anchor significant decisions to the blockchain

### Governance Tasks

The platform currently supports these governance tasks:

- **GasParameterOptimizer**: Analyzes gas usage patterns and recommends optimal parameters
- **ProposalSanityScanner**: Scans governance proposals for security issues and logical inconsistencies
- **MEVCostEstimator**: Estimates potential MEV extraction costs for proposed changes

### Blockchain Context Fetcher

The `EthereumContextFetcher` enables connection to real Ethereum networks to fetch:

- Recent blocks and their metrics
- Active governance proposals
- Gas price statistics and trends

## Getting Started

### Prerequisites

- Python 3.12+
- Web3.py and related dependencies
- Access to an Ethereum RPC endpoint (optional for real data, mock mode available)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/chaoschain/chaoschain-governance-os.git
   cd chaoschain-governance-os
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set environment variables (optional for real blockchain data):
   ```bash
   export ETHEREUM_MOCK=false  # Set to true for mock data
   export ETHEREUM_PROVIDER_URL=your_ethereum_rpc_url
   ```

### Running the Governance Agent Demo

Run the autonomous governance agent demo:

```bash
# Run with agent decision-making
python examples/governance_agent_autonomous.py

# Specify a particular task
python examples/governance_agent_autonomous.py --task GasParameterOptimizer
python examples/governance_agent_autonomous.py --task ProposalSanityScanner
python examples/governance_agent_autonomous.py --task MEVCostEstimator

# Enable verbose output
python examples/governance_agent_autonomous.py --verbose
```

## Project Structure

```
chaoschain-governance-os/
├── agent/                            # Agent implementation
│   ├── agents/                       # Agent definitions
│   │   └── governance_analyst_agent.py  # Main agent implementation
│   ├── blockchain/                   # Blockchain interfaces
│   │   └── context_fetcher.py        # Context fetching from blockchains
│   ├── tasks/                        # Governance tasks
│   │   ├── gas_parameter_optimizer.py  # Gas parameter optimization
│   │   ├── mev_cost_estimator.py     # MEV cost estimation
│   │   └── proposal_sanity_scanner.py  # Proposal security scanning
│   ├── mock_*.py                     # Mock components for testing
│   └── task_registry.py              # Task registration system
├── examples/                         # Example scripts
│   └── governance_agent_autonomous.py  # Autonomous agent demo
├── tests/                            # Test suite
├── requirements.txt                  # Python dependencies
└── pyproject.toml                    # Project configuration
```

## Technology Stack

- **Agent Framework**: Compatible with CrewAI and LangChain
- **Blockchain Interaction**: Web3.py
- **AI Models**: Compatible with various LLM providers

## Recent Developments

### Ethereum Transaction Anchoring

- Implemented real transaction anchoring on Sepolia testnet
- Actions performed by agents are now cryptographically anchored to the blockchain
- Added support for agent registration on-chain
- Transaction hashes are stored and can be verified on Etherscan
- Demo available to showcase the full flow from agent registration to anchoring

To run the Ethereum anchoring demo:

```bash
# Clone and set up the repository
git clone https://github.com/chaoschain/chaoschain-governance-os.git
cd chaoschain-governance-os

# Copy example environment file and update with your keys
cp env.example .env
# Edit .env with your Ethereum provider URL and private key

# Build and run the services
docker-compose -f docker-compose.example.yml up -d

# Run the demo (requires Sepolia ETH in your wallet)
make boot-sepolia
```

### Sprint 7: Governance Agent Context Fetching

- Implemented `EthereumContextFetcher` for real blockchain data integration
- Enhanced task system to properly handle different data structures
- Improved agent decision making with fallbacks and error handling
- Added demonstration of autonomous governance operations

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'S#: Add some amazing feature'`) where # is the sprint number
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md): Comprehensive project overview and roadmap
- [MVP Specification](docs/MVP_SPEC.md): Minimum Viable Product details
- Architecture documents: Found in the [docs/architecture](docs/architecture) directory

## Overview

The ChaosChain Governance OS is a governance platform that combines AI agents, secure execution, and blockchain anchoring to create transparent, verifiable governance systems. This project is built on the ChaosCore platform.

## Components

- **Agent Registry**: Register and verify governance agents
- **Proof of Agency**: Log and verify agent actions
- **Secure Execution Environment**: Run code in a verifiable, isolated environment
- **Reputation System**: Track agent performance
- **Studio Framework**: Organize agents into governance crews

## Setup and Installation

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Node.js and npm (for Ethereum contract deployment)
- An Ethereum account with Sepolia ETH (for testnet deployment)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/chaoschain/chaoschain-governance-os.git
   cd chaoschain-governance-os
   ```

2. Set up environment:
   ```bash
   # Copy the Sepolia environment example
   cp deployments/.env.sepolia.example deployments/.env.sepolia
   
   # Edit with your actual values
   nano deployments/.env.sepolia  # Add your RPC_URL and PRIVATE_KEY
   ```

3. Deploy the contract to Sepolia testnet:
   ```bash
   make deploy-sepolia
   ```

4. Run the full demo stack:
   ```bash
   make boot-sepolia
   ```

5. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

### Running with Docker

Start the entire stack:

```bash
docker-compose up -d
```