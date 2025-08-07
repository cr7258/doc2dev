CREATE DATABASE IF NOT EXISTS doc2dev;

USE doc2dev;

CREATE TABLE repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(500),
    repo VARCHAR(255) NOT NULL,
    repo_url VARCHAR(255) NOT NULL,
    tokens INT NOT NULL,
    snippets INT NOT NULL,
    repo_status ENUM('in_progress', 'completed', 'failed', 'pending') NOT NULL,
    source ENUM('github', 'gitlab') NOT NULL DEFAULT 'github',
    created_at TIMESTAMP DEFAULT UTC_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT UTC_TIMESTAMP() ON UPDATE UTC_TIMESTAMP()
);


CREATE DATABASE IF NOT EXISTS doc2dev_users;

USE doc2dev_users;

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    github_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    avatar_url VARCHAR(500),
    access_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT UTC_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT UTC_TIMESTAMP() ON UPDATE UTC_TIMESTAMP()
);

CREATE INDEX idx_github_id ON users(github_id);
CREATE INDEX idx_username ON users(username);
