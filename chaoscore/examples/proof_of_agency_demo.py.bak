#!/usr/bin/env python3
"""
Proof of Agency and Secure Execution Demo

This script demonstrates the Proof of Agency framework and Secure Execution Environment
working together to create verifiable agent actions with attestations.
"""
import time
import json
from datetime import datetime

from chaoscore.core.agent_registry import InMemoryAgentRegistry
from chaoscore.core.proof_of_agency import (
    ActionType,
    InMemoryProofOfAgency
)
from chaoscore.core.secure_execution import (
    MockSecureExecutionEnvironment
)


def print_separator(title=None):
    """Print a separator with an optional title."""
    width = 80
    if title:
        print(f"\n{'-' * 10} {title} {'-' * (width - 12 - len(title))}")
    else:
        print("\n" + "-" * width)


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def main():
    """Run the demo."""
    print_separator("PROOF OF AGENCY & SECURE EXECUTION DEMO")
    print("This demo shows how the Proof of Agency framework and Secure Execution Environment")
    print("work together to create verifiable agent actions with attestations.")
    
    # Step 1: Create and initialize components
    print_separator("STEP 1: Initialize Components")
    
    # Create an agent registry
    print("Creating Agent Registry...")
    agent_registry = InMemoryAgentRegistry()
    
    # Register agents
    print("Registering agents...")
    researcher_id = agent_registry.register_agent(
        "researcher@chaoscore.ai",
        "Data Researcher",
        {
            "role": "researcher",
            "capabilities": ["data_analysis", "prediction"],
            "organization": "ChaosCore Research"
        }
    )
    
    validator_id = agent_registry.register_agent(
        "validator@chaoscore.ai",
        "Result Validator",
        {
            "role": "validator",
            "capabilities": ["verification", "validation"],
            "organization": "ChaosCore Validation Team"
        }
    )
    
    print(f"Registered researcher agent with ID: {researcher_id}")
    print(f"Registered validator agent with ID: {validator_id}")
    
    # Create Proof of Agency instance
    print("Creating Proof of Agency system...")
    poa = InMemoryProofOfAgency(agent_registry)
    
    # Create Secure Execution Environment
    print("Creating Secure Execution Environment...")
    see = MockSecureExecutionEnvironment()
    
    # Step 2: Define a task to perform
    print_separator("STEP 2: Define Task")
    
    analysis_code = """
import random
from datetime import datetime

# Set a consistent seed for reproducibility
random.seed(42)

# Simulate collecting market data
def collect_market_data(symbols, days_back=30):
    market_data = {}
    for symbol in symbols:
        prices = []
        # Start from a random price between 50 and 200
        current_price = random.uniform(50, 200)
        for _ in range(days_back):
            # Random daily change between -5% and +5%
            daily_change = random.uniform(-0.05, 0.05)
            current_price *= (1 + daily_change)
            prices.append(round(current_price, 2))
        market_data[symbol] = prices
    return market_data

# Analyze market data to find correlations and trends
def analyze_market_data(market_data):
    results = {
        "avg_prices": {},
        "trends": {},
        "volatility": {},
        "correlations": {}
    }
    
    # Calculate average prices
    for symbol, prices in market_data.items():
        results["avg_prices"][symbol] = round(sum(prices) / len(prices), 2)
    
    # Determine trends (up, down, or sideways)
    for symbol, prices in market_data.items():
        if prices[-1] > prices[0] * 1.05:  # 5% increase
            results["trends"][symbol] = "up"
        elif prices[-1] < prices[0] * 0.95:  # 5% decrease
            results["trends"][symbol] = "down"
        else:
            results["trends"][symbol] = "sideways"
    
    # Calculate volatility (standard deviation)
    for symbol, prices in market_data.items():
        mean = sum(prices) / len(prices)
        variance = sum((price - mean) ** 2 for price in prices) / len(prices)
        results["volatility"][symbol] = round((variance ** 0.5) / mean * 100, 2)  # as percentage
    
    # Calculate simple correlations between symbols
    symbols = list(market_data.keys())
    for i, symbol1 in enumerate(symbols):
        for symbol2 in symbols[i+1:]:
            # Calculate Pearson correlation coefficient
            prices1 = market_data[symbol1]
            prices2 = market_data[symbol2]
            
            mean1 = sum(prices1) / len(prices1)
            mean2 = sum(prices2) / len(prices2)
            
            numerator = sum((p1 - mean1) * (p2 - mean2) for p1, p2 in zip(prices1, prices2))
            denom1 = sum((p - mean1) ** 2 for p in prices1) ** 0.5
            denom2 = sum((p - mean2) ** 2 for p in prices2) ** 0.5
            
            correlation = numerator / (denom1 * denom2)
            results["correlations"][f"{symbol1}-{symbol2}"] = round(correlation, 2)
    
    return results

# Make investment recommendations based on analysis
def make_recommendations(analysis_results):
    recommendations = {
        "buy": [],
        "hold": [],
        "sell": []
    }
    
    # Simple recommendation logic based on trends and volatility
    for symbol, trend in analysis_results["trends"].items():
        volatility = analysis_results["volatility"][symbol]
        
        if trend == "up" and volatility < 15:  # Strong uptrend with low volatility
            recommendations["buy"].append(symbol)
        elif trend == "down" and volatility > 20:  # Downtrend with high volatility
            recommendations["sell"].append(symbol)
        else:
            recommendations["hold"].append(symbol)
    
    return recommendations

# Entry point - perform the analysis
def perform_market_analysis(symbols):
    log(f"Starting market analysis for symbols: {symbols}")
    
    # Collect data
    log("Collecting market data...")
    market_data = collect_market_data(symbols)
    
    # Analyze data
    log("Analyzing market data...")
    analysis_results = analyze_market_data(market_data)
    
    # Make recommendations
    log("Generating investment recommendations...")
    recommendations = make_recommendations(analysis_results)
    
    # Prepare final report
    report = {
        "timestamp": datetime.now().isoformat(),
        "symbols_analyzed": symbols,
        "summary": {
            "average_prices": analysis_results["avg_prices"],
            "market_trends": analysis_results["trends"],
            "volatility_metrics": analysis_results["volatility"]
        },
        "recommendations": recommendations,
        "correlation_insights": [
            f"{pair}: {corr}" for pair, corr in analysis_results["correlations"].items() 
            if abs(corr) > 0.7  # Only show strong correlations
        ]
    }
    
    log("Analysis complete.")
    return report

# Execute the analysis
return perform_market_analysis(input_symbols)
"""
    
    print("The researcher agent will perform a market analysis task:")
    print("1. Collect simulated market data for a set of symbols")
    print("2. Analyze the data for trends, volatility, and correlations")
    print("3. Generate investment recommendations")
    print("4. The entire process will be recorded, verified, and attested")
    
    # Step 3: Execute the task in the secure environment
    print_separator("STEP 3: Execute Task in Secure Environment")
    
    symbols = ["BTC", "ETH", "SOL", "AVAX", "DOT"]
    print(f"Executing market analysis for symbols: {symbols}")
    
    # Execute the code in the secure environment
    execution_start = time.time()
    result = see.execute(
        code=analysis_code,
        inputs={"input_symbols": symbols}
    )
    execution_time = time.time() - execution_start
    
    print(f"Execution completed in {execution_time:.2f} seconds")
    print(f"Execution status: {result.get_status().value}")
    
    if result.get_status().name == "SUCCESS":
        # Display a summary of the analysis results
        analysis_report = result.get_outputs()["result"]
        print("\nAnalysis Results Summary:")
        print(f"Symbols analyzed: {', '.join(analysis_report['symbols_analyzed'])}")
        
        print("\nMarket Trends:")
        for symbol, trend in analysis_report["summary"]["market_trends"].items():
            print(f"  {symbol}: {trend.upper()}")
        
        print("\nRecommendations:")
        for action, symbols in analysis_report["recommendations"].items():
            if symbols:
                print(f"  {action.upper()}: {', '.join(symbols)}")
        
        print("\nCorrelation Insights:")
        for insight in analysis_report["correlation_insights"]:
            print(f"  {insight}")
    else:
        print("Execution failed with error:")
        print(result.get_outputs().get("error", "Unknown error"))
    
    # Step 4: Record the action in the Proof of Agency system
    print_separator("STEP 4: Record Action in Proof of Agency")
    
    print("Recording the action...")
    action_id = poa.log_action(
        agent_id=researcher_id,
        action_type=ActionType.ANALYZE,
        description="Market analysis for crypto assets",
        data={
            "symbols": symbols,
            "execution_time": execution_time,
            "code_hash": result.get_attestation().get_code_hash() if result.get_attestation() else None,
            "attestation_id": result.get_attestation().get_id() if result.get_attestation() else None
        }
    )
    
    print(f"Action recorded with ID: {action_id}")
    
    # Step 5: Verify the action
    print_separator("STEP 5: Verify Action")
    
    print(f"Validator agent ({validator_id}) is verifying the action...")
    verification_result = poa.verify_action(action_id, validator_id)
    print(f"Verification result: {verification_result}")
    
    # Step 6: Anchor the action on-chain
    print_separator("STEP 6: Anchor Action On-Chain")
    
    print("Anchoring the verified action on-chain...")
    tx_hash = poa.anchor_action(action_id)
    print(f"Action anchored with transaction hash: {tx_hash}")
    
    # Step 7: Record the outcome
    print_separator("STEP 7: Record Outcome")
    
    print("Recording the outcome of the action...")
    
    # In a real scenario, we would evaluate the impact and success
    # For the demo, we'll assume it was successful with a high impact
    outcome_id = poa.record_outcome(
        action_id=action_id,
        success=True,
        impact_score=0.85,  # High impact
        results={
            "report": result.get_outputs()["result"],
            "verification": {
                "attestation_verified": True,
                "execution_status": result.get_status().value,
                "verifier_id": validator_id
            }
        }
    )
    
    print(f"Outcome recorded for action: {outcome_id}")
    
    # Step 8: Compute and distribute rewards
    print_separator("STEP 8: Compute and Distribute Rewards")
    
    print("Computing rewards for involved agents...")
    rewards = poa.compute_rewards(action_id)
    
    print("Reward distribution:")
    for agent_id, amount in rewards.items():
        agent_role = "researcher" if agent_id == researcher_id else "validator"
        print(f"  {agent_role} ({agent_id}): {amount:.2f} tokens")
    
    print("\nDistributing rewards...")
    distribution_tx = poa.distribute_rewards(action_id)
    print(f"Rewards distributed with transaction hash: {distribution_tx}")
    
    # Step 9: Summary
    print_separator("DEMO SUMMARY")
    
    print("This demo showcased the following components working together:")
    print("1. Agent Registry - for identity management")
    print("2. Secure Execution Environment - for attested code execution")
    print("3. Proof of Agency - for recording, verifying, and rewarding actions")
    
    print("\nThe key benefits demonstrated are:")
    print("- Verifiable agent actions with cryptographic attestations")
    print("- Transparent reward distribution based on contribution")
    print("- Anchoring of critical actions on-chain for permanent record")
    
    print("\nIn a real ChaosCore deployment, these components would be:")
    print("- Connected to actual blockchain networks")
    print("- Using real TEE implementations like Intel SGX")
    print("- Integrated with on-chain governance systems")
    print_separator()


if __name__ == "__main__":
    main() 