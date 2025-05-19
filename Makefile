# ChaosCore Makefile

.PHONY: help boot-staging boot-sepolia deploy-sepolia clean wait-api prepare-staging prepare-sepolia

help:
	@echo "ChaosCore Governance OS Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  help                 Show this help message"
	@echo "  deploy-sepolia       Deploy contracts to Sepolia testnet"
	@echo "  boot-sepolia         Deploy to Sepolia testnet, spin up stack, and run demo"
	@echo "  boot-staging         (DEPRECATED) Use boot-sepolia instead"
	@echo "  clean                Clean up deployment artifacts"

# Deploy to Sepolia testnet
deploy-sepolia:
	@echo "Deploying contracts to Sepolia testnet..."
	@set -a ; source deployments/.env.sepolia ; set +a
	@if [ -z "$${RPC_URL}" ]; then echo "ERROR: RPC_URL is empty in .env.sepolia"; exit 1; fi
	@if [ -z "$${PRIVATE_KEY}" ]; then echo "ERROR: PRIVATE_KEY is empty in .env.sepolia"; exit 1; fi
	npx hardhat run --network sepolia deployments/hardhat/deploy_endpoint.js
	@echo "Deployment completed"

# Helper target to wait for API health
wait-api:
	@echo "Waiting for API to be healthy..."
	@timeout=60; \
	while [ $${timeout} -gt 0 ]; do \
		if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
			echo "API is healthy!"; \
			break; \
		fi; \
		echo "Waiting for API to be healthy ($${timeout} seconds left)..."; \
		sleep 5; \
		timeout=$$((timeout - 5)); \
	done; \
	if [ $${timeout} -le 0 ]; then \
		echo "Error: API failed to become healthy within timeout"; \
		exit 1; \
	fi

# Prepare Sepolia environment
prepare-sepolia:
	@echo "Preparing Sepolia environment..."
	cp deployments/.env.sepolia.example deployments/.env.sepolia
	@if [ -f deployments/sepolia/ChaosEndpoint.json ]; then \
		echo "Updating contract address in .env.sepolia..."; \
		CONTRACT_ADDRESS=$$(cat deployments/sepolia/ChaosEndpoint.json | grep -o '"address": "[^"]*' | cut -d'"' -f4); \
		sed -i.bak "s|ETHEREUM_CONTRACT_ADDRESS=.*|ETHEREUM_CONTRACT_ADDRESS=$$CONTRACT_ADDRESS|g" deployments/.env.sepolia; \
		rm -f deployments/.env.sepolia.bak; \
	else \
		echo "Warning: No contract deployment found. Run 'make deploy-sepolia' first."; \
	fi

# Prepare Staging environment (DEPRECATED)
prepare-staging:
	@echo "DEPRECATED: Please use prepare-sepolia instead"
	@echo "Preparing Sepolia environment..."
	cp deployments/.env.staging.example deployments/.env.staging
	@if [ -f deployments/sepolia/ChaosEndpoint.json ]; then \
		echo "Updating contract address in .env.staging..."; \
		CONTRACT_ADDRESS=$$(cat deployments/sepolia/ChaosEndpoint.json | grep -o '"address": "[^"]*' | cut -d'"' -f4); \
		sed -i.bak "s|ETHEREUM_CONTRACT_ADDRESS=.*|ETHEREUM_CONTRACT_ADDRESS=$$CONTRACT_ADDRESS|g" deployments/.env.staging; \
		sed -i.bak "s|ETHEREUM_PROVIDER_URL=.*|ETHEREUM_PROVIDER_URL=https://sepolia.infura.io/v3/\$${INFURA_API_KEY}|g" deployments/.env.staging; \
		rm -f deployments/.env.staging.bak; \
	else \
		echo "Warning: No contract deployment found. Run 'make deploy-sepolia' first."; \
	fi

# Boot Sepolia environment
boot-sepolia: prepare-sepolia
	@echo "Booting environment on Sepolia..."
	docker-compose -f docker-compose.sepolia.yml build api
	docker-compose -f docker-compose.sepolia.yml up -d
	$(MAKE) wait-api
	@echo "Running governance demo..."
	python examples/sdk_gateway_demo_http.py --stage --anchor-eth --network sepolia
	@echo "Demo completed"
	@if [ -f tx_hash.txt ] && [ -s tx_hash.txt ]; then \
		ANCHOR_STATUS=$$(curl -s -o /dev/null -w "%{http_code}" https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)); \
		if [ "$$ANCHOR_STATUS" = "200" ] || [ "$$ANCHOR_STATUS" = "201" ]; then \
			echo "🟢 Sepolia anchor OK – tx: $$(cat tx_hash.txt)"; \
			echo "Etherscan URL: https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)"; \
			open "https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)" || echo "Open URL manually: https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)"; \
		else \
			echo "⚠️ Anchoring transaction exists but status check failed ($$ANCHOR_STATUS)"; \
			echo "Etherscan URL: https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)"; \
		fi; \
	else \
		echo "⛔ No transaction hash found - anchoring may have failed"; \
	fi

# Boot staging environment (DEPRECATED)
boot-staging: prepare-staging
	@echo "DEPRECATED: Please use boot-sepolia instead"
	@echo "Booting environment on Sepolia..."
	docker-compose -f docker-compose.sepolia.yml up -d
	@echo "Waiting for API to be healthy..."
	@timeout=60; \
	while [ $${timeout} -gt 0 ]; do \
		if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
			echo "API is healthy!"; \
			break; \
		fi; \
		echo "Waiting for API to be healthy ($${timeout} seconds left)..."; \
		sleep 5; \
		timeout=$$((timeout - 5)); \
	done; \
	if [ $${timeout} -le 0 ]; then \
		echo "Error: API failed to become healthy within timeout"; \
		exit 1; \
	fi
	@echo "Running governance demo..."
	python examples/sdk_gateway_demo_http.py --stage --anchor-eth --network sepolia
	@echo "Demo completed"
	@if [ -f tx_hash.txt ]; then \
		echo "🟢 Sepolia anchor OK – tx: $$(cat tx_hash.txt)"; \
		echo "Etherscan URL: https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)"; \
		open "https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)" || echo "Open URL manually: https://sepolia.etherscan.io/tx/$$(cat tx_hash.txt)"; \
	fi

# Clean up resources
clean:
	@echo "Cleaning up..."
	docker-compose -f docker-compose.sepolia.yml down
	rm -f tx_hash.txt
	@echo "Cleanup completed" 