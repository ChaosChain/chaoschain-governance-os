/**
 * TypeScript definitions for ChaosChain Ethereum client
 */

export interface Proposal {
  proposalId: bigint;
  submitter: string;
  metadataURI: string;
  attestation: Uint8Array;
  timestamp: Date;
}

export interface ChaosEndpointClientOptions {
  contractAddress: string;
  rpcUrl?: string;
  privateKey?: string;
}

export interface IChaosEndpointClient {
  submitProposal(metadataURI: string, attestation: Uint8Array): Promise<bigint>;
  getProposal(proposalId: bigint | number): Promise<Proposal>;
} 