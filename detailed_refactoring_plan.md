# Doc2Dev 详细重构计划

## 项目目标

将 Doc2Dev 重构为支持多种数据库和服务的可扩展架构：
- **关系型数据库**：MySQL、PostgreSQL、SQLite 等（用于元数据存储）
- **向量数据库**：OceanBase、ChromaDB、PGVector、Qdrant、Weaviate 等
- **嵌入服务**：DashScope、OpenAI、Cohere、HuggingFace 等

## 架构设计原则

1. **分层架构**：清晰的分层结构，便于维护和扩展
2. **接口抽象**：使用抽象接口定义组件行为
3. **工厂模式**：通过工厂类动态创建组件实例
4. **依赖注入**：通过配置文件和依赖注入管理组件
5. **可插拔设计**：新的数据库或服务可以轻松集成

## 目录结构设计

```
/backend/
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # 配置管理（支持多环境）
│   ├── database_configs.py      # 数据库配置模板
│   └── service_configs.py       # 服务配置模板
│
├── core/
│   ├── __init__.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── vector_store.py      # 向量数据库接口
│   │   ├── metadata_db.py       # 元数据数据库接口
│   │   └── embedding.py         # 嵌入服务接口
│   │
│   ├── factories/
│   │   ├── __init__.py
│   │   ├── vector_store.py
│   │   ├── metadata_db.py
│   │   ├── embedding.py
│   │   └── service.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document.py          # 文档处理服务 (DocumentService)
│   │   ├── vector.py            # 向量存储服务 (VectorService)
│   │   ├── metadata.py          # 元数据服务 (MetadataService)
│   │   └── ai.py                # AI 总结服务 (AIService)
│   │
│   └── models/
│       ├── __init__.py
│       ├── repository.py         # 仓库数据模型
│       ├── document.py          # 文档数据模型
│       └── query.py             # 查询数据模型
│
├── adapters/
│   ├── __init__.py
│   │
│   ├── vector_stores/
│   │   ├── __init__.py
│   │   ├── base.py              # 向量数据库基类
│   │   ├── oceanbase.py         # OceanBase 适配器
│   │   ├── chroma.py            # ChromaDB 适配器
│   │   ├── pgvector.py          # PGVector 适配器
│   │   └── weaviate.py          # Weaviate 适配器
│   │
│   ├── metadata_dbs/
│   │   ├── __init__.py
│   │   ├── base.py              # 元数据数据库基类
│   │   ├── mysql.py             # MySQL 适配器
│   │   ├── postgresql.py        # PostgreSQL 适配器
│   │   ├── sqlite.py            # SQLite 适配器
│   │   └── oceanbase.py    # OceanBase 元数据适配器
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── base.py              # 嵌入服务基类
│   │   ├── dashscope.py         # DashScope 适配器
│   │   ├── openai.py            # OpenAI 适配器
│   │   ├── cohere.py            # Cohere 适配器
│   │   └── huggingface.py       # HuggingFace 适配器
│   │
│   └── document_processors/
│       ├── __init__.py
│       ├── base.py              # 文档处理基类
│       ├── markdown.py          # Markdown 处理器
│       ├── pdf.py               # PDF 处理器
│       └── code.py              # 代码文件处理器
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # 日志工具
│   ├── exceptions.py            # 自定义异常
│   ├── validators.py            # 数据验证工具
│   └── helpers.py               # 通用辅助函数
│
├── api/
│   ├── __init__.py
│   ├── dependencies.py          # FastAPI 依赖注入
│   ├── middleware.py            # 中间件
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── repositories.py      # 仓库管理端点
│   │   ├── documents.py         # 文档处理端点
│   │   ├── queries.py           # 查询端点
│   │   └── health.py            # 健康检查端点
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── repository.py        # 仓库 API 模型
│       ├── document.py          # 文档 API 模型
│       └── query.py             # 查询 API 模型
│
├── mcp/
│   ├── __init__.py
│   ├── server.py                # MCP 服务器实现
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── library_search.py    # 库搜索工具
│   │   └── doc_retrieval.py     # 文档检索工具
│   └── schemas.py               # MCP 数据模型
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_adapters/
│   │   ├── test_services/
│   │   └── test_factories/
│   ├── integration/
│   │   ├── test_api/
│   │   └── test_workflows/
│   └── fixtures/
│       ├── sample_data.py
│       └── test_configs.py
│

├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── scripts/
│   ├── setup.py                 # 环境设置脚本
│   └── seed_data.py             # 测试数据生成
│
├── docs/
│   ├── api/                     # API 文档
│   ├── architecture/            # 架构文档
│   └── deployment/              # 部署文档
│
├── main.py                      # FastAPI 应用入口
├── pyproject.toml              # 项目配置
└── README.md                   # 项目说明
```

