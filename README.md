# Doc2Dev: 智能文档检索与查询平台

## 项目概述

Doc2Dev 可以为 LLM 和 AI 编程助手提供实时的文档查询。Doc2Dev 可对任意 GitHub 仓库进行文档索引与查询，并通过 MCP 轻松集成至 Cursor、Windsurf 等 AI 编程工具。

### 开发者面临的痛点

作为开发者，你是否经常遇到这样的困扰？

- AI 编程助手常常编造根本不存在的 API 接口，导致严重的代码幻觉问题。
- 主流大语言模型的训练数据滞后于技术更新，生成的代码常常基于已经废弃的旧版 API。
- 尽管 AI 可以快速生成代码，但调试和排错却耗费了大量时间，反而拖慢了开发进度。

Doc2Dev 的出现正是为了解决这些问题。它利用 OceanBase 向量数据库和大型语言模型(LLM)的强大能力，从官方源头获取最新的、版本特定的文档和相关代码示例，将这些信息注入到 LLM 的上下文中，从而有效提高 LLM 生成代码的质量。

### 核心优势

- **最新、最准确的代码**：获取反映最新库版本和最佳实践的建议。
- **减少调试时间**：减少因过时的 AI 知识导致的错误修复时间。
- **拒绝代码幻觉**：依赖于已记录的、存在的函数和 API。
- **精准版本**：能根据特定库版本给出准确答案。
- **无缝工作流程**：直接集成到现有的 AI 编程助手中，无需频繁切换到文档网站。
- **语义理解**：基于向量嵌入的搜索超越了传统的关键词匹配，能够理解查询的语义内容。

## 技术方案

### 系统架构

Doc2Dev 采用前后端分离的架构设计：

- **前端**：基于 Next.js 构建的现代化 Web 应用，提供仓库管理和文档查询界面。
- **后端**：使用 FastAPI 构建的高性能 API 服务，负责文档下载、处理、索引和查询。
- **数据存储**：使用 OceanBase 存储文档的向量表示和仓库元数据信息。

### 技术栈

- **前端**：Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
- **后端**：Python, FastAPI, WebSockets, AsyncIO
- **AI 模型**：
  - DashScope 嵌入模型：用于生成文档的向量表示
  - OpenAI API (via OpenRouter)：用于生成搜索结果摘要
- **数据库**：使用 OceanBase 处理向量存储、元数据管理和相似度检索
- **MCP** 通过 MCP Server 的方式向 AI 编程助手提供查询文档的接口

### 数据处理流程

1. **文档获取**：通过 GitHub API 下载指定仓库的 Markdown 文件
2. **文档分割**：使用 LangChain 的 MarkdownHeaderTextSplitter 将文档分割成适合嵌入的片段
3. **向量嵌入**：使用 DashScope 嵌入模型将文本片段转换为高维向量
4. **向量存储**：将向量和原始文本存储到 OceanBase 向量数据库中
5. **查询处理**：
   - 将用户查询转换为向量
   - 在 OceanBase 中进行相似度搜索
   - 使用 LLM 生成搜索结果的摘要

## 实施细节

### 系统组件

#### 1. 文档下载与处理模块

```python
# 下载 GitHub 仓库的 Markdown 文件
async def download_md_files_with_progress(repo_url, output_dir, progress_callback=None):
    # 解析 GitHub URL
    org, repo = extract_org_repo(repo_url)
    
    # 使用 GitHub API 下载文件
    # ...
    
    # 返回下载的文件列表
    return md_files
```

#### 2. 文档嵌入与存储模块

```python
# 嵌入并存储文档
def embed_and_store(documents, table_name, drop_old=False):
    # 初始化嵌入模型
    embeddings = DashScopeEmbeddings(model="text-embedding-v2", dashscope_api_key=DASHSCOPE_API)
    
    # 创建或连接到 OceanBase 向量存储
    vector_store = OceanbaseVectorStore.from_documents(
        documents,
        embeddings,
        connection_args=DEFAULT_CONNECTION_ARGS,
        table_name=table_name,
        drop_old=drop_old
    )
    
    return vector_store
```

#### 3. 查询与摘要生成模块

```python
# 查询向量数据库并生成摘要
async def query_and_summarize(table_name, query_text, k=5):
    # 连接到向量存储
    vector_store = connect_to_vector_store(table_name=table_name)
    
    # 执行相似度搜索
    results = vector_store.similarity_search(query_text, k=k)
    
    # 生成搜索结果摘要
    summary = await summarize_search_results(query_text, results)
    
    return results, summary
```

### 数据库设计

#### OceanBase 向量表结构

每个仓库的文档向量存储在独立的表中，表名格式为 `{组织名}_{仓库名}`，表结构如下：

- `id`: 唯一标识符
- `embedding`: 文档片段的向量表示
- `document`: 原始文本内容
- `metadata`: 文档元数据 (JSON格式)

#### 仓库元数据表结构

仓库元数据表存储了关于已索引仓库的信息，包括：

- 仓库名称
- 仓库描述
- GitHub 仓库路径
- GitHub 仓库 URL
- 创建和更新时间戳

### 前端实现

前端采用现代化的组件设计，主要包括：

1. **首页仓库列表**：展示已索引的仓库，支持排序和搜索
2. **仓库添加页面**：提供 GitHub 仓库 URL 输入，支持实时进度显示
3. **文档查询页面**：提供自然语言查询界面，展示搜索结果和智能摘要

## 部署与使用

### 环境要求

- Python 3.9+
- Node.js 18+
- OceanBase 数据库

### 配置说明

项目使用 `.env` 文件管理环境变量：

```bash
GITHUB_TOKEN=xxx
# Embedding
DASHSCOPE_API_KEY=xxx
# AI Summary
OPENAI_API_KEY=xxx
OPENAI_API_BASE=xxx
```

### 准备 Oceanbase 数据库

使用启动 Oceanbase：

```bash
docker run -p 2881:2881 --name obstandalone -e MODE=MINI -e OB_TENANT_PASSWORD=admin -d quay.io/oceanbase/oceanbase-ce
```

创建仓库元数据表：

```sql
CREATE TABLE repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(500),
    repo VARCHAR(255) NOT NULL,
    repo_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 启动服务

1. 启动后端服务：
   ```bash
   uv run src/main.py
   ```

2. 启动前端服务：
   ```bash
   cd frontend/doc2dev
   npm run dev
   ```
