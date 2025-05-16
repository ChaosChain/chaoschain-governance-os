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
    
    // Event emitted when a new agent is registered
    event AgentRegistered(
        string indexed agentId,
        address registrar,
        string metadataURI,
        bytes attestation
    );
    
    // Event emitted when an action is anchored
    event ActionAnchored(
        string indexed actionId,
        string agentId,
        string actionType,
        string metadataURI,
        bytes attestation
    );
    
    // Event emitted when rewards are distributed for an action
    event RewardsDistributed(
        string indexed actionId,
        address distributor,
        string recipientsData
    );
    
    // Struct representing a parameter adjustment proposal
    struct Proposal {
        uint256 proposalId;
        address submitter;
        string metadataURI;
        bytes attestation;
        uint256 timestamp;
    }
    
    // Struct representing a registered agent
    struct AgentRegistration {
        string agentId;
        address registrar;
        string metadataURI;
        bytes attestation;
        uint256 timestamp;
    }
    
    // Struct representing an anchored action
    struct AnchoredAction {
        string actionId;
        string agentId;
        string actionType;
        string metadataURI;
        bytes attestation;
        uint256 timestamp;
        bool hasOutcome;
        string outcomeURI;
    }
    
    // Submit a new parameter adjustment proposal
    function submitProposal(
        string calldata metadataURI,
        bytes calldata attestation
    ) external returns (uint256 proposalId);
    
    // Register a new agent
    function registerAgent(
        string calldata agentId,
        string calldata metadataURI,
        bytes calldata attestation
    ) external returns (bool success);
    
    // Anchor an action in the blockchain
    function anchorAction(
        string calldata actionId,
        string calldata agentId,
        string calldata actionType,
        string calldata metadataURI,
        bytes calldata attestation
    ) external returns (bool success);
    
    // Record an outcome for an anchored action
    function recordOutcome(
        string calldata actionId,
        string calldata outcomeURI
    ) external returns (bool success);
    
    // Distribute rewards for an action
    function distributeRewards(
        string calldata actionId,
        string calldata recipientsData
    ) external returns (bool success);
    
    // Get proposal details
    function getProposal(uint256 proposalId) 
        external view returns (Proposal memory);
    
    // Get agent registration details
    function getAgentRegistration(string calldata agentId)
        external view returns (AgentRegistration memory);
    
    // Get anchored action details
    function getAnchoredAction(string calldata actionId)
        external view returns (AnchoredAction memory);
    
    // Check if an agent is registered
    function isAgentRegistered(string calldata agentId)
        external view returns (bool);
    
    // Check if an action is anchored
    function isActionAnchored(string calldata actionId)
        external view returns (bool);
}

