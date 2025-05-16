# ChaosChain Governance OS

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
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
- **Cryptographic verification:** agents run inside SGX (zkML coming) — anyone can audit the attestation
- **Drop‑in for existing DAOs/L1s:** minimal endpoint contract or off‑chain adapter, no consensus changes
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

- **Cross-Chain Monitoring**: Monitor on-chain activity across various EVM-compatible chains
- **AI-Powered Analysis**: Analyze blockchain data to identify potential governance improvements
- **Governance Automation**: Generate and validate governance proposals using LLM-driven agents
- **Multi-Chain Execution**: Submit validated proposals to different blockchains

## Architecture

ChaosChain consists of several interconnected systems that work together to deliver AI-enhanced governance:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ChaosChain Platform                           │
│                                                                     │
│   ┌─────────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│   │ Agent       │    │ Verification │    │ Blockchain Endpoint   │  │
│   │ Runtime     │◄─┐ │ Layer        │    │ Client                │  │
│   │ - Framework │  │ │              │    │ - Chain adapters      │  │
│   │   Agnostic  │  │ │              │    │ - Transaction signing │  │
│   └─────────────┘  │ └──────────────┘    └───────────────────────┘  │
│         ▲          │        ▲                       ▲               │
│         │          │        │                       │               │
│   ┌─────┴──────────┴─┐    ┌─┴──────────┐      ┌────┴──────────────┐ │
│   │ Simulation       │    │ Reputation │      │ Incentive         │ │
│   │ Environment      │    │ System     │      │ Mechanism         │ │
│   └──────────────────┘    └────────────┘      └───────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Major Components

1. **Agent Runtime**: Framework-agnostic inference engine for governance agents
2. **Verification Layer**: Transparency and audit mechanisms with TEE (Trusted Execution Environment)
3. **Blockchain Endpoint Client**: Chain-specific adapters for multiple blockchains
4. **Simulation Environment**: Forked chain testing environments for proposal validation
5. **Reputation System**: Performance tracking for agent contributions

For detailed architecture documentation, see the [Implementation Plan](IMPLEMENTATION_PLAN.md) and [MVP Specification](docs/MVP_SPEC.md).

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- Access to an Ethereum RPC endpoint
- (Optional) GPU for AI model acceleration

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/chaoschain-governance-os.git
   cd chaoschain-governance-os
   ```

2. Set up Python environment:
   ```bash
   python -m venv chaos
   source chaos/bin/activate  # On Windows, use: chaos\Scripts\activate
   pip install -e .
   ```

3. Install Ethereum dependencies:
   ```bash
   npm install
   ```

4. Set up environment variables:
   ```bash
   export ETHEREUM_RPC_URL=your_ethereum_rpc_url
   export OPENAI_API_KEY=your_openai_api_key  # If using OpenAI models
   ```

### Running the Application

#### Demo

The simplest way to see the system in action is to run the demo script:

```bash
# Run with default settings
python demo.py

# Run with verbose output
python demo.py --verbose
```

The demo uses mock data to simulate blockchain analysis and governance proposal generation.

#### Agent Testing

```bash
# Run unit tests
pytest tests/unit/

# Run the quick demo
python -m agent.quick_demo
```

#### Smart Contract Testing

```bash
# Compile contracts
npx hardhat compile

# Run contract tests
npx hardhat test
```

## Project Structure

```
chaoschain-governance-os/
├── agent/                   # AI agent implementation
│   ├── governance_crew.py   # Main governance crew implementation
│   ├── tools/               # Agent tools for blockchain interaction
│   └── models/              # Data models
├── ethereum/                # Ethereum smart contracts
│   ├── contracts/           # Solidity contracts
│   └── test/                # Contract tests
├── api/                     # API service
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── demo.py                  # Demo script
└── docs/                    # Documentation
```

## Technology Stack

- **Agent Framework**: CrewAI + LangChain
- **Blockchain Interaction**: Web3.py, Hardhat
- **AI Models**: Compatible with OpenAI, Anthropic Claude, and other providers
- **Smart Contracts**: Solidity
- **API**: FastAPI

## Contributing

Contributions are welcome! Please check out our [contribution guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Agent collaboration framework
- [LangChain](https://github.com/hwchase17/langchain) - LLM framework
- [Web3.py](https://github.com/ethereum/web3.py) - Ethereum interface
- [Hardhat](https://github.com/nomiclabs/hardhat) - Ethereum development environment

## 📚 Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md): Comprehensive project overview and roadmap
- [MVP Specification](docs/MVP_SPEC.md): Minimum Viable Product details
- Architecture documents: Found in the [docs/architecture](docs/architecture) directory

## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows our style guidelines and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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
- Node.js 16+ (for Ethereum development)

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/chaoschain/chaoschain-governance-os.git
cd chaoschain-governance-os
```

2. Install dependencies:
```bash
pip install -e .
```

3. Run the demo:
```bash
python demo_governance_flow.py
```

### Staging Environment

The staging environment is a production-like environment used for testing. It includes:

- PostgreSQL for persistent storage
- SGX dev-container for secure execution
- Goerli testnet for blockchain anchoring
- Prometheus and Grafana for monitoring

#### Setting Up Staging

1. Start the staging environment:
```bash
docker-compose up -d
```

2. The following services will be available:
   - ChaosCore API: http://localhost:8000
   - PostgreSQL: localhost:5432
   - SGX Enclave: http://localhost:7000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (username: admin, password: admin)

3. Environment variables for connecting to services:
```
# PostgreSQL
POSTGRES_USER=chaoscore
POSTGRES_PASSWORD=chaoscore_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chaoscore

# SGX Enclave
SGX_ENCLAVE_URL=http://localhost:7000

# Ethereum (Goerli)
ETHEREUM_PROVIDER_URL=https://goerli.infura.io/v3/your-api-key
ETHEREUM_CONTRACT_ADDRESS=0x1234567890123456789012345678901234567890
```

4. Run the demo in staging mode:
```bash
python demo_governance_flow.py --stage
```

## Testing

### Run Tests
```bash
pytest tests/
```

### Run Linting
```bash
black .
isort .
flake8 .
```

## SDK

The ChaosCore SDK can be used to interact with the platform:

```python
from chaoscore.sdk.python import ChaosCoreClient

# Create a client
client = ChaosCoreClient()

# Register an agent
agent_id = client.register_agent(
    name="Parameter Optimizer",
    email="optimizer@example.com",
    metadata={"role": "developer"}
)

# Log an action
action_id = client.log_action(
    agent_id=agent_id,
    action_type="OPTIMIZE",
    description="Optimize gas parameters"
)
```

## Monitoring

The platform includes monitoring tools to track system metrics:

- **Prometheus**: Collects metrics at http://localhost:9090
- **Grafana**: Visualizes metrics at http://localhost:3000

The dashboard visualizes:
- Agent count
- Action count
- Simulation count
- Anchoring operations
- API performance

## Architecture

The ChaosChain Governance OS is built on the ChaosCore platform, which provides core infrastructure for governance operations:

1. Agents are registered in the Agent Registry
2. Agent actions are logged through Proof of Agency
3. Simulations run in the Secure Execution Environment
4. Results are anchored to Ethereum
5. Agent reputation is updated based on outcomes

## License

MIT

