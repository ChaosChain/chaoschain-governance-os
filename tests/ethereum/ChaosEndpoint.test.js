const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ChaosEndpoint", function () {
  let chaosEndpoint;
  let owner;
  let addr1;

  beforeEach(async function () {
    // Get signers (accounts)
    [owner, addr1] = await ethers.getSigners();

    // Deploy the contract
    const ChaosEndpoint = await ethers.getContractFactory("ChaosEndpoint");
    chaosEndpoint = await ChaosEndpoint.deploy();
  });

  describe("Proposal Submission", function () {
    it("Should create a new proposal and emit an event", async function () {
      const metadataURI = "ipfs://QmTest";
      const attestation = ethers.toUtf8Bytes("test-attestation");

      // Submit proposal
      const tx = await chaosEndpoint.submitProposal(metadataURI, attestation);
      
      // Wait for the transaction
      const receipt = await tx.wait();
      
      // Check that the ProposalSubmitted event was emitted
      const event = receipt.logs[0];
      const args = event.args;
      
      expect(args.proposalId).to.equal(1n);
      expect(args.submitter).to.equal(owner.address);
      expect(args.metadataURI).to.equal(metadataURI);
      expect(ethers.toUtf8String(args.attestation)).to.equal("test-attestation");
    });

    it("Should store the proposal correctly", async function () {
      const metadataURI = "ipfs://QmTest2";
      const attestation = ethers.toUtf8Bytes("test-attestation-2");

      // Submit proposal
      await chaosEndpoint.submitProposal(metadataURI, attestation);
      
      // Get the proposal
      const proposal = await chaosEndpoint.getProposal(1);
      
      expect(proposal.proposalId).to.equal(1n);
      expect(proposal.submitter).to.equal(owner.address);
      expect(proposal.metadataURI).to.equal(metadataURI);
      expect(ethers.toUtf8String(proposal.attestation)).to.equal("test-attestation-2");
    });

    it("Should revert when trying to get a non-existent proposal", async function () {
      await expect(chaosEndpoint.getProposal(999))
        .to.be.revertedWith("Invalid proposal ID");
    });
  });
}); 