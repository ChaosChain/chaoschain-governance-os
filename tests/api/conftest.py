"""
Pytest fixtures for API tests.
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from chaoscore.core.db.sqlite_adapter import SQLiteAdapter
from chaoscore.core.database_adapter import (
    PostgreSQLAgentRegistry,
    PostgreSQLProofOfAgency,
    PostgreSQLReputationSystem
)
from chaoscore.core.studio import InMemoryStudioManager
from chaoscore.core.secure_execution import InMemorySecureExecution


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set environment variables for testing
    os.environ["CHAOSCORE_ENV"] = "test"
    os.environ["SQLITE_TEST_MODE"] = "true"
    os.environ["SGX_MOCK"] = "true"
    os.environ["ETHEREUM_MOCK"] = "true"
    
    yield
    
    # Clean up environment variables
    # (commented out to avoid affecting other tests)
    # os.environ.pop("CHAOSCORE_ENV", None)
    # os.environ.pop("SQLITE_TEST_MODE", None)
    # os.environ.pop("SGX_MOCK", None)
    # os.environ.pop("ETHEREUM_MOCK", None)


@pytest.fixture
def sqlite_db():
    """Create an in-memory SQLite database for testing."""
    db = SQLiteAdapter()
    db.create_tables()
    yield db
    db.close()


@pytest.fixture
def agent_registry(sqlite_db):
    """Create an agent registry with SQLite backend for testing."""
    return PostgreSQLAgentRegistry(sqlite_db)


@pytest.fixture
def proof_of_agency(sqlite_db):
    """Create a proof of agency with SQLite backend for testing."""
    return PostgreSQLProofOfAgency(sqlite_db)


@pytest.fixture
def reputation_system(sqlite_db):
    """Create a reputation system with SQLite backend for testing."""
    return PostgreSQLReputationSystem(sqlite_db)


@pytest.fixture
def studio_manager():
    """Create an in-memory studio manager for testing."""
    return InMemoryStudioManager()


@pytest.fixture
def secure_execution():
    """Create an in-memory secure execution environment for testing."""
    return InMemorySecureExecution()


@pytest.fixture
def api_client(sqlite_db, agent_registry, proof_of_agency, reputation_system, studio_manager, secure_execution):
    """Create a test client for the FastAPI application."""
    # We need to patch the dependencies before importing the app
    with patch("chaoscore.core.database_adapter.get_database_adapter", return_value=sqlite_db):
        with patch("api_gateway.main.agent_registry", agent_registry):
            with patch("api_gateway.main.proof_of_agency", proof_of_agency):
                with patch("api_gateway.main.reputation_system", reputation_system):
                    with patch("api_gateway.main.studio_manager", studio_manager):
                        with patch("api_gateway.main.secure_execution", secure_execution):
                            # Now we can import the app
                            from api_gateway.main import app
                            
                            # Create a test client
                            with TestClient(app) as client:
                                yield client 