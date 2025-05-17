# ChaosCore Makefile

.PHONY: help boot-staging deploy-goerli clean

help:
	@echo "ChaosCore Governance OS Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  help                 Show this help message"
	@echo "  boot-staging         Deploy to Goerli testnet, spin up stack, and run demo"
	@echo "  deploy-goerli        Deploy contracts to Goerli testnet"
	@echo "  clean                Clean up deployment artifacts"

# Deploy to Goerli testnet
deploy-goerli:
	@echo "Deploying contracts to Goerli testnet..."
	npx hardhat run --network goerli deployments/hardhat/deploy_endpoint.js
	@echo "Deployment completed"

# Prepare staging environment
prepare-staging:
	@echo "Preparing staging environment..."
	cp deployments/.env.staging.example deployments/.env.staging
	@if [ -f deployments/goerli/ChaosEndpoint.json ]; then \
		echo "Updating contract address in .env.staging..."; \
		CONTRACT_ADDRESS=$$(cat deployments/goerli/ChaosEndpoint.json | grep -o '"address": "[^"]*' | cut -d'"' -f4); \
		sed -i.bak "s|ETHEREUM_CONTRACT_ADDRESS=.*|ETHEREUM_CONTRACT_ADDRESS=$$CONTRACT_ADDRESS|g" deployments/.env.staging; \
		rm -f deployments/.env.staging.bak; \
	else \
		echo "Warning: No contract deployment found. Run 'make deploy-goerli' first."; \
	fi

# Boot staging environment
boot-staging: prepare-staging
	@echo "Booting staging environment..."
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

# Clean up resources
clean:
	@echo "Cleaning up..."
	docker-compose -f docker-compose.staging.yml down
	rm -f tx_hash.txt
	@echo "Cleanup completed" 