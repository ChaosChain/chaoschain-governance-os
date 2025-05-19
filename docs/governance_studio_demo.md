# ChaosCore Governance Studio Demo

This document describes how to run the ChaosCore Governance Studio demonstration on the Sepolia testnet.

## Prerequisites

- Node.js 16+
- Hardhat
- Docker & Docker Compose
- Python 3.9+
- Alchemy API key (for Sepolia access)
- Ethereum account with private key (with some Sepolia ETH)

## Environment Setup

1. Set up your environment variables in a `.env.sepolia` file in the deployments directory:

```bash
RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your-api-key
PRIVATE_KEY=your64characterprivatekeywithout0xprefix
```

You can use the template provided in `deployments/.env.sepolia.example`.

## Deployment Process

### 1. Deploy the ChaosEndpoint Contract to Sepolia

```bash
# Deploy the contract to Sepolia testnet
make deploy-sepolia
```

This will:
- Deploy the ChaosEndpoint contract to Sepolia
- Save deployment data to `deployments/sepolia/ChaosEndpoint.json`
- Output verification instructions for Etherscan

![Contract Deployment](images/contract_deployment.png)
*[Screenshot placeholder: Contract deployment output and contract address]*

### 2. Run the Full Sepolia Environment

```bash
# Start the Sepolia environment and run the demo
make boot-sepolia
```

This command will:
- Copy the Sepolia environment template
- Update the contract address from the deployment
- Start the Docker containers for the API, database, and SGX mock
- Wait for the API to be healthy
- Run the governance demo
- Output and open the transaction hash in Etherscan

![Governance Demo](images/governance_demo.png)
*[Screenshot placeholder: Demo output with agent creation, actions, and outcomes]*

![Etherscan Transaction](images/etherscan_tx.png)
*[Screenshot placeholder: Etherscan transaction view]*

## Demo Walkthrough

The demo showcases the core capabilities of the ChaosCore Governance Studio:

1. **Agent Registration**: Creates a governance agent with specific capabilities
2. **Action Logging**: Records a governance action (performance analysis)
3. **Outcome Recording**: Captures the results of the action
4. **Studio Creation**: Establishes a specialized governance studio
5. **Task Creation**: Defines a concrete governance task within the studio
6. **SGX Enclave Simulation**: Demonstrates secure computation
7. **Ethereum Anchoring**: Anchors action proofs to Sepolia for verifiability
8. **Reputation Updates**: Shows how agent reputation changes based on actions

## Troubleshooting

If you encounter issues with the demo, try the following:

- Check that your `.env.sepolia` file contains valid API keys and private key
- Ensure you have sufficient Sepolia ETH in your account
- Verify all containers are running with `docker-compose -f docker-compose.sepolia.yml ps`
- Check logs with `docker-compose -f docker-compose.sepolia.yml logs api`
- Reset the environment with `make clean` before trying again

## Next Steps

After running the demo, you can:

- Explore the API at `http://localhost:8000/docs`
- View monitoring dashboards at `http://localhost:3000`
- Examine the anchored data on Sepolia Etherscan
- Build your own governance workflows using the SDK

For more information, contact the ChaosChain Labs team. 