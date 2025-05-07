// Deployment script for ChaosEndpoint contract
const hre = require("hardhat");

async function main() {
  console.log("Deploying ChaosEndpoint contract...");

  // Get the Contract Factory
  const ChaosEndpoint = await hre.ethers.getContractFactory("ChaosEndpoint");
  
  // Deploy the contract
  const chaosEndpoint = await ChaosEndpoint.deploy();
  
  // Wait for deployment to finish
  await chaosEndpoint.waitForDeployment();
  
  // Get the contract address
  const contractAddress = await chaosEndpoint.getAddress();
  
  console.log(`ChaosEndpoint deployed to: ${contractAddress}`);
  console.log(`Verify with: npx hardhat verify --network sepolia ${contractAddress}`);
}

// Execute the deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 