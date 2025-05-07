# Intel SGX Integration for ChaosChain

This directory contains the Trusted Execution Environment (TEE) components of ChaosChain Governance OS, implemented using Intel SGX.

## Development Environment Setup

### Prerequisites

1. **Hardware Requirements**
   - CPU with Intel SGX support
   - BIOS with SGX enabled (may require configuration)

2. **Software Requirements**
   - [Intel SGX SDK](https://github.com/intel/linux-sgx) (version 2.17.0 or newer)
   - [Intel SGX Driver](https://github.com/intel/linux-sgx-driver) (for hardware mode)
   - Rust toolchain (stable)
   - [Fortanix EDP](https://edp.fortanix.com/) for Rust SGX development

### Installation Steps

#### 1. Install Intel SGX SDK

**Ubuntu:**
```bash
# Add Intel SGX repository
echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' | sudo tee /etc/apt/sources.list.d/intel-sgx.list
wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo apt-key add -

# Update and install SGX packages
sudo apt update
sudo apt install libsgx-epid libsgx-quote-ex libsgx-dcap-ql libsgx-urts libsgx-enclave-common sgx-aesm-service libsgx-uae-service sgx-aesm-service

# Install SGX SDK
wget https://download.01.org/intel-sgx/sgx-linux/2.17/distro/ubuntu20.04-server/sgx_linux_x64_sdk_2.17.100.3.bin
chmod +x sgx_linux_x64_sdk_2.17.100.3.bin
./sgx_linux_x64_sdk_2.17.100.3.bin
```

**macOS:**
Note: macOS is limited to simulation mode only, as hardware SGX is not available.
```bash
brew install sgx-sdk
```

#### 2. Set up Rust SGX environment

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Fortanix EDP
cargo install fortanix-sgx-tools sgx-detect

# Verify installation
sgx-detect
```

## Development Workflow

### Simulation Mode (No SGX Hardware)

For development without SGX hardware, use the simulation mode:

```bash
# Build without SGX features
cargo build

# Run tests in simulation mode
cargo test
```

### Hardware Mode (SGX-enabled CPU)

When using SGX hardware:

```bash
# Build with SGX features
cargo build --features sgx

# Run with SGX
cargo run --features sgx
```

## Project Structure

- `enclave/` - SGX enclave code (Rust)
- `attestation/` - Remote attestation utilities
- `utils/` - Helper functions for SGX integration

## Testing

```bash
# Run unit tests (simulation mode)
cargo test

# Run SGX-specific tests (requires SGX hardware or simulator)
cargo test --features sgx
```

## Troubleshooting

1. **SGX Not Detected**: Ensure SGX is enabled in BIOS and the SGX driver is installed.
2. **Enclave Signing Issues**: Check that enclave signing key is properly configured.
3. **AE Service Issues**: Ensure the Architectural Enclave service is running: `systemctl status aesmd`.

## Resources

- [Intel SGX Documentation](https://software.intel.com/content/www/us/en/develop/topics/software-guard-extensions.html)
- [Fortanix Rust EDP Guide](https://edp.fortanix.com/docs/)
- [Rust SGX SDK](https://github.com/apache/incubator-teaclave-sgx-sdk) 