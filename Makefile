# ChaosCore Makefile

.PHONY: help boot-staging deploy-goerli deploy-sepolia boot-sepolia clean

help:
	@echo "ChaosCore Governance OS Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  help                 Show this help message"
	@echo "  boot-staging         Deploy to Goerli testnet, spin up stack, and run demo"
	@echo "  deploy-goerli        Deploy contracts to Goerli testnet"
	@echo "  deploy-sepolia       Deploy contracts to Sepolia testnet"
	@echo "  boot-sepolia         Deploy to Sepolia testnet, spin up stack, and run demo"
	@echo "  clean                Clean up deployment artifacts"

# Deploy to Goerli testnet (deprecated but maintained for backward compatibility)
deploy-goerli:
	@echo "Deploying contracts to Goerli testnet..."
	@echo "Warning: Goerli network is deprecated, consider using Sepolia instead."
	npx hardhat run --network goerli deployments/hardhat/deploy_endpoint.js
	@echo "Deployment completed"

# Deploy to Sepolia testnet
deploy-sepolia:
	@echo "Deploying contracts to Sepolia testnet..."
	npx hardhat run --network sepolia deployments/hardhat/deploy_endpoint.js
	@echo "Deployment completed"

# Prepare staging environment (Goerli - deprecated)
prepare-staging:
	@echo "Preparing staging environment (Goerli)..."
	@echo "Warning: Goerli network is deprecated, consider using Sepolia instead."
	cp deployments/.env.staging.example deployments/.env.staging
	@if [ -f deployments/goerli/ChaosEndpoint.json ]; then \
		echo "Updating contract address in .env.staging..."; \
		CONTRACT_ADDRESS=$$(cat deployments/goerli/ChaosEndpoint.json | grep -o '"address": "[^"]*' | cut -d'"' -f4); \
		sed -i.bak "s|ETHEREUM_CONTRACT_ADDRESS=.*|ETHEREUM_CONTRACT_ADDRESS=$$CONTRACT_ADDRESS|g" deployments/.env.staging; \
		rm -f deployments/.env.staging.bak; \
	else \
		echo "Warning: No contract deployment found. Run 'make deploy-goerli' first."; \
	fi

# Prepare Sepolia environment
prepare-sepolia:
	@echo "Preparing Sepolia environment..."
	cp deployments/.env.staging.example deployments/.env.sepolia
	@if [ -f deployments/sepolia/ChaosEndpoint.json ]; then \
		echo "Updating contract address in .env.sepolia..."; \
		CONTRACT_ADDRESS=$$(cat deployments/sepolia/ChaosEndpoint.json | grep -o '"address": "[^"]*' | cut -d'"' -f4); \
		sed -i.bak "s|ETHEREUM_CONTRACT_ADDRESS=.*|ETHEREUM_CONTRACT_ADDRESS=$$CONTRACT_ADDRESS|g" deployments/.env.sepolia; \
		sed -i.bak "s|ETHEREUM_PROVIDER_URL=.*|ETHEREUM_PROVIDER_URL=https://sepolia.infura.io/v3/\$${INFURA_API_KEY}|g" deployments/.env.sepolia; \
		rm -f deployments/.env.sepolia.bak; \
	else \
		echo "Warning: No contract deployment found. Run 'make deploy-sepolia' first."; \
	fi

# Boot staging environment (Goerli - deprecated)
boot-staging: prepare-staging
	@echo "Booting staging environment on Goerli..."
	@echo "Warning: Goerli network is deprecated, consider using Sepolia instead."
	docker-compose -f docker-compose.staging.yml up -d
	@echo "Waiting for API to be healthy..."
	@timeout=60; \
	while [ $$timeout -gt 0 ]; do \
		if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
			echo "API is healthy!"; \
			break; \
		fi; \
		echo "Waiting for API to be healthy ($$timeout seconds left)..."; \
		sleep 5; \
		timeout=$$((timeout - 5)); \
	done
	@if [ $$timeout -le 0 ]; then \
		echo "Error: API failed to become healthy within timeout"; \
		exit 1; \
	fi
	@echo "Running governance demo..."
	python examples/sdk_gateway_demo_http.py --stage --anchor-eth
	@echo "Demo completed"
	@if [ -f tx_hash.txt ]; then \
		echo "Transaction hash: $$(cat tx_hash.txt)"; \
		echo "Etherscan URL: https://goerli.etherscan.io/tx/$$(cat tx_hash.txt)"; \
		open "https://goerli.etherscan.io/tx/$$(cat tx_hash.txt)" || echo "Open URL manually: https://goerli.etherscan.io/tx/$$(cat tx_hash.txt)"; \
	fi

# Boot Sepolia environment
boot-sepolia: prepare-sepolia
	@echo "Booting environment on Sepolia..."
	docker-compose -f docker-compose.sepolia.yml up -d
	@echo "Waiting for API to be healthy..."
	@timeout=60; \
	while [ $$timeout -gt 0 ]; do \
		if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
			echo "API is healthy!"; \
			break; \
		fi; \
		echo "Waiting for API to be healthy ($$timeout seconds left)..."; \
		sleep 5; \
		timeout=$$((timeout - 5)); \
	done
	@if [ $$timeout -le 0 ]; then \
		echo "Error: API failed to become healthy within timeout"; \
		exit 1; \
	fi
	@echo "Running governance demo..."
	python examples/sdk_gateway_demo_http.py --stage --anchor-eth --network sepolia
	@echo "Demo completed"
	@if [ -f tx_hash.txt ]; then \
		echo "Transaction hash: $$(cat tx_hash.txt)"; \
		echo "Etherscan URL: https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)"; \
		open "https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)" || echo "Open URL manually: https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)"; \
	fi

# Clean up resources
clean:
	@echo "Cleaning up..."
	docker-compose -f docker-compose.staging.yml down
	docker-compose -f docker-compose.sepolia.yml down
	rm -f tx_hash.txt
	@echo "Cleanup completed" 