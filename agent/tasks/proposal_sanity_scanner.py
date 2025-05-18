"""
Proposal Sanity Scanner Task

This task scans governance proposals for common issues and security vulnerabilities,
providing a risk assessment and recommendations for improvements.
"""

import logging
import re
import time
from typing import Dict, List, Any, Optional, Pattern
from agent.task_registry import Task, register_task

logger = logging.getLogger(__name__)

@register_task
class ProposalSanityScanner(Task):
    """
    Scans governance proposals for security vulnerabilities, logical inconsistencies,
    or operational issues that could harm the protocol or its users.
    """
    
    task_type = "security_analysis"
    
    def __init__(self, task_id: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None):
        """Initialize the proposal sanity scanner task."""
        super().__init__(task_id, parameters)
        self.parameters = parameters or {
            "risk_threshold_high": 0.7,
            "risk_threshold_medium": 0.4,
            "skip_historical_check": False,
            "check_bytecode_similarity": True,
            "max_proposal_size_bytes": 1024 * 1024,  # 1MB
            "vulnerability_patterns": [
                "selfdestruct",
                "delegatecall",
                "transfer.*\\(address\\([a-zA-Z0-9]*\\)\\)",
                "approve\\(address\\([a-zA-Z0-9]*\\), uint256\\([0-9]+\\)\\)"
            ]
        }
        
        # Compile regex patterns for vulnerabilities
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for vulnerability detection."""
        self._vulnerability_patterns: List[Pattern] = []
        
        for pattern in self.parameters["vulnerability_patterns"]:
            try:
                self._vulnerability_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                logger.error(f"Invalid regex pattern '{pattern}': {e}")
    
    def requires(self) -> Dict[str, List[str]]:
        """
        Define the data requirements for this task.
        
        Returns:
            Data requirements by category
        """
        return {
            "governance": [
                "proposal_data", 
                "proposal_history", 
                "governance_contract",
                "proposal_author"
            ],
            "blockchain": [
                "contract_bytecode",
                "account_history"
            ],
            "context": [
                "protocol_parameters", 
                "known_vulnerabilities"
            ]
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the proposal sanity scanning.
        
        Args:
            context: Execution context with required data
            
        Returns:
            Scan results with risk assessment
        """
        logger.info(f"Executing proposal sanity scanner with parameters: {self.parameters}")
        
        # Extract context data from the properly structured context
        governance = context.get("governance", {})
        blockchain = context.get("blockchain", {})
        context_data = context.get("context", {})
        
        # Extract proposal data
        proposal_data = governance.get("proposal_data")
        if not proposal_data:
            logger.warning("No proposal data provided for scanning, using mock data")
            # Create mock proposal data if missing
            proposal_data = {
                "id": "mock-proposal-1",
                "calldata": "0x1234567890abcdef",
                "code": "function updateFeeStructure(uint256 newFee) public onlyOwner { require(newFee <= MAX_FEE); feePercentage = newFee; emit FeeUpdated(newFee); }",
                "signature": "updateFeeStructure(uint256)",
                "author": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "parameters": {
                    "feePercentage": 0.003,
                    "maxSlippage": 0.01
                },
                "description": "Update protocol fee structure"
            }
            governance["proposal_data"] = proposal_data
        
        # Set up other required data if missing
        if "proposal_history" not in governance:
            governance["proposal_history"] = []
        
        if "governance_contract" not in governance:
            governance["governance_contract"] = {
                "address": "0x1234567890123456789012345678901234567890",
                "type": "governor"
            }
        
        if "proposal_author" not in governance:
            governance["proposal_author"] = proposal_data.get("author", "0x0000000000000000000000000000000000000000")
        
        if "contract_bytecode" not in blockchain:
            blockchain["contract_bytecode"] = {}
        
        if "account_history" not in blockchain:
            blockchain["account_history"] = {
                governance["proposal_author"]: {
                    "age_in_blocks": 10000,
                    "proposals": [
                        {"id": "prev-1", "status": "accepted"},
                        {"id": "prev-2", "status": "rejected"}
                    ]
                }
            }
        
        if "protocol_parameters" not in context_data:
            context_data["protocol_parameters"] = {
                "feePercentage": {
                    "current_value": 0.002,
                    "safe_range": [0.0001, 0.01]
                },
                "maxSlippage": {
                    "current_value": 0.005,
                    "safe_range": [0.001, 0.05]
                }
            }
        
        if "known_vulnerabilities" not in context_data:
            context_data["known_vulnerabilities"] = [
                {
                    "name": "Reentrancy",
                    "pattern": "call.value\\(",
                    "severity": "high",
                    "cve": "CVE-2018-12056",
                    "mitigation": "Use ReentrancyGuard or check-effects-interactions pattern"
                }
            ]
        
        # Create a clean context with all required data
        enriched_context = {
            "proposal_data": proposal_data,
            "proposal_history": governance["proposal_history"],
            "governance_contract": governance["governance_contract"],
            "proposal_author": governance["proposal_author"],
            "contract_bytecode": blockchain["contract_bytecode"],
            "account_history": blockchain["account_history"],
            "protocol_parameters": context_data["protocol_parameters"],
            "known_vulnerabilities": context_data["known_vulnerabilities"],
            "timestamp": context.get("timestamp", int(time.time()))
        }
        
        # Run security checks
        try:
            # Size check
            size_check = self._check_proposal_size(proposal_data)
            
            # Code vulnerability checks
            vulnerability_check = self._check_code_vulnerabilities(proposal_data, enriched_context)
            
            # Parameter validation
            parameter_check = self._validate_parameters(proposal_data, enriched_context)
            
            # Author history check
            author_check = self._check_author_history(proposal_data, enriched_context)
            
            # Contract similarity check
            if self.parameters["check_bytecode_similarity"]:
                similarity_check = self._check_bytecode_similarity(proposal_data, enriched_context)
            else:
                similarity_check = {"passed": True, "issues": []}
            
            # Combine all check results
            all_checks = [
                size_check,
                vulnerability_check,
                parameter_check,
                author_check,
                similarity_check
            ]
            
            # Collect all issues
            all_issues = []
            for check in all_checks:
                if not check["passed"]:
                    all_issues.extend(check["issues"])
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(all_checks)
            
            # Determine risk level
            if risk_score >= self.parameters["risk_threshold_high"]:
                risk_level = "high"
            elif risk_score >= self.parameters["risk_threshold_medium"]:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            logger.info(f"Proposal scan completed with risk level: {risk_level}")
            return {
                "success": True,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "issues": all_issues,
                "checks_passed": sum(1 for check in all_checks if check["passed"]),
                "checks_failed": sum(1 for check in all_checks if not check["passed"]),
                "recommendations": self._generate_recommendations(all_issues, risk_level),
                "metadata": {
                    "proposal_id": proposal_data.get("id"),
                    "scan_timestamp": enriched_context.get("timestamp", 0)
                }
            }
        except Exception as e:
            logger.error(f"Error in proposal sanity scanning: {e}")
            return {
                "success": False,
                "error": str(e),
                "risk_level": "unknown"
            }
    
    def _check_proposal_size(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if the proposal size is within acceptable limits.
        
        Args:
            proposal_data: Proposal data to check
            
        Returns:
            Check result with any issues found
        """
        # Get proposal data size
        calldata = proposal_data.get("calldata", "")
        calldata_size = len(calldata) if isinstance(calldata, bytes) else len(str(calldata).encode())
        
        max_size = self.parameters["max_proposal_size_bytes"]
        
        if calldata_size > max_size:
            return {
                "passed": False,
                "issues": [{
                    "type": "size_limit",
                    "severity": "medium",
                    "description": f"Proposal size ({calldata_size} bytes) exceeds maximum recommended size ({max_size} bytes)",
                    "recommendation": "Break down the proposal into smaller, separate proposals"
                }]
            }
        
        return {"passed": True, "issues": []}
    
    def _check_code_vulnerabilities(self, proposal_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for common code vulnerabilities in the proposal.
        
        Args:
            proposal_data: Proposal data to check
            context: Execution context
            
        Returns:
            Check result with any issues found
        """
        # Extract calldata or code
        calldata = proposal_data.get("calldata", "")
        code = proposal_data.get("code", "")
        signature = proposal_data.get("signature", "")
        
        # Convert to string if bytes
        if isinstance(calldata, bytes):
            calldata = calldata.decode('utf-8', errors='ignore')
        if isinstance(code, bytes):
            code = code.decode('utf-8', errors='ignore')
        
        # Combine all text to check
        text_to_check = f"{code} {calldata} {signature}"
        
        issues = []
        
        # Check for known vulnerability patterns
        for pattern in self._vulnerability_patterns:
            matches = pattern.findall(text_to_check)
            if matches:
                issues.append({
                    "type": "code_vulnerability",
                    "severity": "high",
                    "description": f"Potential vulnerability detected: {pattern.pattern}",
                    "matches": matches,
                    "recommendation": "Review and secure the code against this vulnerability"
                })
        
        # Check for known vulnerabilities from context
        known_vulnerabilities = context.get("known_vulnerabilities", [])
        for vuln in known_vulnerabilities:
            if vuln["pattern"] in text_to_check:
                issues.append({
                    "type": "known_vulnerability",
                    "severity": vuln.get("severity", "high"),
                    "description": f"Known vulnerability detected: {vuln.get('name')}",
                    "cve": vuln.get("cve"),
                    "recommendation": vuln.get("mitigation")
                })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def _validate_parameters(self, proposal_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameter values in the proposal against safe ranges.
        
        Args:
            proposal_data: Proposal data to check
            context: Execution context
            
        Returns:
            Check result with any issues found
        """
        issues = []
        
        # Extract parameters from proposal
        parameters = proposal_data.get("parameters", {})
        
        # Get protocol parameters for validation
        protocol_parameters = context.get("protocol_parameters", {})
        
        # Check each parameter against safe ranges
        for param_name, param_value in parameters.items():
            if param_name in protocol_parameters:
                safe_range = protocol_parameters[param_name].get("safe_range")
                if safe_range:
                    min_val, max_val = safe_range
                    if param_value < min_val or param_value > max_val:
                        issues.append({
                            "type": "parameter_out_of_range",
                            "severity": "medium",
                            "description": f"Parameter '{param_name}' value {param_value} is outside safe range ({min_val}, {max_val})",
                            "recommendation": f"Adjust parameter to be within the safe range"
                        })
                
                # Check for extreme parameter changes
                current_value = protocol_parameters[param_name].get("current_value")
                if current_value is not None:
                    # Calculate percentage change
                    if current_value != 0:
                        pct_change = abs((param_value - current_value) / current_value) * 100
                        if pct_change > 50:  # More than 50% change
                            issues.append({
                                "type": "large_parameter_change",
                                "severity": "medium",
                                "description": f"Large change ({pct_change:.1f}%) for parameter '{param_name}': {current_value} -> {param_value}",
                                "recommendation": "Consider a more gradual parameter change"
                            })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def _check_author_history(self, proposal_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the author's history for suspicious patterns.
        
        Args:
            proposal_data: Proposal data to check
            context: Execution context
            
        Returns:
            Check result with any issues found
        """
        issues = []
        
        # Skip check if configured to do so
        if self.parameters["skip_historical_check"]:
            return {"passed": True, "issues": []}
        
        # Get author address
        author = proposal_data.get("author")
        if not author:
            return {"passed": True, "issues": []}
        
        # Get author history
        account_history = context.get("account_history", {}).get(author, {})
        
        # Check account age
        account_age_blocks = account_history.get("age_in_blocks", 0)
        if account_age_blocks < 1000:  # Arbitrary threshold for new accounts
            issues.append({
                "type": "new_account",
                "severity": "low",
                "description": f"Proposal author account is relatively new ({account_age_blocks} blocks old)",
                "recommendation": "Verify author's reputation in the community"
            })
        
        # Check previous proposals
        previous_proposals = account_history.get("proposals", [])
        rejected_count = sum(1 for p in previous_proposals if p.get("status") == "rejected")
        total_count = len(previous_proposals)
        
        if total_count > 0 and rejected_count / total_count > 0.7:
            issues.append({
                "type": "high_rejection_rate",
                "severity": "medium",
                "description": f"Author has high proposal rejection rate ({rejected_count}/{total_count})",
                "recommendation": "Review author's previous proposals to understand rejection patterns"
            })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def _check_bytecode_similarity(self, proposal_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for bytecode similarity with known contracts.
        
        Args:
            proposal_data: Proposal data to check
            context: Execution context
            
        Returns:
            Check result with any issues found
        """
        issues = []
        
        # Get new contract bytecode
        new_bytecode = proposal_data.get("bytecode")
        if not new_bytecode:
            return {"passed": True, "issues": []}
        
        # Get existing contracts bytecode
        existing_bytecode = context.get("contract_bytecode", {})
        
        # Perform simple similarity check
        # In a real implementation, this would use more sophisticated bytecode analysis
        for contract_name, bytecode in existing_bytecode.items():
            similarity = self._calculate_bytecode_similarity(new_bytecode, bytecode)
            if similarity > 0.9:  # 90% similarity
                issues.append({
                    "type": "high_bytecode_similarity",
                    "severity": "medium",
                    "description": f"New contract is very similar to existing contract '{contract_name}' ({similarity*100:.1f}% match)",
                    "recommendation": "Verify that this is not a duplicate or malicious variation of an existing contract"
                })
            elif similarity > 0.7:  # 70% similarity
                issues.append({
                    "type": "moderate_bytecode_similarity",
                    "severity": "low",
                    "description": f"New contract has similarities with existing contract '{contract_name}' ({similarity*100:.1f}% match)",
                    "recommendation": "Review the contract code to understand the similarities"
                })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def _calculate_bytecode_similarity(self, bytecode1: str, bytecode2: str) -> float:
        """
        Calculate similarity between two bytecode strings.
        
        Args:
            bytecode1: First bytecode string
            bytecode2: Second bytecode string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Simple Jaccard similarity for demonstration
        # In practice, a more sophisticated algorithm would be used
        if not bytecode1 or not bytecode2:
            return 0.0
            
        # Convert to bytes if not already
        if isinstance(bytecode1, str):
            bytecode1 = bytecode1.encode()
        if isinstance(bytecode2, str):
            bytecode2 = bytecode2.encode()
            
        # Break into chunks for comparison
        chunk_size = 16
        set1 = set(bytecode1[i:i+chunk_size] for i in range(0, len(bytecode1) - chunk_size + 1, 4))
        set2 = set(bytecode2[i:i+chunk_size] for i in range(0, len(bytecode2) - chunk_size + 1, 4))
        
        # Jaccard similarity: intersection over union
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_risk_score(self, checks: List[Dict[str, Any]]) -> float:
        """
        Calculate an overall risk score from all checks.
        
        Args:
            checks: List of check results
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        if not checks:
            return 0.0
        
        # Extract all issues
        all_issues = []
        for check in checks:
            all_issues.extend(check.get("issues", []))
        
        # Count issues by severity
        high_count = sum(1 for issue in all_issues if issue.get("severity") == "high")
        medium_count = sum(1 for issue in all_issues if issue.get("severity") == "medium")
        low_count = sum(1 for issue in all_issues if issue.get("severity") == "low")
        
        # Calculate weighted score
        # High: 1.0, Medium: 0.5, Low: 0.2
        weighted_sum = high_count * 1.0 + medium_count * 0.5 + low_count * 0.2
        
        # Scale factor to limit maximum score to 1.0
        scale_factor = 10
        
        # Final score (capped at 1.0)
        return min(weighted_sum / scale_factor, 1.0)
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]], risk_level: str) -> List[str]:
        """
        Generate recommendations based on issues found.
        
        Args:
            issues: List of issues found
            risk_level: Overall risk level
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Add specific recommendations from issues
        for issue in issues:
            if "recommendation" in issue:
                recommendations.append(issue["recommendation"])
        
        # Add general recommendations based on risk level
        if risk_level == "high":
            recommendations.append("Consider rejecting this proposal until security issues are addressed")
            recommendations.append("Request a formal security audit for this proposal")
        elif risk_level == "medium":
            recommendations.append("Request more documentation and justification for the proposed changes")
            recommendations.append("Consider a peer review by at least two community members")
        elif len(recommendations) == 0:
            recommendations.append("No significant issues found. Standard review procedures recommended.")
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        for rec in recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)
        
        return unique_recommendations 