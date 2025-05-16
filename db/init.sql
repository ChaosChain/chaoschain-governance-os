-- Initialize ChaosCore database schema

-- Agent Registry tables
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_metadata (
    agent_id VARCHAR(255) REFERENCES agents(id),
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (agent_id, key)
);

-- Proof of Agency tables
CREATE TABLE IF NOT EXISTS actions (
    id VARCHAR(255) PRIMARY KEY,
    agent_id VARCHAR(255) REFERENCES agents(id),
    action_type VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    anchored BOOLEAN NOT NULL DEFAULT FALSE,
    tx_hash VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS action_data (
    action_id VARCHAR(255) REFERENCES actions(id),
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (action_id, key)
);

CREATE TABLE IF NOT EXISTS outcomes (
    action_id VARCHAR(255) PRIMARY KEY REFERENCES actions(id),
    success BOOLEAN NOT NULL,
    impact_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    anchored BOOLEAN NOT NULL DEFAULT FALSE,
    tx_hash VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS outcome_results (
    action_id VARCHAR(255) REFERENCES outcomes(action_id),
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (action_id, key)
);

-- Secure Execution tables
CREATE TABLE IF NOT EXISTS attestations (
    id VARCHAR(255) PRIMARY KEY,
    enclave_hash VARCHAR(255) NOT NULL,
    data TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Reputation System tables
CREATE TABLE IF NOT EXISTS reputation_scores (
    agent_id VARCHAR(255) REFERENCES agents(id),
    context VARCHAR(255) NOT NULL DEFAULT 'global',
    score DECIMAL(5,2) NOT NULL DEFAULT 0,
    last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (agent_id, context)
);

-- Metrics tables
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_actions_agent_id ON actions(agent_id);
CREATE INDEX IF NOT EXISTS idx_reputation_scores_context ON reputation_scores(context);

-- Insert initial metrics
INSERT INTO metrics (name, value) VALUES ('agent_count', 0);
INSERT INTO metrics (name, value) VALUES ('action_count', 0);
INSERT INTO metrics (name, value) VALUES ('simulation_count', 0);
INSERT INTO metrics (name, value) VALUES ('anchoring_count', 0); 