## 详细实施计划

### 第一阶段：基础架构搭建（1-2周）

#### 1.1 项目结构初始化
- [x] 创建新的目录结构
- [x] 设置包初始化文件
- [x] 配置开发环境（pyproject.toml 已存在且配置完整）

#### 1.4 现有代码分析与规划
- [x] 分析现有代码结构（embed_and_store.py, query_oceanbase.py, main.py 等）
- [x] 制定代码迁移计划（分模块逐步迁移）
- [x] 识别可复用的工具函数和业务逻辑

#### 1.2 配置管理系统
- [x] 实现 `config/settings.py`：支持多环境配置（使用Pydantic v2 discriminated unions）
- [x] 创建数据库配置模板（`config/metadata_db.py` - MySQL/PostgreSQL协议）
- [x] 创建服务配置模板（`config/vector_store.py`, `config/embedding.py`）
- [x] 实现配置验证机制（Pydantic自动验证和类型安全）

#### 1.3 核心接口定义 (已废弃)
- [x] ~~定义向量数据库接口~~ (已删除，直接使用 LangChain 标准接口)
- [x] ~~定义元数据数据库接口~~ (已废弃，直接使用 SQLAlchemy 标准接口)
- [x] ~~定义嵌入服务接口~~ (已废弃，直接使用 LangChain 标准接口)
- [x] ~~定义文档处理接口~~ (已废弃，业务逻辑直接在服务层实现)

**说明**: 为避免过度设计和不必要的抽象层，我们选择直接使用标准库接口：
- 向量存储：使用 LangChain 的 `VectorStore` 接口
- 嵌入服务：使用 LangChain 的 `Embeddings` 接口
- 数据库：使用 SQLAlchemy 的 `Session`, `Engine` 接口
- 文档处理：直接在业务服务层实现，使用 LangChain 的 `Document` 类型

### 第二阶段：适配器实现（2-3周）

#### 2.1 向量数据库适配器
- [ ] 实现 OceanBase 向量存储适配器
- [ ] 实现 ChromaDB 适配器
- [ ] 实现 PGVector 适配器
- [ ] 实现 Qdrant 适配器（可选）
- [ ] 实现 Weaviate 适配器（可选）

#### 2.2 元数据数据库适配器
- [ ] 实现 MySQL 适配器
- [ ] 实现 PostgreSQL 适配器
- [ ] 实现 SQLite 适配器
- [ ] 实现 OceanBase 元数据适配器

#### 2.3 嵌入服务适配器
- [ ] 实现 DashScope 嵌入适配器
- [ ] 实现 OpenAI 嵌入适配器
- [ ] 实现 Cohere 嵌入适配器（可选）
- [ ] 实现 HuggingFace 嵌入适配器（可选）

### 第三阶段：业务逻辑层（2周）

#### 3.1 工厂类实现
- [ ] 实现向量存储工厂
- [ ] 实现元数据数据库工厂
- [ ] 实现嵌入服务工厂
- [ ] 实现统一服务工厂

#### 3.2 业务服务实现
- [ ] 实现文档处理服务
- [ ] 实现向量操作服务
- [ ] 实现元数据操作服务
- [ ] 实现查询服务

#### 3.3 数据模型定义
- [ ] 定义仓库数据模型
- [ ] 定义文档数据模型
- [ ] 定义查询数据模型

### 第四阶段：API层重构（1-2周）

#### 4.1 依赖注入系统
- [ ] 实现 FastAPI 依赖注入
- [ ] 配置组件生命周期管理
- [ ] 实现中间件

