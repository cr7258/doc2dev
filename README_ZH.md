<p>
   <a href="README.md"> English <a/>| 中文
</p>

# Doc2Dev

Doc2Dev 可以为 LLM 和 AI 编程助手提供实时的文档查询。Doc2Dev 可对任意 GitHub/GitLab 仓库进行文档索引与查询，并通过 MCP 轻松集成至 Cursor、Windsurf 等 AI 编程工具。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202508072302799.png)

## 核心优势

- **最新、最准确的代码**：获取反映最新库版本和最佳实践的建议。
- **减少调试时间**：减少因过时的 AI 知识导致的错误修复时间。
- **拒绝代码幻觉**：依赖于已记录的、存在的函数和 API。
- **精准版本**：能根据特定库版本给出准确答案。
- **无缝工作流程**：直接集成到现有的 AI 编程助手中，无需频繁切换到文档网站。
- **语义理解**：基于向量嵌入的搜索超越了传统的关键词匹配，能够理解查询的语义内容。

## 设置环境变量

请根据 `.env.example` 文件的说明，创建 [.env](https://github.com/cr7258/doc2dev/blob/main/backend/.env.example) 文件并配置相应的环境变量。

## 启动服务

1. 启动后端服务：

```bash
cd backend
uv run main.py
```

2. 启动前端服务：
   
```bash
cd frontend
npm run dev
```
