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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Migration script for existing data
-- Add source column to existing repositories table (if it doesn't exist)
-- ALTER TABLE repositories ADD COLUMN source ENUM('github', 'gitlab') NOT NULL DEFAULT 'github';

-- Update existing data to set source as 'github' (for backward compatibility)
-- UPDATE repositories SET source = 'github' WHERE source IS NULL;
