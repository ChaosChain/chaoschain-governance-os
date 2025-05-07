import { ethers } from "ethers";
import "dotenv/config";

// Import contract artifacts
const ChaosEndpointArtifact = require("../../artifacts/ethereum/contracts/ChaosEndpoint.sol/ChaosEndpoint.json");

/**
 * Client for interacting with the ChaosEndpoint contract
 */
export class ChaosEndpointClient {
  private provider: ethers.JsonRpcProvider;
  private contract: ethers.Contract;
  private signer?: ethers.Signer;

  /**
   * Create a new client instance
   * @param contractAddress The address of the deployed ChaosEndpoint contract
   * @param rpcUrl The Ethereum RPC URL to connect to
   * @param privateKey Optional wallet private key for sending transactions
   */
  constructor(
    contractAddress: string,
    rpcUrl: string = `https://sepolia.infura.io/v3/${process.env.INFURA_API_KEY}`,
    privateKey?: string
  ) {
    // Initialize provider
    this.provider = new ethers.JsonRpcProvider(rpcUrl);
    
    // Initialize contract instance
    this.contract = new ethers.Contract(
      contractAddress,
      ChaosEndpointArtifact.abi,
      this.provider
    );
    
    // Set up signer if private key is provided
    if (privateKey) {
      this.signer = new ethers.Wallet(privateKey, this.provider);
      this.contract = this.contract.connect(this.signer);
    }
  }

  /**
   * Submit a new parameter adjustment proposal
   * @param metadataURI IPFS or HTTP URI containing proposal metadata
   * @param attestation TEE attestation proving the proposal's integrity
   * @returns The ID of the newly created proposal
   */
  async submitProposal(
    metadataURI: string,
    attestation: Uint8Array
  ): Promise<bigint> {
    if (!this.signer) {
      throw new Error("Signer not available. Provide a private key to submit proposals.");
    }
    
    const tx = await this.contract.submitProposal(metadataURI, attestation);
    const receipt = await tx.wait();
    
    // Extract proposal ID from event
    const event = receipt.logs
      .map((log: any) => {
        try {
          return this.contract.interface.parseLog(log);
        } catch (e) {
          return null;
        }
      })
      .find((event: any) => event?.name === "ProposalSubmitted");
    
    if (!event) {
      throw new Error("Failed to parse ProposalSubmitted event");
    }
    
    return event.args[0]; // proposalId
  }

  /**
   * Get proposal details by ID
   * @param proposalId The ID of the proposal to retrieve
   * @returns The proposal details
   */
  async getProposal(proposalId: bigint | number) {
    const proposal = await this.contract.getProposal(proposalId);
    return {
      proposalId: proposal.proposalId,
      submitter: proposal.submitter,
      metadataURI: proposal.metadataURI,
      attestation: proposal.attestation,
      timestamp: new Date(Number(proposal.timestamp) * 1000)
    };
  }
} 