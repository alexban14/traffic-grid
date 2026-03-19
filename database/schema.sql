-- TrafficGrid Core Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE identities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255),
    platform VARCHAR(50),
    cookies JSONB,
    behavioral_dna vector(1536), -- For mimicking human interaction paths
    trust_score INT DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50),
    target_url TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE proxy_logs (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45),
    latency_ms INT,
    provider VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);