#### 4.2 API端点重构
- [ ] 重构仓库管理端点
- [ ] 重构文档处理端点
- [ ] 重构查询端点
- [ ] 添加健康检查端点

#### 4.3 API模型定义
- [ ] 定义请求/响应模型
- [ ] 实现数据验证
- [ ] 添加API文档

### 第五阶段：MCP服务重构（1周）

#### 5.1 MCP工具重构
- [ ] 重构库搜索工具
- [ ] 重构文档检索工具
- [ ] 适配新的服务层

#### 5.2 MCP服务器优化
- [ ] 优化错误处理
- [ ] 添加日志记录
- [ ] 性能优化

### 第六阶段：测试与文档（1-2周）

#### 6.1 测试实现
- [ ] 单元测试（适配器、服务、工厂）
- [ ] 集成测试（API端点、工作流）
- [ ] 性能测试
- [ ] 端到端测试

#### 6.2 文档完善
- [ ] API文档
- [ ] 架构文档
- [ ] 部署文档
- [ ] 用户指南

### 第七阶段：现有代码迁移（2-3周）

#### 7.1 工具函数迁移
- [ ] 迁移 `markdown_utils.py` 到 `utils/markdown.py`
- [ ] 迁移 `embed_and_store.py` 中的工具函数到对应模块
- [ ] 迁移 `query_oceanbase.py` 中的连接函数到适配器

#### 7.2 业务逻辑迁移
- [ ] 将 `embed_and_store.py` 的核心逻辑迁移到 `core/services/document_service.py`
- [ ] 将 `query_oceanbase.py` 的查询逻辑迁移到 `core/services/query_service.py`
- [ ] 将 `repository_db.py` 的逻辑迁移到 `core/services/metadata_service.py`
- [ ] 将 `summarize.py` 的逻辑迁移到 `core/services/ai_service.py`

#### 7.3 API层重构
- [ ] 重构 `main.py` 中的 API 端点，使用新的服务层
- [ ] 更新依赖注入，使用工厂模式创建服务
- [ ] 保持 API 接口向后兼容

#### 7.4 MCP服务迁移
- [ ] 将 `mcp_server.py` 迁移到 `mcp/server.py`
- [ ] 更新 MCP 工具使用新的服务层
- [ ] 测试 MCP 功能完整性

### 第八阶段：部署与优化（1周）

#### 8.1 部署配置
- [ ] Docker配置
- [ ] 环境配置
- [ ] CI/CD配置

#### 8.2 性能优化
- [ ] 代码性能优化
- [ ] 数据库连接优化
- [ ] 缓存机制优化

## 现有代码迁移映射

### 代码迁移策略

| 现有文件 | 迁移目标 | 迁移内容 | 备注 |
|---------|---------|---------|------|
| `embed_and_store.py` | `core/services/document.py` | 文档嵌入和存储业务逻辑 | 重构为 DocumentService 类 |
| `query_oceanbase.py` | `core/services/vector.py` | 向量查询服务 | 重构为 VectorService 类 |
| `repository_db.py` | `core/services/metadata.py` | 元数据管理 | 重构为 MetadataService 类 |
| `summarize.py` | `core/services/ai.py` | AI 总结功能 | 重构为 AIService 类 |
| `markdown_utils.py` | `utils/markdown.py` | Markdown 处理工具 | 直接迁移工具函数 |
| `mcp_server.py` | `mcp/server.py` | MCP 服务器实现 | 更新为使用新的服务层 |
| `main.py` | `api/routes/` | API 端点分离 | 按功能分离到不同的路由文件 |
| `main.py` | `main.py` | 应用入口和配置 | 简化为应用启动和配置 |

### 函数迁移映射表

#### embed_and_store.py → core/services/document.py

| 原函数名 | 新函数名 | 所属类 | 功能描述 |
|---------|---------|--------|---------|
| `load_markdown_files()` | `load_documents()` | DocumentService | 加载 Markdown 文件 |
| `split_documents()` | `split_documents()` | DocumentService | 按标题分割文档 |
| `embed_and_store()` | `embed_and_store()` | DocumentService | 嵌入文档并存储 |
| `search_documents()` | `search_documents()` | DocumentService | 搜索相似文档 |

#### query_oceanbase.py → core/services/vector.py

