// Hardhat deployment script for ChaosEndpoint contract to Sepolia testnet
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

  // Save contract address to JSON file
  const deploymentData = {
    network: "sepolia",
    contractName: "ChaosEndpoint",
    address: contractAddress,
    deployedAt: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber()
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