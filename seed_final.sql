-- TrafficGrid Final Seed
CREATE TABLE IF NOT EXISTS proxies (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45),
    port INT,
    protocol VARCHAR(10),
    provider VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    last_rotated_at TIMESTAMP WITH TIME ZONE
);

INSERT INTO proxies (ip_address, port, protocol, provider, is_active) 
VALUES ('192.168.1.100', 8080, 'socks5', 'Digi RO', true),
       ('192.168.1.101', 8080, 'socks5', 'Orange RO', true)
ON CONFLICT DO NOTHING;

INSERT INTO identities (username, platform, status, user_agent, trust_score) 
VALUES ('alex_tiktok_01', 'tiktok', 'active', 'Mozilla/5.0 (Linux; Android 14; SM-S928B)', 85),
       ('alex_yt_01', 'youtube', 'active', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 90)
ON CONFLICT (username) DO NOTHING;
