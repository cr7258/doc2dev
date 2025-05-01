CREATE TABLE repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(500),
    repo VARCHAR(255) NOT NULL,
    repo_url VARCHAR(255) NOT NULL,
    tokens INT NOT NULL,
    snippets INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


INSERT INTO repositories (name, description, repo, repo_url, tokens, snippets) VALUES
('Next.js', 'React framework for building full-stack web applications', '/vercel/next.js', 'https://github.com/vercel/next.js', 30000, 40),
('Elasticsearch', 'Distributed search and analytics engine', '/elastic/elasticsearch', 'https://github.com/elastic/elasticsearch', 45000, 65),
('Laravel', 'PHP web application framework', '/laravel/docs', 'https://github.com/laravel/docs', 28000, 35),
('Clerk', 'Complete user management and authentication solution', '/clerk/clerk-docs', 'https://github.com/clerk/clerk-docs', 15000, 25),
('FastAPI', 'Modern, fast Python web framework', '/tiangolo/fastapi', 'https://github.com/tiangolo/fastapi', 32000, 48),
('PyTorch', 'Open source machine learning framework', '/pytorch/tutorials', 'https://github.com/pytorch/tutorials', 50000, 70),
('Vue.js', 'Progressive JavaScript framework', '/vuejs/docs', 'https://github.com/vuejs/docs', 25000, 38),
('Elasticsearch MCP Server', 'Elasticsearch Model Context Protocol server', '/cr7258/elasticsearch-mcp-server', 'https://github.com/cr7258/elasticsearch-mcp-server', 12000, 20);