# Sepolia Testnet Deployments

This directory contains deployment artifacts for the Sepolia Ethereum testnet.

## ChaosEndpoint Contract

The primary contract deployed on Sepolia is `ChaosEndpoint`, which serves as the anchoring point for governance attestations.

### Deployment Information

Deployment information is stored in `ChaosEndpoint.json`, which is automatically generated when running:

```
make deploy-sepolia
```

### Verifying the Contract

After deployment, you can verify the contract on Sepolia Etherscan with:

```
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

Replace `<CONTRACT_ADDRESS>` with the address from `ChaosEndpoint.json`.

## Using the Deployment

To use this deployment in your application:

1. Set the environment variable `ETHEREUM_PROVIDER_URL` to your Sepolia RPC endpoint
2. Set the environment variable `ETHEREUM_CONTRACT_ADDRESS` to the deployed contract address
3. Make sure your Ethereum account has some Sepolia ETH for gas

## Why Sepolia?

Sepolia is the recommended testnet for Ethereum development as Goerli is being phased out. It provides a stable testing environment with the following benefits:

- More reliable testnet with fewer service disruptions
- Better maintained by the Ethereum community
- Faster block times for quicker testing
- Better aligned with mainnet parameters

## Getting Sepolia ETH

You can obtain Sepolia ETH from these faucets:
- [Alchemy Sepolia Faucet](https://sepoliafaucet.com/)
- [QuickNode Sepolia Faucet](https://faucet.quicknode.com/ethereum/sepolia)
- [Infura Sepolia Faucet](https://www.infura.io/faucet/sepolia) 