contract ChaosEndpoint is IChaosChainEndpoint {
    // Counter for proposal IDs
    uint256 private _nextProposalId = 1;
    
    // Mapping from proposal ID to proposal details
    mapping(uint256 => Proposal) private _proposals;
    
    // Mapping from agent ID to agent registration details
    mapping(string => AgentRegistration) private _agentRegistrations;
    
    // Mapping from action ID to anchored action details
    mapping(string => AnchoredAction) private _anchoredActions;
    
    // Set of registered agent IDs
    mapping(string => bool) private _registeredAgents;
    
    // Set of anchored action IDs
    mapping(string => bool) private _anchoredActionIds;
    
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
     * @dev Register a new agent
     * @param agentId Unique identifier for the agent
     * @param metadataURI IPFS or HTTP URI containing agent metadata
     * @param attestation TEE attestation proving the agent's integrity
     * @return success Whether the registration was successful
     */
    function registerAgent(
        string calldata agentId,
        string calldata metadataURI,
        bytes calldata attestation
    ) external override returns (bool success) {
        // Ensure agent ID is not empty
        require(bytes(agentId).length > 0, "Agent ID cannot be empty");
        
        // Ensure agent is not already registered
        require(!_registeredAgents[agentId], "Agent already registered");
        
        // Create and store the agent registration
        _agentRegistrations[agentId] = AgentRegistration({
            agentId: agentId,
            registrar: msg.sender,
            metadataURI: metadataURI,
            attestation: attestation,
            timestamp: block.timestamp
        });
        
        // Mark agent as registered
        _registeredAgents[agentId] = true;
        
        // Emit the event
        emit AgentRegistered(
            agentId,
            msg.sender,
            metadataURI,
            attestation
        );
        
        return true;
    }
    
    /**
     * @dev Anchor an action in the blockchain
     * @param actionId Unique identifier for the action
     * @param agentId ID of the agent that performed the action
     * @param actionType Type of the action (e.g., ANALYZE, CREATE)
     * @param metadataURI IPFS or HTTP URI containing action metadata
     * @param attestation TEE attestation proving the action's integrity
     * @return success Whether the anchoring was successful
     */
    function anchorAction(
        string calldata actionId,
        string calldata agentId,
        string calldata actionType,
        string calldata metadataURI,
        bytes calldata attestation
    ) external override returns (bool success) {
        // Ensure action ID is not empty
        require(bytes(actionId).length > 0, "Action ID cannot be empty");
        
        // Ensure action is not already anchored
        require(!_anchoredActionIds[actionId], "Action already anchored");
        
        // Ensure agent is registered
        require(_registeredAgents[agentId], "Agent not registered");
        
        // Create and store the anchored action
        _anchoredActions[actionId] = AnchoredAction({
            actionId: actionId,
            agentId: agentId,
            actionType: actionType,
            metadataURI: metadataURI,
            attestation: attestation,
            timestamp: block.timestamp,
            hasOutcome: false,
            outcomeURI: ""
        });
        
        // Mark action as anchored
        _anchoredActionIds[actionId] = true;
        
        // Emit the event
        emit ActionAnchored(
            actionId,
            agentId,
            actionType,
            metadataURI,
            attestation
        );
        
        return true;
    }
    
    /**
     * @dev Record an outcome for an anchored action
     * @param actionId ID of the anchored action
     * @param outcomeURI IPFS or HTTP URI containing outcome metadata
     * @return success Whether the outcome recording was successful
     */
    function recordOutcome(
        string calldata actionId,
        string calldata outcomeURI
    ) external override returns (bool success) {
        // Ensure action ID is not empty
        require(bytes(actionId).length > 0, "Action ID cannot be empty");
        
        // Ensure action is anchored
        require(_anchoredActionIds[actionId], "Action not anchored");
        
        // Ensure action does not already have an outcome
        require(!_anchoredActions[actionId].hasOutcome, "Action already has an outcome");
        
        // Update the anchored action with the outcome
        _anchoredActions[actionId].hasOutcome = true;
        _anchoredActions[actionId].outcomeURI = outcomeURI;
        
        return true;
    }
    
    /**
     * @dev Distribute rewards for an action
     * @param actionId ID of the anchored action
     * @param recipientsData JSON string containing recipient addresses and amounts
     * @return success Whether the reward distribution was successful
     */
    function distributeRewards(
        string calldata actionId,
        string calldata recipientsData
    ) external override returns (bool success) {
        // Ensure action ID is not empty
        require(bytes(actionId).length > 0, "Action ID cannot be empty");
        
        // Ensure action is anchored
        require(_anchoredActionIds[actionId], "Action not anchored");
        
        // Ensure action has an outcome
        require(_anchoredActions[actionId].hasOutcome, "Action does not have an outcome");
        
        // Emit the event
        emit RewardsDistributed(
            actionId,
            msg.sender,
            recipientsData
        );
        
        return true;
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
    
    /**
     * @dev Retrieve an agent registration by ID
     * @param agentId The ID of the agent to retrieve
     * @return The agent registration details
     */
    function getAgentRegistration(string calldata agentId)
        external view override returns (AgentRegistration memory) {
        require(_registeredAgents[agentId], "Agent not registered");
        return _agentRegistrations[agentId];
    }
    
    /**
     * @dev Retrieve an anchored action by ID
     * @param actionId The ID of the action to retrieve
     * @return The anchored action details
     */
    function getAnchoredAction(string calldata actionId)
        external view override returns (AnchoredAction memory) {
        require(_anchoredActionIds[actionId], "Action not anchored");
        return _anchoredActions[actionId];
    }
    
    /**
     * @dev Check if an agent is registered
     * @param agentId The ID of the agent to check
     * @return Whether the agent is registered
     */
    function isAgentRegistered(string calldata agentId)
        external view override returns (bool) {
        return _registeredAgents[agentId];
    }
    
    /**
     * @dev Check if an action is anchored
     * @param actionId The ID of the action to check
     * @return Whether the action is anchored
     */
    function isActionAnchored(string calldata actionId)
        external view override returns (bool) {
        return _anchoredActionIds[actionId];
    }
} 