"""
Test for successful anchoring responses
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from examples.sdk_gateway_demo_http import anchor_to_ethereum


class TestAnchoringSuccess(unittest.TestCase):
    """Test cases for successful anchoring responses."""

    @patch('examples.sdk_gateway_demo_http.requests.post')
    @patch('examples.sdk_gateway_demo_http.requests.get')
    @patch('examples.sdk_gateway_demo_http.time.sleep')
    def test_200_success_response(self, mock_sleep, mock_get, mock_post):
        """Test that a 200 response with is_mock=false is treated as success."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tx_hash": "0xabc123def456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "block_number": 12345678,
            "network": "sepolia",
            "is_mock": False,
            "action_id": "action-test-123",
            "status": "confirmed"
        }
        mock_post.return_value = mock_response
        
        # Mock the Etherscan response
        mock_etherscan = MagicMock()
        mock_etherscan.status_code = 200
        mock_get.return_value = mock_etherscan
        
        # Call the function
        result = anchor_to_ethereum(
            hash_value="dummy_hash",
            use_staging=True,
            network="sepolia",
            action_id="action-test-123",
            token="dummy_token"
        )
        
        # Verify the result
        self.assertEqual(
            result,
            "0xabc123def456789abcdef0123456789abcdef0123456789abcdef0123456789"
        )
        # Verify the API was called with the expected parameters
        mock_post.assert_called_once()
        # Verify Etherscan was polled
        mock_get.assert_called()

    @patch('examples.sdk_gateway_demo_http.requests.post')
    @patch('examples.sdk_gateway_demo_http.requests.get')
    @patch('examples.sdk_gateway_demo_http.time.sleep')
    def test_mock_response_handling(self, mock_sleep, mock_get, mock_post):
        """Test that a response with is_mock=true returns the error token."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tx_hash": "0xabc123def456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "block_number": 12345678,
            "network": "sepolia",
            "is_mock": True,  # This should cause the function to return ERROR-ANCHORING-FAILED
            "action_id": "action-test-123",
            "status": "confirmed"
        }
        mock_post.return_value = mock_response
        
        # Call the function
        result = anchor_to_ethereum(
            hash_value="dummy_hash",
            use_staging=True,
            network="sepolia",
            action_id="action-test-123",
            token="dummy_token"
        )
        
        # Verify the result
        self.assertEqual(result, "ERROR-ANCHORING-FAILED")
        # Verify the API was called
        mock_post.assert_called_once()
        # Verify Etherscan was NOT polled (since it was a mock transaction)
        mock_get.assert_not_called()

    @patch('examples.sdk_gateway_demo_http.requests.post')
    @patch('examples.sdk_gateway_demo_http.requests.get')
    @patch('examples.sdk_gateway_demo_http.time.sleep')
    def test_missing_0x_prefix(self, mock_sleep, mock_get, mock_post):
        """Test that a transaction hash without 0x prefix gets fixed."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tx_hash": "abc123def456789abcdef0123456789abcdef0123456789abcdef0123456789",  # No 0x prefix
            "block_number": 12345678,
            "network": "sepolia",
            "is_mock": False,
            "action_id": "action-test-123",
            "status": "confirmed"
        }
        mock_post.return_value = mock_response
        
        # Mock the Etherscan response
        mock_etherscan = MagicMock()
        mock_etherscan.status_code = 200
        mock_get.return_value = mock_etherscan
        
        # Call the function
        result = anchor_to_ethereum(
            hash_value="dummy_hash",
            use_staging=True,
            network="sepolia",
            action_id="action-test-123",
            token="dummy_token"
        )
        
        # Verify the result has 0x prefix added
        self.assertEqual(
            result,
            "0xabc123def456789abcdef0123456789abcdef0123456789abcdef0123456789"
        )
        # Verify the API was called
        mock_post.assert_called_once()
        # Verify Etherscan was polled with the corrected hash
        mock_get.assert_called()


if __name__ == '__main__':
    unittest.main() 