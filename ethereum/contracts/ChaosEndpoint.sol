// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IChaosChainEndpoint {
    // Event emitted when a new proposal is submitted
    event ProposalSubmitted(
        uint256 indexed proposalId,
        address submitter,
        string metadataURI,
        bytes attestation
    );
    
    // Struct representing a parameter adjustment proposal
    struct Proposal {
        uint256 proposalId;
        address submitter;
        string metadataURI;
        bytes attestation;
        uint256 timestamp;
    }
    
    // Submit a new parameter adjustment proposal
    function submitProposal(
        string calldata metadataURI,
        bytes calldata attestation
    ) external returns (uint256 proposalId);
    
    // Get proposal details
    function getProposal(uint256 proposalId) 
        external view returns (Proposal memory);
}

contract ChaosEndpoint is IChaosChainEndpoint {
    // Counter for proposal IDs
    uint256 private _nextProposalId = 1;
    
    // Mapping from proposal ID to proposal details
    mapping(uint256 => Proposal) private _proposals;
    
    /**
     * @dev Submit a new parameter adjustment proposal
     * @param metadataURI IPFS or HTTP URI containing proposal metadata
     * @param attestation TEE attestation proving the proposal's integrity
     * @return proposalId The ID of the newly created proposal
     */
    function submitProposal(
        string calldata metadataURI,
        bytes calldata attestation
    ) external override returns (uint256 proposalId) {
        // Assign the next proposal ID
        proposalId = _nextProposalId++;
        
        // Create and store the proposal
        _proposals[proposalId] = Proposal({
            proposalId: proposalId,
            submitter: msg.sender,
            metadataURI: metadataURI,
            attestation: attestation,
            timestamp: block.timestamp
        });
        
        // Emit the event
        emit ProposalSubmitted(
            proposalId,
            msg.sender,
            metadataURI,
            attestation
        );
        
        return proposalId;
    }
    
    /**
     * @dev Retrieve a proposal by ID
     * @param proposalId The ID of the proposal to retrieve
     * @return The proposal details
     */
    function getProposal(uint256 proposalId) 
        external view override returns (Proposal memory) {
        require(proposalId > 0 && proposalId < _nextProposalId, "Invalid proposal ID");
        return _proposals[proposalId];
    }
} 