CREATE TABLE repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(500),
    repo VARCHAR(255) NOT NULL,
    repo_url VARCHAR(255) NOT NULL,
    tokens INT NOT NULL,
    snippets INT NOT NULL,
    repo_status ENUM('in_progress', 'completed', 'failed', 'pending') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
