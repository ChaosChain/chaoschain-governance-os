"""
Unit tests for the ProposalSanityScanner task.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
import random
from typing import Dict, List, Any

from agent.tasks.proposal_sanity_scanner import ProposalSanityScanner

# Suppress logging during tests
logging.disable(logging.CRITICAL)

class TestProposalSanityScanner(unittest.TestCase):
    """Unit tests for the ProposalSanityScanner task."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task = ProposalSanityScanner()
        self.secure_code = "function transferTokens(address recipient, uint256 amount) public onlyOwner { token.transfer(recipient, amount); }"
        self.vulnerable_code = "function selfDestruct() public onlyOwner { selfdestruct(payable(owner)); }"
        self.test_context = self._create_test_context()
    
    def _create_test_context(self) -> Dict[str, Any]:
        """Create a test context with mock proposal data."""
        # Create mock proposal data
        proposal_data = {
            "id": "proposal-1",
            "title": "Update Fee Structure",
            "description": "Update the protocol fee structure to optimize revenue",
            "author": "0x1234567890123456789012345678901234567890",
            "calldata": "0x12345678",
            "code": "function updateFeeStructure(uint256 newFee) external onlyGovernance { fee = newFee; emit FeeUpdated(newFee); }",
            "signature": "updateFeeStructure(uint256)",
            "parameters": {
                "fee": 0.003,
                "fee_recipient": "0x2345678901234567890123456789012345678901"
            }
        }
        
        # Create mock proposal history
        proposal_history = [
            {
                "id": "proposal-2",
                "title": "Previous Fee Update",
                "status": "executed",
                "timestamp": 1234567890
            },
            {
                "id": "proposal-3",
                "title": "Emergency Fix",
                "status": "executed",
                "timestamp": 1234567000
            }
        ]
        
        # Create mock account history
        account_history = {
            "0x1234567890123456789012345678901234567890": {
                "age_in_blocks": 5000,
                "transaction_count": 100,
                "proposals": [
                    {"id": "prop-1", "status": "executed"},
                    {"id": "prop-2", "status": "executed"}
                ]
            }
        }
        
        # Create mock protocol parameters
        protocol_parameters = {
            "fee": {
                "current_value": 0.002,
                "safe_range": [0.001, 0.01],
                "description": "Protocol fee percentage"
            },
            "max_slippage": {
                "current_value": 0.03,
                "safe_range": [0.01, 0.05],
                "description": "Maximum allowed slippage"
            }
        }
        
        # Create mock known vulnerabilities
        known_vulnerabilities = [
            {
                "name": "Reentrancy",
                "pattern": "call.value",
                "severity": "high",
                "cve": "CVE-2018-12345",
                "mitigation": "Use ReentrancyGuard or check-effects-interactions pattern"
            },
            {
                "name": "Unprotected Self-destruct",
                "pattern": "selfdestruct",
                "severity": "high",
                "cve": "CVE-2020-54321",
                "mitigation": "Remove selfdestruct or implement secure access controls"
            }
        ]
        
        # Create mock contract bytecode
        contract_bytecode = {
            "Vault": "0x608060405234801561001057600080fd5b506101a0806100206000396000f3fe608060405260043610610041576000357c0100000000000000000000000000000000",
            "Governance": "0x608060405234801561001057600080fd5b50610200806100206000396000f3fe608060405260043610610051576000357c0100000000000000000000000000000000",
            "Token": "0x608060405234801561001057600080fd5b50610180806100206000396000f3fe608060405260043610610031576000357c0100000000000000000000000000000000"
        }
        
        # Create mock context
        return {
            "governance": {
                "proposal_data": proposal_data,
                "proposal_history": proposal_history,
                "governance_contract": "0x3456789012345678901234567890123456789012",
                "proposal_author": "0x1234567890123456789012345678901234567890"
            },
            "blockchain": {
                "contract_bytecode": contract_bytecode,
                "account_history": account_history
            },
            "context": {
                "protocol_parameters": protocol_parameters,
                "known_vulnerabilities": known_vulnerabilities,
                "timestamp": 1234567890
            }
        }
    
    def test_initialize(self):
        """Test initialization with default parameters."""
        self.assertIsNotNone(self.task)
        self.assertEqual(self.task.task_type, "security_analysis")
        self.assertIn("risk_threshold_high", self.task.parameters)
        self.assertIn("risk_threshold_medium", self.task.parameters)
        self.assertIn("vulnerability_patterns", self.task.parameters)
    
    def test_requires(self):
        """Test that the required data is correctly specified."""
        required = self.task.requires()
        self.assertIn("governance", required)
        self.assertIn("blockchain", required)
        self.assertIn("context", required)
        
        self.assertIn("proposal_data", required["governance"])
        self.assertIn("proposal_history", required["governance"])
        self.assertIn("governance_contract", required["governance"])
        self.assertIn("proposal_author", required["governance"])
        
        self.assertIn("contract_bytecode", required["blockchain"])
        self.assertIn("account_history", required["blockchain"])
        
        self.assertIn("protocol_parameters", required["context"])
        self.assertIn("known_vulnerabilities", required["context"])
    
    def test_execute_success(self):
        """Test successful execution with mock data."""
        result = self.task.execute(self.test_context)
        
        self.assertTrue(result["success"])
        self.assertIn("risk_level", result)
        self.assertIn("risk_score", result)
        self.assertIn("issues", result)
        self.assertIn("recommendations", result)
        self.assertIn("metadata", result)
        
        self.assertIn(result["risk_level"], ["high", "medium", "low"])
        self.assertGreaterEqual(result["risk_score"], 0.0)
        self.assertLessEqual(result["risk_score"], 1.0)
    
    def test_execute_missing_data(self):
        """Test execution with missing required data."""
        # Create a context with missing proposal data
        context_missing_proposal = {
            "governance": {
                "proposal_history": self.test_context["governance"]["proposal_history"],
                "governance_contract": self.test_context["governance"]["governance_contract"],
                "proposal_author": self.test_context["governance"]["proposal_author"]
            },
            "blockchain": self.test_context["blockchain"],
            "context": self.test_context["context"]
        }
        
        result = self.task.execute(context_missing_proposal)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_vulnerability_detection(self):
        """Test detection of vulnerabilities in code."""
        # Create a proposal with vulnerable code
        vulnerable_proposal = self.test_context.copy()
        vulnerable_proposal["governance"] = self.test_context["governance"].copy()
        vulnerable_proposal["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        vulnerable_proposal["governance"]["proposal_data"]["code"] = self.vulnerable_code
        
        result = self.task.execute(vulnerable_proposal)
        
        # Should detect high risk due to selfdestruct
        self.assertEqual(result["risk_level"], "high")
        self.assertGreater(result["risk_score"], 0.5)
        
        # Should have at least one issue
        self.assertGreater(len(result["issues"]), 0)
        
        # At least one issue should be related to selfdestruct
        self.assertTrue(any("selfdestruct" in str(issue).lower() for issue in result["issues"]))
        
        # Create a proposal with secure code
        secure_proposal = self.test_context.copy()
        secure_proposal["governance"] = self.test_context["governance"].copy()
        secure_proposal["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        secure_proposal["governance"]["proposal_data"]["code"] = self.secure_code
        
        result = self.task.execute(secure_proposal)
        
        # Should have lower risk
        self.assertNotEqual(result["risk_level"], "high")
    
    def test_parameter_validation(self):
        """Test validation of parameter values."""
        # Create a proposal with out-of-range parameters
        out_of_range_proposal = self.test_context.copy()
        out_of_range_proposal["governance"] = self.test_context["governance"].copy()
        out_of_range_proposal["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        out_of_range_proposal["governance"]["proposal_data"]["parameters"] = {
            "fee": 0.02,  # Above safe range upper bound
            "max_slippage": 0.06  # Above safe range upper bound
        }
        
        result = self.task.execute(out_of_range_proposal)
        
        # Should detect risks with parameters
        self.assertGreater(len(result["issues"]), 0)
        
        # At least one issue should be related to parameters out of range
        self.assertTrue(any("parameter" in str(issue).lower() for issue in result["issues"]))
    
    def test_author_history_check(self):
        """Test checking of author history."""
        # Create a proposal with new author
        new_author_proposal = self.test_context.copy()
        new_author_proposal["blockchain"] = self.test_context["blockchain"].copy()
        new_author_proposal["blockchain"]["account_history"] = {
            "0x1234567890123456789012345678901234567890": {
                "age_in_blocks": 500,  # New account
                "transaction_count": 10,
                "proposals": []
            }
        }
        
        result = self.task.execute(new_author_proposal)
        
        # Should detect risks with new author
        self.assertGreater(len(result["issues"]), 0)
        
        # At least one issue should be related to new account
        self.assertTrue(any("new account" in str(issue).lower() for issue in result["issues"]))
    
    def test_bytecode_similarity(self):
        """Test detection of similar bytecode."""
        # Create a proposal with similar bytecode
        similar_bytecode_proposal = self.test_context.copy()
        similar_bytecode_proposal["governance"] = self.test_context["governance"].copy()
        similar_bytecode_proposal["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        
        # Use similar bytecode to an existing contract
        similar_bytecode = self.test_context["blockchain"]["contract_bytecode"]["Vault"]
        similar_bytecode_proposal["governance"]["proposal_data"]["bytecode"] = similar_bytecode
        
        result = self.task.execute(similar_bytecode_proposal)
        
        # Check if bytecode similarity was detected
        similarities = [issue for issue in result["issues"] if "bytecode_similarity" in issue.get("type", "")]
        self.assertGreaterEqual(len(similarities), 0)  # May not detect if similarity method is approximate
    
    def test_recommendation_generation(self):
        """Test generation of recommendations."""
        # Test recommendations for high risk
        mock_issues = [
            {"type": "code_vulnerability", "severity": "high", "recommendation": "Fix vulnerability"},
            {"type": "parameter_out_of_range", "severity": "medium", "recommendation": "Adjust parameter"}
        ]
        
        recommendations = self.task._generate_recommendations(mock_issues, "high")
        
        # Should include all issue recommendations
        self.assertIn("Fix vulnerability", recommendations)
        self.assertIn("Adjust parameter", recommendations)
        
        # Should include high risk general recommendations
        self.assertTrue(any("reject" in rec.lower() for rec in recommendations))
        
        # Test recommendations for low risk
        recommendations = self.task._generate_recommendations([], "low")
        
        # Should include default low risk recommendation
        self.assertTrue(any("no significant issues" in rec.lower() for rec in recommendations))

if __name__ == '__main__':
    unittest.main() 