| 原函数名 | 新函数名 | 所属类 | 功能描述 |
|---------|---------|--------|---------|
| `connect_to_vector_store()` | `get_vector_store()` | VectorService | 连接向量存储 |
| `search_documents()` | `similarity_search()` | VectorService | 向量相似度搜索 |

#### repository_db.py → core/services/metadata.py

| 原函数名 | 新函数名 | 所属类 | 功能描述 |
|---------|---------|--------|---------|
| `get_db_connection()` | `get_connection()` | MetadataService | 获取数据库连接 |
| `get_all_repositories()` | `get_all_repositories()` | MetadataService | 获取所有仓库 |
| `get_repository_by_name()` | `get_repository_by_name()` | MetadataService | 按名称获取仓库 |
| `get_repository_by_path()` | `get_repository_by_path()` | MetadataService | 按路径获取仓库 |
| `get_repository_by_id()` | `get_repository_by_id()` | MetadataService | 按ID获取仓库 |
| `add_repository()` | `create_repository()` | MetadataService | 创建仓库记录 |
| `update_repository()` | `update_repository()` | MetadataService | 更新仓库信息 |
| `update_repository_status()` | `update_repository_status()` | MetadataService | 更新仓库状态 |
| `update_repository_counts()` | `update_repository_counts()` | MetadataService | 更新仓库统计 |
| `delete_repository()` | `delete_repository()` | MetadataService | 删除仓库记录 |
| `delete_vector_table()` | `delete_vector_table()` | MetadataService | 删除向量表 |

#### summarize.py → core/services/ai.py

| 原函数名 | 新函数名 | 所属类 | 功能描述 |
|---------|---------|--------|---------|
| `summarize_search_results()` | `summarize_results()` | AIService | 总结搜索结果 |

#### markdown_utils.py → utils/markdown.py

| 原函数名 | 新函数名 | 所属模块 | 功能描述 |
|---------|---------|----------|---------|
| `count_code_blocks()` | `count_code_blocks()` | utils.markdown | 统计代码块数量 |
| `count_code_blocks_in_documents()` | `count_code_blocks_in_documents()` | utils.markdown | 统计文档中代码块总数 |

### 迁移优先级

**第一优先级（核心功能）：**
1. 向量存储适配器（OceanBase）
2. 文档服务（嵌入和存储）
3. 查询服务（相似度搜索）

**第二优先级（支持功能）：**
1. 元数据服务（仓库管理）
2. AI 服务（总结功能）
3. 工具函数迁移

**第三优先级（接口层）：**
1. API 端点重构
2. MCP 服务迁移
3. 依赖注入更新

### 向后兼容策略

1. **API 接口保持不变**：所有现有的 API 端点保持相同的请求/响应格式
2. **渐进式替换**：新旧代码并存，通过配置开关控制使用哪个实现
3. **功能对等**：确保迁移后的功能与原有功能完全一致

## 核心组件设计

### 1. 配置管理系统

```python
# config/settings.py
from pydantic import BaseSettings
from typing import Dict, Any, Optional

class DatabaseConfig(BaseSettings):
    type: str  # mysql, postgresql, sqlite, oceanbase
    host: Optional[str] = None
    port: Optional[int] = None
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    connection_params: Dict[str, Any] = {}

class VectorStoreConfig(BaseSettings):
    type: str  # oceanbase, chroma, pgvector, qdrant
    connection_params: Dict[str, Any] = {}

class EmbeddingConfig(BaseSettings):
    type: str  # dashscope, openai, cohere, huggingface
    api_key: Optional[str] = None
    model: str
    connection_params: Dict[str, Any] = {}

class Settings(BaseSettings):
    # 元数据数据库配置
    metadata_db: DatabaseConfig
    
    # 向量数据库配置
    vector_store: VectorStoreConfig
    
    # 嵌入服务配置
    embedding: EmbeddingConfig
    
    # 应用配置
    app_name: str = "Doc2Dev"
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
```

### 2. 接口定义

