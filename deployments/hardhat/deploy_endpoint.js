// Hardhat deployment script for ChaosEndpoint contract to Sepolia testnet
require("dotenv").config();
const fs = require('fs');
const path = require('path');
const hre = require("hardhat");

async function main() {
  console.log("Deploying ChaosEndpoint contract to Sepolia testnet...");

  // Get the Contract Factory
  const ChaosEndpoint = await hre.ethers.getContractFactory("ChaosEndpoint");
  
  // Deploy the contract
  const chaosEndpoint = await ChaosEndpoint.deploy();
  
  // Wait for deployment to finish
  const tx = await chaosEndpoint.deploymentTransaction();
  await chaosEndpoint.waitForDeployment();
  
  // Get the contract address
  const contractAddress = await chaosEndpoint.getAddress();
  
  console.log(`ChaosEndpoint deployed to Sepolia at address: ${contractAddress}`);
  console.log(`Verify with: npx hardhat verify --network sepolia ${contractAddress}`);

  // Create output directory if it doesn't exist
  const outputDir = path.join(__dirname, '..', 'sepolia');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Get the current block number
  const blockNumber = await hre.ethers.provider.getBlockNumber();

  // Save contract address to JSON file
  const deploymentData = {
    network: "sepolia",
    address: contractAddress,
    block: blockNumber,
    txHash: tx.hash,
    deployedAt: new Date().toISOString()
  };
  
  const outputPath = path.join(outputDir, 'ChaosEndpoint.json');
  fs.writeFileSync(
    outputPath,
    JSON.stringify(deploymentData, null, 2)
  );
  
  console.log(`Deployment data saved to ${outputPath}`);
}

// Execute the deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 