"""
Configuration for simulation harness.

Contains default and demo-specific configurations.
"""

from typing import Dict, List, Any

# Demo configuration
DEMO_BLOCK = 5524380  # Specific Ethereum block for demo

# Example transactions for deterministic demo
DEMO_TRANSACTIONS: List[Dict[str, Any]] = [
    {
        "from": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap Router
        "to": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "value": "0x0",
        "gasPrice": "0x12a05f200",  # 5 Gwei
        "gasLimit": "0x55730",  # 350,000
        "gasUsed": "0x36b90",  # 224,144
        "data": "0xa9059cbb000000000000000000000000d8da6bf26964af9d7eed9e03e53415d37aa960450000000000000000000000000000000000000000000000009c377fstring8c4000",
        "nonce": "0x37",
        "hash": "0x82b85f2abe4419930512704a4f38e72181c6fc36fafda19c4c75c48acf400d61",
    },
    {
        "from": "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",  # Uniswap Router v3
        "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        "value": "0x0",
        "gasPrice": "0x12a05f200",  # 5 Gwei
        "gasLimit": "0x2bf20",  # 180,000
        "gasUsed": "0x1d965",  # 120,165
        "data": "0x095ea7b3000000000000000000000000a5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff0000000000000000000000000000000000000000000000000000000000000000",
        "nonce": "0x42",
        "hash": "0xc4c92d07f9c83ba0659eb10a72e4ebe48173d5b3a8ff8c9e1bd8e0bdd4df4bf6",
    },
    {
        "from": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # vitalik.eth
        "to": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",  # UNI token
        "value": "0x0",
        "gasPrice": "0x12a05f200",  # 5 Gwei
        "gasLimit": "0x12bad",  # 76,717
        "gasUsed": "0xc411",  # 50,193
        "data": "0x23b872dd000000000000000000000000d8da6bf26964af9d7eed9e03e53415d37aa960450000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d0000000000000000000000000000000000000000000000000de0b6b3a7640000",
        "nonce": "0x143",
        "hash": "0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
    },
    {
        "from": "0xF1Dc500FdE233A4055e25e5BbF516372BC4F6871",  # Random address
        "to": "0x0000000000000000000000000000000000000000",  # Plain ETH transfer
        "value": "0x2386f26fc10000",  # 0.01 ETH
        "gasPrice": "0x12a05f200",  # 5 Gwei
        "gasLimit": "0x5208",  # 21,000 (standard ETH transfer)
        "gasUsed": "0x5208",  # 21,000
        "data": "0x",
        "nonce": "0x7",
        "hash": "0xb2e9b0a7d7d9770a0c2c37a2c631050a0079a7d9f5c963351c0f8f20d947f248",
    },
    {
        "from": "0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b",  # OpenSea
        "to": "0x3a7dD3ea9E2A0B2F5116211eBfA17952A084B1B0",  # NFT
        "value": "0x0",
        "gasPrice": "0x12a05f200",  # 5 Gwei
        "gasLimit": "0xc6400",  # 812,500
        "gasUsed": "0x74240",  # 476,736
        "data": "0x23b872dd000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d0000000000000000000000007be8076f4ea4a4ad08075c2508e481d6c946d12b0000000000000000000000000000000000000000000000000000000000000220",
        "nonce": "0x81",
        "hash": "0x4b8d7fd94409e50595f03be33df05aa8c1a05a3b5737a5f3c6d19a3dff4b2252",
    },
]

# Default demo proposal
DEMO_PROPOSAL = {
    "title": "EIP-1559 Parameter Adjustment",
    "description": "Adjust the base fee parameters to improve gas price predictability during network congestion",
    "chain_id": 1,
    "parameters": {
        "gas_adjustment": 0.88,  # -12% gas usage
        "fee_adjustment": 1.032,  # +3.2% fee growth (32 basis points)
        "target_block_utilization": 0.85,
        "adjustment_quotient": 8,
    }
}

# Demo simulation configuration
DEMO_SIMULATION_CONFIG = {
    "transaction_count": len(DEMO_TRANSACTIONS),
    "gas_limit": 12500000,  # 12.5M gas
    "base_fee_per_gas": 5 * 10**9,  # 5 Gwei
    "fee_denominator": 8,
    "use_predefined_transactions": True  # Flag to use the demo transactions
} 