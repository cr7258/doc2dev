# MCP Streamable HTTP 集成指南

Doc2Dev 现在支持 MCP (Model Context Protocol) Streamable HTTP，为每个用户提供独立的 URL，可以轻松与支持 MCP 的 AI 工具集成。

## 🎯 功能特点

- **用户隔离**：每个用户拥有独立的 MCP 服务器 URL
- **标准协议**：完全符合 MCP Streamable HTTP 标准
- **简单配置**：只需一个 URL 即可集成到 AI 工具中
- **实时文档**：访问用户已索引的最新仓库文档

## 🔗 获取您的 MCP URL

1. 登录 Doc2Dev 应用
2. 访问 **设置 > MCP** 页面
3. 复制您的专属 MCP URL：`https://doc2dev.com/mcp/{your-user-id}`

## 🛠️ 支持的 AI 工具

### Claude Desktop

在 Claude Desktop 配置文件中添加：

```json
{
  "mcpServers": {
    "doc2dev": {
      "url": "https://doc2dev.com/mcp/{your-user-id}"
    }
  }
}
```

### VS Code Copilot

通过 MCP 扩展配置：

```json
{
  "mcp.servers": {
    "doc2dev": {
      "url": "https://doc2dev.com/mcp/{your-user-id}"
    }
  }
}
```

## 🔧 支持的 MCP 方法

### 标准 MCP 方法

- **initialize**: 初始化 MCP 连接
- **notifications/initialized**: 客户端初始化完成通知
- **tools/list**: 获取可用工具列表
- **tools/call**: 调用特定工具

### 可用工具

#### 1. search-library-id

搜索库 ID，用于查找您已索引的仓库。

**参数：**
- `libraryName` (string): 要搜索的库名称

**示例：**
```json
{
  "method": "tools/call",
  "params": {
    "name": "search-library-id",
    "arguments": {
      "libraryName": "kubernetes"
    }
  }
}
```

#### 2. get-library-docs

获取特定库的文档内容。

**参数：**
- `libraryID` (string): 库的 ID（从 search-library-id 获取）
- `question` (string): 关于库的问题

**示例：**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get-library-docs",
    "arguments": {
      "libraryID": "kubernetes_sigs_kubebuilder",
      "question": "How to create a new controller?"
    }
  }
}
```

## 📋 快速开始

### 1. 在 AI 工具中配置

将您的 MCP URL 添加到 AI 工具的配置文件中。

### 2. 开始对话

在 AI 工具中，您可以直接询问关于已索引仓库的问题：

```
"How do I use kubebuilder to create a Kubernetes operator?"
```

AI 工具会自动调用 Doc2Dev 的 MCP 服务来获取最新的文档信息。

### 3. 搜索和查询

AI 工具会：
1. 使用 `search-library-id` 找到相关的库
2. 使用 `get-library-docs` 获取具体的文档内容
3. 基于最新文档提供准确的回答

## 🔍 测试您的集成

您可以使用 curl 命令测试 MCP 端点：

```bash
# 获取服务器信息
curl -X GET "https://doc2dev.com/mcp/{your-user-id}"

# 列出可用工具
curl -X POST "https://doc2dev.com/mcp/{your-user-id}" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "id": 1}'

# 搜索库
curl -X POST "https://doc2dev.com/mcp/{your-user-id}" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "id": 1,
    "params": {
      "name": "search-library-id",
      "arguments": {
        "libraryName": "react"
      }
    }
  }'
```

## 🚀 高级用法

### 批量查询

您可以在一次对话中询问多个仓库的信息：

```
"Compare the authentication methods in Next.js and React Router"
```

### 特定版本

如果您索引了特定版本的文档，可以询问版本相关的问题：

```
"What's new in Kubernetes 1.28 compared to 1.27?"
```

### 代码示例

请求具体的代码示例：

```
"Show me a complete example of creating a custom Kubernetes controller with kubebuilder"
```

## 🔒 安全性

- 每个用户只能访问自己的仓库
- 所有请求都通过 HTTPS 加密
- 用户身份验证通过 URL 中的用户 ID 进行

## 📞 支持

如果您在使用 MCP 集成时遇到问题：

1. 检查您的 MCP URL 是否正确
2. 确认您已登录 Doc2Dev
3. 验证您要查询的仓库已经被索引
4. 查看 AI 工具的 MCP 配置文档

## 🔄 更新

Doc2Dev 的 MCP 服务会自动反映您仓库的最新状态。当您添加新仓库或更新现有仓库时，MCP 工具会立即可用。