```python
# core/interfaces/vector_store.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.models.document import Document

class VectorStoreInterface(ABC):
    @abstractmethod
    def from_documents(
        self, 
        documents: List[Document], 
        embedding, 
        table_name: str,
        connection_args: Dict[str, Any],
        **kwargs
    ):
        """从文档列表创建向量存储（用于批量嵌入和存储）"""
        pass
    
    @abstractmethod
    def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """搜索相似文档"""
        pass
```

### 3. 工厂模式实现

```python
# core/factories/vector_store_factory.py
from typing import Dict, Type
from core.interfaces.vector_store import VectorStoreInterface
from adapters.vector_stores import (
    OceanBaseVectorStore,
    ChromaVectorStore,
    PGVectorStore
)

class VectorStoreFactory:
    _stores: Dict[str, Type[VectorStoreInterface]] = {
        "oceanbase": OceanBaseVectorStore,
        "chroma": ChromaVectorStore,
        "pgvector": PGVectorStore,
    }
    
    @classmethod
    def create(cls, store_type: str, **kwargs) -> VectorStoreInterface:
        if store_type not in cls._stores:
            raise ValueError(f"Unsupported vector store type: {store_type}")
        
        store_class = cls._stores[store_type]
        return store_class(**kwargs)
    
    @classmethod
    def register(cls, store_type: str, store_class: Type[VectorStoreInterface]):
        """注册新的向量存储类型"""
        cls._stores[store_type] = store_class
```

### 4. 依赖注入系统

通过 FastAPI 的依赖注入系统管理组件生命周期：
- 配置管理：统一的设置获取
- 组件创建：通过工厂模式创建各类组件
- 服务注入：将底层组件注入到业务服务中
- 生命周期管理：确保组件的正确初始化和清理

## 配置示例

### 环境配置 (.env)
```env
# 向量数据库
VECTOR_STORE_TYPE=oceanbase
VECTOR_STORE_CONNECTION_PARAMS_HOST=127.0.0.1
VECTOR_STORE_CONNECTION_PARAMS_PORT=2881
VECTOR_STORE_CONNECTION_PARAMS_USER=root@test
VECTOR_STORE_CONNECTION_PARAMS_PASSWORD=admin
VECTOR_STORE_CONNECTION_PARAMS_DB_NAME=doc2dev

# 嵌入服务
EMBEDDING_TYPE=dashscope
EMBEDDING_API_KEY=your_dashscope_api_key
EMBEDDING_MODEL=text-embedding-v3

# AI 总结服务
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://openrouter.ai/api/v1

# GitHub 集成
GITHUB_TOKEN=your_github_token

# 应用配置
DEBUG=false
LOG_LEVEL=INFO
```

## 重构策略

### 1. 渐进式重构
- 保持现有API兼容性
- 逐步替换底层实现
- 提供配置开关

### 2. 测试策略
- 并行运行新旧系统
- A/B测试验证功能
- 性能对比测试

### 3. 代码组织
- 逐步迁移现有代码到新架构
- 保持功能完整性
- 清理冗余代码

## 扩展指南

### 添加新的向量数据库支持
1. 在 `adapters/vector_stores/` 下创建新的适配器
2. 实现 `VectorStoreInterface` 接口
3. 在工厂类中注册新的适配器
4. 添加相应的配置选项
5. 编写单元测试和集成测试

### 添加新的嵌入服务支持
1. 在 `adapters/embeddings/` 下创建新的适配器
2. 实现 `EmbeddingInterface` 接口
3. 在工厂类中注册新的适配器
4. 添加相应的配置选项
5. 编写单元测试

## 风险评估与缓解

### 技术风险
- **数据迁移风险**：提供完整的备份和回滚方案
- **性能风险**：进行充分的性能测试和优化
- **兼容性风险**：保持API向后兼容

### 项目风险
- **时间风险**：分阶段实施，优先核心功能
- **资源风险**：合理分配开发资源
- **质量风险**：建立完善的测试体系

## 成功标准

1. **功能完整性**：所有现有功能正常工作
2. **性能指标**：响应时间不超过现有系统的120%
3. **可扩展性**：能够轻松添加新的数据库和服务支持
4. **代码质量**：测试覆盖率达到80%以上
5. **文档完整性**：提供完整的API和架构文档

这个重构计划将使 Doc2Dev 成为一个真正可扩展、可维护的多数据库支持平台。
