CREATE DATABASE IF NOT EXISTS llm_interaction_system DEFAULT CHARACTER SET utf8mb4;
USE llm_interaction_system;

CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_session (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_code VARCHAR(64) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    title VARCHAR(128) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS chat_message (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_session(id)
);

CREATE TABLE IF NOT EXISTS system_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    level VARCHAR(16) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(64) NOT NULL UNIQUE,
    config_value VARCHAR(255) NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO system_config (config_key, config_value)
VALUES
    ('model_name', 'demo-llm'),
    ('gateway_timeout_ms', '5000'),
    ('history_window', '6')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);
