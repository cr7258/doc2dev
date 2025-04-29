CREATE TABLE repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(500),
    repo VARCHAR(255) NOT NULL,
    repo_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


INSERT INTO repositories (name, description, repo, repo_url) VALUES
('Next.js', 'React 框架，用于构建全栈 Web 应用', '/vercel/next.js', 'https://github.com/vercel/next.js'),
('Elasticsearch', '分布式搜索和分析引擎', '/elastic/elasticsearch', 'https://github.com/elastic/elasticsearch'),
('Laravel', 'PHP Web 应用框架', '/laravel/docs', 'https://github.com/laravel/docs'),
('Clerk', '完整的用户管理和认证解决方案', '/clerk/clerk-docs', 'https://github.com/clerk/clerk-docs'),
('MongoDB', '文档数据库解决方案', '/mongodb/docs', 'https://github.com/mongodb/docs'),
('Upstash Redis', '无服务器 Redis 数据库', '/upstash/docs', 'https://github.com/upstash/docs'),
('FastAPI', '现代、快速的 Python Web 框架', '/tiangolo/fastapi', 'https://github.com/tiangolo/fastapi'),
('PyTorch', '开源机器学习框架', '/pytorch/tutorials', 'https://github.com/pytorch/tutorials'),
('Vue.js', '渐进式 JavaScript 框架', '/vuejs/docs', 'https://github.com/vuejs/docs'),
('Elasticsearch MCP Server', 'Elasticsearch MCP 服务器', '/cr7258/elasticsearch-mcp-server', 'https://github.com/cr7258/elasticsearch-mcp-server');