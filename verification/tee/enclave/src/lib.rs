/**
 * ChaosChain SGX Enclave
 * 
 * Minimal enclave implementation for Intel SGX integration.
 * This is a placeholder for Sprint-0 and will be expanded in Sprint-1.
 */

// Conditional compilation for SGX environment
#![cfg_attr(feature = "sgx", no_std)]

#[cfg(feature = "sgx")]
extern crate sgx_tstd as std;

use serde::{Deserialize, Serialize};

/// Input for an enclave operation
#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct EnclaveInput {
    pub operation: String,
    pub parameters: Vec<i32>,
}

/// Result of an enclave operation
#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct EnclaveOutput {
    pub result: i32,
    pub status: String,
}

/// Add two numbers within the enclave
/// 
/// This is a minimal demonstration function for Sprint-0.
/// In Sprint-1, this will be replaced with actual verification logic.
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Process an operation in the enclave
pub fn process_operation(input: EnclaveInput) -> EnclaveOutput {
    match input.operation.as_str() {
        "add" => {
            if input.parameters.len() != 2 {
                return EnclaveOutput {
                    result: 0,
                    status: "ERROR: add operation requires exactly 2 parameters".to_string(),
                };
            }
            
            let result = add(input.parameters[0], input.parameters[1]);
            
            EnclaveOutput {
                result,
                status: "SUCCESS".to_string(),
            }
        },
        _ => EnclaveOutput {
            result: 0,
            status: format!("ERROR: Unsupported operation '{}'", input.operation),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
        assert_eq!(add(-1, 1), 0);
        assert_eq!(add(100, 200), 300);
    }

    #[test]
    fn test_process_operation_add() {
        let input = EnclaveInput {
            operation: "add".to_string(),
            parameters: vec![10, 20],
        };
        
        let expected_output = EnclaveOutput {
            result: 30,
            status: "SUCCESS".to_string(),
        };
        
        assert_eq!(process_operation(input), expected_output);
    }

    #[test]
    fn test_process_operation_invalid() {
        let input = EnclaveInput {
            operation: "multiply".to_string(),
            parameters: vec![10, 20],
        };
        
        let output = process_operation(input);
        assert_eq!(output.result, 0);
        assert!(output.status.starts_with("ERROR"));
    }
} 