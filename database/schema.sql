-- TrafficGrid Core Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE IF NOT EXISTS identities (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    platform VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    user_agent TEXT,
    screen_resolution VARCHAR(20),
    behavioral_dna vector(1536),
    trust_score INT DEFAULT 50,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'IDLE',
    ip_address VARCHAR(45),
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proxies (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45),
    port INT,
    protocol VARCHAR(10) DEFAULT 'socks5',
    provider VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    last_rotated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50),
    target_url TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    config JSONB,
    celery_task_id VARCHAR(255),
    worker_id INT REFERENCES workers(id),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
