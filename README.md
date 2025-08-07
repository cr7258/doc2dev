<p>
   English | <a href="README_ZH.md">中文</a>
</p>

# Doc2Dev

Doc2Dev provides real-time documentation querying for LLMs and AI programming assistants. Doc2Dev can index and query documentation from any GitHub/Gitlab repository and easily integrate with AI programming tools like Cursor and Windsurf through MCP.

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202508072302799.png)

## Core Advantages

- **Latest, Most Accurate Code**: Get recommendations that reflect the latest library versions and best practices.
- **Reduced Debugging Time**: Minimize time spent fixing errors caused by outdated AI knowledge.
- **No Code Hallucinations**: Rely on documented, existing functions and APIs.
- **Version Precision**: Provide accurate answers based on specific library versions.
- **Seamless Workflow**: Direct integration into existing AI programming assistants without frequent switching to documentation websites.
- **Semantic Understanding**: Vector embedding-based search goes beyond traditional keyword matching to understand the semantic content of queries.

## Environment Variables Setup

Please create a `.env` file based on the `.env.example` file instructions and configure the corresponding environment variables.

## Starting Services

1. Start the backend service:

```bash
cd backend
uv run main.py
```

2. Start the frontend service:

```bash
cd frontend
npm run dev
```