-- Migration: Create user_platform_configs table
-- Description: Add table for storing user-specific Git platform configurations
-- Date: 2025-01-04

CREATE TABLE IF NOT EXISTS user_platform_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL COMMENT 'GitHub user ID or UUID',
    name VARCHAR(255) NOT NULL COMMENT 'User-friendly name for the configuration',
    platform VARCHAR(50) NOT NULL COMMENT 'Platform type: github or gitlab',
    base_url VARCHAR(500) NOT NULL COMMENT 'Base URL of the platform instance',
    token TEXT NOT NULL COMMENT 'Access token for the platform',
    enabled BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Whether this configuration is enabled',
    is_default BOOLEAN DEFAULT FALSE NOT NULL COMMENT 'Whether this is the default configuration for the platform',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_platform (platform),
    INDEX idx_enabled (enabled),
    INDEX idx_user_platform (user_id, platform),
    
    -- Constraints
    CONSTRAINT chk_platform CHECK (platform IN ('github', 'gitlab')),
    CONSTRAINT chk_base_url CHECK (base_url LIKE 'http%')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User-specific Git platform configurations';

-- Note: We don't enforce unique constraint on (user_id, platform, is_default) 
-- because it would prevent having multiple defaults temporarily during updates.
-- The application logic ensures only one default per platform per user.
