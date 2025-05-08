"""
Tests for the Phala TEE attestation stub.
"""

import pytest
import json
from verification.tee import PhalaAttestationStub


@pytest.fixture
def attestation_stub():
    """
    Create a PhalaAttestationStub instance for testing.
    
    Returns:
        PhalaAttestationStub instance
    """
    return PhalaAttestationStub(enclave_id="test-enclave-123")


@pytest.fixture
def sample_payload():
    """
    Create a sample payload for testing.
    
    Returns:
        Sample payload
    """
    return {
        "proposal_id": 42,
        "title": "Test Proposal",
        "parameters": {
            "gas_adjustment": 1.1,
            "fee_adjustment": 0.9
        }
    }


def test_attestation_stub_initialization():
    """Test that the PhalaAttestationStub initializes correctly."""
    # Test with default enclave ID generation
    stub1 = PhalaAttestationStub()
    assert stub1.enclave_id.startswith("enclave-")
    assert len(stub1.enclave_key) == 32
    
    # Test with provided enclave ID
    stub2 = PhalaAttestationStub(enclave_id="custom-enclave-id")
    assert stub2.enclave_id == "custom-enclave-id"
    assert len(stub2.enclave_key) == 32


def test_attestation_generation(attestation_stub, sample_payload):
    """Test attestation generation for a payload."""
    attestation = attestation_stub.generate_attestation(sample_payload)
    
    # Check that the attestation has the expected fields
    assert "enclave_id" in attestation
    assert attestation["enclave_id"] == "test-enclave-123"
    assert "payload_hash" in attestation
    assert "signature" in attestation
    assert "timestamp" in attestation
    
    # Calculate expected payload hash
    payload_json = json.dumps(sample_payload, sort_keys=True)
    import hashlib
    expected_hash = hashlib.sha256(payload_json.encode()).hexdigest()
    
    # Check that the hash matches
    assert attestation["payload_hash"] == expected_hash


def test_attestation_verification(attestation_stub, sample_payload):
    """Test attestation verification."""
    # Generate an attestation
    attestation = attestation_stub.generate_attestation(sample_payload)
    
    # Verify it against the original payload
    result = PhalaAttestationStub.verify_attestation(attestation, sample_payload)
    assert result is True
    
    # Verify it fails with a modified payload
    modified_payload = sample_payload.copy()
    modified_payload["title"] = "Modified Title"
    result = PhalaAttestationStub.verify_attestation(attestation, modified_payload)
    assert result is False


def test_attestation_uniqueness(sample_payload):
    """Test that attestations are unique for different enclaves."""
    stub1 = PhalaAttestationStub(enclave_id="enclave-1")
    stub2 = PhalaAttestationStub(enclave_id="enclave-2")
    
    attestation1 = stub1.generate_attestation(sample_payload)
    attestation2 = stub2.generate_attestation(sample_payload)
    
    # Same payload hash but different signatures and enclave IDs
    assert attestation1["payload_hash"] == attestation2["payload_hash"]
    assert attestation1["signature"] != attestation2["signature"]
    assert attestation1["enclave_id"] != attestation2["enclave_id"] 