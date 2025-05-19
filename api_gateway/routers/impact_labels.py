"""
Impact Labels API Router

This module provides endpoints for generating impact labels for governance analysis receipts.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Local imports
from api_gateway.auth.jwt_auth import get_current_agent_id
from api_gateway.dependencies import get_db_adapter
from api_gateway.metrics import start_timer, end_timer

# Set up router
router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---

class ImpactLabelRequest(BaseModel):
    """Request model for generating impact labels."""
    
    task_output: Dict[str, Any]
    task_type: str
    network: str = "sepolia"
    anchor_ethereum: bool = True


class ImpactLabelResponse(BaseModel):
    """Response model for impact labels."""
    
    impact_score: float
    impact_level: str
    impact_areas: List[str]
    labels: List[str]
    markdown_summary: Optional[str] = None
    etherscan_url: Optional[str] = None
    receipt_tx_hash: Optional[str] = None
    timestamp: int


# --- Routes ---

@router.post("", response_model=ImpactLabelResponse, status_code=status.HTTP_201_CREATED)
async def generate_impact_labels(
    request: ImpactLabelRequest,
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Generate impact labels for a governance analysis task.
    
    Args:
        request: Impact label request
        current_agent_id: ID of the authenticated agent
        
    Returns:
        Impact label response
    """
    timer = start_timer()
    
    try:
        # Extract task output
        task_output = request.task_output
        task_type = request.task_type
        
        # Calculate impact score based on task type
        impact_score = 0.0
        impact_level = "low"
        impact_areas = []
        labels = []
        
        if task_type == "ProposalSanityScanner" or task_type == "ProposalAnalysis":
            # Extract risk information
            risk_score = task_output.get("risk_score", 0.0)
            risk_level = task_output.get("risk_level", "unknown")
            issues = task_output.get("issues", [])
            
            # Calculate impact score
            impact_score = 1.0 - risk_score  # Invert risk score (higher risk = lower positive impact)
            
            # Determine impact level
            if impact_score >= 0.7:
                impact_level = "high"
            elif impact_score >= 0.4:
                impact_level = "medium"
            else:
                impact_level = "low"
            
            # Determine impact areas
            if issues:
                # Count issue types
                issue_types = {}
                for issue in issues:
                    issue_type = issue.get("type", "unknown")
                    issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
                
                # Map issue types to impact areas
                if any(t in issue_types for t in ["size_limit", "high_bytecode_similarity"]):
                    impact_areas.append("complexity")
                if any(t in issue_types for t in ["code_vulnerability", "known_vulnerability"]):
                    impact_areas.append("security")
                if any(t in issue_types for t in ["parameter_out_of_range", "high_rejection_rate"]):
                    impact_areas.append("governance")
            
            # Generate labels
            if impact_level == "high":
                labels.append("Safe Proposal")
            elif risk_level == "high":
                labels.append("High Risk Proposal")
            
            if "security" in impact_areas:
                labels.append("Security Concerns")
            if "complexity" in impact_areas:
                labels.append("Complex Proposal")
        
        elif task_type == "MEVCostEstimator":
            # Extract MEV information
            risk_score = task_output.get("risk_score", 0.0)
            risk_level = task_output.get("risk_level", "unknown")
            mev_vectors = task_output.get("mev_vectors", {})
            
            # Calculate impact score
            impact_score = 1.0 - risk_score  # Invert risk score (higher risk = lower positive impact)
            
            # Determine impact level
            if impact_score >= 0.7:
                impact_level = "high"
            elif impact_score >= 0.4:
                impact_level = "medium"
            else:
                impact_level = "low"
            
            # Determine impact areas
            if "sandwich_attacks" in mev_vectors and mev_vectors["sandwich_attacks"].get("risk_score", 0) > 0.5:
                impact_areas.append("trading")
            if "frontrunning" in mev_vectors and mev_vectors["frontrunning"].get("risk_score", 0) > 0.5:
                impact_areas.append("fairness")
            if "liquidations" in mev_vectors and mev_vectors["liquidations"].get("risk_score", 0) > 0.5:
                impact_areas.append("liquidations")
            
            # Generate labels
            if impact_level == "high":
                labels.append("MEV Resistant")
            elif risk_level == "high":
                labels.append("High MEV Exposure")
            
            if "trading" in impact_areas:
                labels.append("Trading Impact")
            if "fairness" in impact_areas:
                labels.append("Fairness Concerns")
        
        elif task_type == "GasParameterOptimizer":
            # Extract optimization information
            optimization_score = task_output.get("optimization_score", 0.0)
            recommended_params = task_output.get("recommended_parameters", {})
            
            # Calculate impact score
            impact_score = optimization_score
            
            # Determine impact level
            if impact_score >= 0.7:
                impact_level = "high"
            elif impact_score >= 0.4:
                impact_level = "medium"
            else:
                impact_level = "low"
            
            # Determine impact areas
            impact_areas.append("gas_efficiency")
            if recommended_params.get("base_fee_change_pct", 0) > 10:
                impact_areas.append("fee_structure")
            
            # Generate labels
            if impact_level == "high":
                labels.append("Highly Optimized")
            if "fee_structure" in impact_areas:
                labels.append("Fee Structure Changes")
        
        # Get markdown summary if available
        markdown_summary = task_output.get("markdown_summary")
        
        # Get or generate receipt transaction hash
        # In a real implementation, this would submit the analysis to Ethereum
        receipt_tx_hash = task_output.get("receipt_tx_hash")
        if not receipt_tx_hash and request.anchor_ethereum:
            # Mock transaction hash for demonstration
            receipt_tx_hash = "0x" + "0" * 64  # This would be a real tx hash
        
        # Generate Etherscan URL
        etherscan_url = None
        if receipt_tx_hash:
            network = request.network.lower()
            base_urls = {
                "mainnet": "https://etherscan.io",
                "goerli": "https://goerli.etherscan.io",
                "sepolia": "https://sepolia.etherscan.io"
            }
            base_url = base_urls.get(network, base_urls["sepolia"])
            etherscan_url = f"{base_url}/tx/{receipt_tx_hash}"
        
        # Create response
        response = {
            "impact_score": impact_score,
            "impact_level": impact_level,
            "impact_areas": impact_areas,
            "labels": labels,
            "markdown_summary": markdown_summary,
            "etherscan_url": etherscan_url,
            "receipt_tx_hash": receipt_tx_hash,
            "timestamp": task_output.get("timestamp", 0)
        }
        
        end_timer(timer, "impact_labels_generation")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate impact labels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate impact labels: {e}"
        ) 