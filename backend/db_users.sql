-- User management database schema for GitHub OAuth authentication
CREATE DATABASE IF NOT EXISTS doc2dev_users;

USE doc2dev_users;

-- Users table for GitHub OAuth authentication
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,  -- UUID primary key
    github_id VARCHAR(50) UNIQUE NOT NULL,  -- GitHub user ID
    username VARCHAR(50) NOT NULL,  -- GitHub username
    email VARCHAR(100),  -- GitHub email (optional)
    avatar_url VARCHAR(500),  -- GitHub avatar URL
    access_token VARCHAR(255),  -- GitHub access token (encrypted storage)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_github_id ON users(github_id);
CREATE INDEX idx_username ON users(username);
