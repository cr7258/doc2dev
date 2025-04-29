CREATE TABLE repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    repo VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


INSERT INTO repositories (name, repo) 
VALUES ('cr7258_elasticsearch_mcp_server', 'cr7258/elasticsearch-mcp-server');