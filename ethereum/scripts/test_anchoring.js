// Test script for anchoring receipts in the ChaosEndpoint contract
const { ethers } = require("hardhat");

async function main() {
  console.log("Starting ChaosEndpoint anchoring test...");
  
  // Deploy the contract if not already deployed
  console.log("Deploying ChaosEndpoint contract...");
  const ChaosEndpoint = await ethers.getContractFactory("ChaosEndpoint");
  const chaosEndpoint = await ChaosEndpoint.deploy();
  await chaosEndpoint.deployed();
  console.log("ChaosEndpoint deployed to:", chaosEndpoint.address);
  
  // Get signers
  const [owner] = await ethers.getSigners();
  console.log("Testing with address:", owner.address);
  
  // Generate a random agent ID
  const agentId = `agent-${Math.floor(Math.random() * 1000000)}`;
  console.log(`Registering agent with ID: ${agentId}`);
  
  // Register an agent
  const agentMetadataURI = "ipfs://Qm123456789012345678901234567890";
  const mockAttestation = ethers.utils.toUtf8Bytes("This is a mock attestation");
  
  console.log("Registering agent...");
  const registerTx = await chaosEndpoint.registerAgent(
    agentId,
    agentMetadataURI,
    mockAttestation
  );
  
  // Wait for the transaction to be mined
  const registerReceipt = await registerTx.wait();
  console.log("Agent registered in transaction:", registerReceipt.transactionHash);
  console.log("Gas used for agent registration:", registerReceipt.gasUsed.toString());
  
  // Generate a random action ID
  const actionId = `action-${Math.floor(Math.random() * 1000000)}`;
  console.log(`Anchoring action with ID: ${actionId}`);
  
  // Anchor an action
  const actionType = "GOVERNANCE_SIMULATION";
  const actionMetadataURI = "ipfs://Qm987654321098765432109876543210";
  
  console.log("Anchoring action...");
  const anchorTx = await chaosEndpoint.anchorAction(
    actionId,
    agentId,
    actionType,
    actionMetadataURI,
    mockAttestation
  );
  
  // Wait for the transaction to be mined
  const anchorReceipt = await anchorTx.wait();
  console.log("Action anchored in transaction:", anchorReceipt.transactionHash);
  console.log("Gas used for action anchoring:", anchorReceipt.gasUsed.toString());
  
  // Record the outcome
  const outcomeURI = "ipfs://Qm567890123456789012345678901234";
  
  console.log("Recording outcome...");
  const outcomeTx = await chaosEndpoint.recordOutcome(
    actionId,
    outcomeURI
  );
  
  // Wait for the transaction to be mined
  const outcomeReceipt = await outcomeTx.wait();
  console.log("Outcome recorded in transaction:", outcomeReceipt.transactionHash);
  console.log("Gas used for outcome recording:", outcomeReceipt.gasUsed.toString());
  
  // Distribute rewards
  const recipientsData = JSON.stringify({
    recipients: [
      { address: owner.address, amount: "1.0" }
    ]
  });
  
  console.log("Distributing rewards...");
  const rewardsTx = await chaosEndpoint.distributeRewards(
    actionId,
    recipientsData
  );
  
  // Wait for the transaction to be mined
  const rewardsReceipt = await rewardsTx.wait();
  console.log("Rewards distributed in transaction:", rewardsReceipt.transactionHash);
  console.log("Gas used for rewards distribution:", rewardsReceipt.gasUsed.toString());
  
  // Get the anchored action
  console.log("Fetching anchored action...");
  const action = await chaosEndpoint.getAnchoredAction(actionId);
  console.log("Anchored action:", {
    actionId: action.actionId,
    agentId: action.agentId,
    actionType: action.actionType,
    metadataURI: action.metadataURI,
    timestamp: action.timestamp.toString(),
    hasOutcome: action.hasOutcome,
    outcomeURI: action.outcomeURI
  });
  
  // Total gas usage
  const totalGas = registerReceipt.gasUsed
    .add(anchorReceipt.gasUsed)
    .add(outcomeReceipt.gasUsed)
    .add(rewardsReceipt.gasUsed);
  
  console.log("\nTotal gas used:", totalGas.toString());
  console.log("Test completed successfully!");
}

// Execute the script
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 