# Doc2Dev 多源支持实施计划

## 项目目标
扩展 Doc2Dev 系统以支持 GitHub 和 GitLab 仓库索引（使用 Token 认证），提供统一的多源管理界面。

## 基于现有 GitHub 工具的接口设计

### 核心接口抽象
基于 `backend/utils/github.py` 中的现有方法，设计统一的 Git 平台接口：

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Tuple

class GitPlatformAdapter(ABC):
    """Git 平台适配器抽象基类"""

    @abstractmethod
    def get_git_token(self) -> str:
        """获取平台 Token（对应 get_github_token）"""
        pass

    @abstractmethod
    def parse_git_url(self, url: str) -> str:
        """解析平台 URL 获取 owner/repo（对应 parse_github_url）"""
        pass

    @abstractmethod
    def extract_org_repo(self, url: str) -> Tuple[str, str]:
        """提取组织和仓库名（对应 extract_org_repo）"""
        pass

    @abstractmethod
    def get_repo_contents_using_trees(self, repo_client) -> List:
        """获取仓库文件树（对应 get_repo_contents_using_trees）"""
        pass

    @abstractmethod
    async def download_md_files_with_progress(
        self,
        repo_url: str,
        output_dir: str,
        progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """下载 Markdown 文件并支持进度回调（对应 download_md_files_with_progress）"""
        pass

    @abstractmethod
    def get_git_name(self) -> str:
        """获取平台名称"""
        pass

    @abstractmethod
    def get_git_api_base_url(self) -> str:
        """获取 API 基础 URL"""
        pass
```

## 实施步骤

### Phase 1: 数据库结构调整 ✅
- [x] 1.1 修改 `repositories` 表结构，添加 `source` 字段
- [x] 1.2 更新数据库模型类 (`Repository`)
- [x] 1.3 创建数据库迁移脚本（已手动执行迁移）
- [x] 1.4 更新现有数据的 `source` 字段为 `github`
- [x] 1.5 更新 API 模型和路由支持 `source` 字段
- [x] 1.6 更新用户数据库表结构

### Phase 2: Git 平台核心模块创建 ✅
- [x] 2.1 创建 `core/git` 目录结构
  - [x] 2.1.1 创建 `backend/core/git/__init__.py` - GitPlatformAdapter 抽象基类
  - [x] 2.1.2 创建 `backend/core/git/utils.py` - Git 工具函数（URL 解析、平台检测等）
- [x] 2.2 迁移和重构现有 GitHub 代码
  - [x] 2.2.1 将 `utils/github.py` 重构为 `backend/core/git/github.py` - GitHub 适配器
  - [x] 2.2.2 重构方法名：`get_github_token()` → `get_git_token()`
  - [x] 2.2.3 重构方法名：`parse_github_url()` → `parse_git_url()`
  - [x] 2.2.4 保持 `extract_org_repo()` 和 `get_repo_contents_using_trees()` 逻辑
  - [x] 2.2.5 保持 `download_md_files_with_progress()` 核心逻辑
- [x] 2.3 创建 GitLab 支持基础结构
  - [x] 2.3.1 创建 `backend/core/git/gitlab.py` - GitLab 适配器基础实现
  - [x] 2.3.2 实现 GitLab Token 获取逻辑
  - [x] 2.3.3 实现 GitLab URL 解析逻辑
  - [ ] 2.3.4 实现 GitLab 文件树遍历和文件下载逻辑（待 Phase 4 完成）
- [x] 2.4 创建工厂类
  - [x] 2.4.1 创建 `backend/core/factories/git.py` - `GitFactory` 和 `GitAdapterManager`

### Phase 3: Git 工具和配置 ✅
- [x] 3.1 完善 Git 工具模块 (`backend/core/git/utils.py`)
  - [x] 3.1.1 实现 Git URL 解析器 `GitUrlParser` - 支持 HTTPS/SSH URL 格式
  - [x] 3.1.2 实现平台自动检测 `PlatformDetector` - 自动识别 GitHub/GitLab
  - [x] 3.1.3 支持 GitHub 和 GitLab URL 格式检测和规范化
  - [x] 3.1.4 支持自定义域名检测（GitHub Enterprise/自托管 GitLab）
- [x] 3.2 扩展配置管理
  - [x] 3.2.1 更新 `backend/config/settings.py` - 添加 GitLab 配置支持（GITLAB_URL, GITLAB_TOKEN）
  - [x] 3.2.2 支持自定义 GitHub 企业版配置（GITHUB_URL）
  - [x] 3.2.3 创建 `backend/config/git.py` - 专门的 Git 平台配置管理
- [x] 3.3 添加配置验证和诊断工具
  - [x] 3.3.1 创建 `backend/core/git/config_validator.py` - 配置验证器
  - [x] 3.3.2 添加 URL 验证和错误处理
  - [x] 3.3.3 集成配置管理到 Git 适配器中

### Phase 4: GitLab API 集成 ✅
- [x] 4.1 安装 GitLab API 客户端库 (`python-gitlab`)
- [x] 4.2 实现 GitLab 仓库信息获取（项目获取、认证、URL 编码处理）
- [x] 4.3 实现 GitLab 文件树遍历（对应 GitHub 的 Trees API）
- [x] 4.4 实现 GitLab 文件内容下载（对应 GitHub 的 Blob API）
- [x] 4.5 处理 GitLab 特有的 API 差异和错误码
- [x] 4.6 完成 GitLab 适配器的所有核心方法实现
- [x] 4.7 测试 GitLab URL 解析、平台检测和适配器创建

### Phase 5: 配置管理 ✅ (已在 Phase 3 中完成)
- [x] 5.1 扩展环境变量配置支持 GITHUB_URL/GITHUB_TOKEN 和 GITLAB_URL/GITLAB_TOKEN
- [x] 5.2 实现配置验证和错误提示
- [x] 5.3 设置默认 URL 值（github.com 和 gitlab.com）
- [x] 5.4 创建配置管理类 `GitPlatformConfig`

### Phase 6: 服务层重构 ✅
- [x] 6.1 重构 `RepositoryService` 支持多源（已在 Phase 1 中完成）
- [x] 6.2 更新 `DocumentService` 处理不同源的文档（无需修改，通用处理）
- [x] 6.3 修改后台任务处理器 `repository_processor.py` 支持多平台
  - [x] 6.3.1 更新导入：使用 `GitFactory` 替代 `utils.github`
  - [x] 6.3.2 添加自动平台检测和适配器创建
  - [x] 6.3.3 更新仓库创建逻辑支持 `source` 参数
  - [x] 6.3.4 使用适配器的 `download_md_files_with_progress` 方法
- [x] 6.4 更新路由层支持多平台
  - [x] 6.4.1 更新 `routes/repository.py` 使用 Git 适配器
  - [x] 6.4.2 替换 `extract_org_repo` 调用为适配器方法

### Phase 7: API 接口更新 ✅
- [x] 7.1 更新仓库创建 API 支持 `source` 参数（已在 Phase 1 中完成）
- [x] 7.2 更新仓库列表 API 返回 `source` 信息
  - [x] 7.2.1 仓库列表 API 已返回 `source` 字段
  - [x] 7.2.2 修复仓库详情 API 缺少 `source` 字段的问题
- [x] 7.3 添加平台配置验证 API
  - [x] 7.3.1 创建平台配置 API 模型（PlatformConfigRequest/Response 等）
  - [x] 7.3.2 实现 `/platforms/status` - 获取所有平台状态
  - [x] 7.3.3 实现 `/platforms/validate` - 验证平台配置
  - [x] 7.3.4 实现 `/platforms/validate-url` - 验证和解析仓库 URL
  - [x] 7.3.5 实现 `/platforms/config/{platform}` - 获取特定平台配置
  - [x] 7.3.6 集成平台路由到主应用程序
- [x] 7.4 更新 WebSocket 进度回调支持多平台
  - [x] 7.4.1 在进度消息中添加 `platform` 和 `source` 字段
  - [x] 7.4.2 更新初始下载消息包含平台信息
  - [x] 7.4.3 在处理器中设置当前平台和源信息

### Phase 8: 前端界面改造
- [ ] 8.1 更新仓库列表显示不同源的图标
- [ ] 8.2 创建多源仓库添加界面
- [ ] 8.3 添加 GitHub/GitLab URL 和 Token 配置界面
- [ ] 8.4 更新 URL 输入验证逻辑

### Phase 9: 文档和部署
- [ ] 9.1 更新 API 文档
- [ ] 9.2 编写用户使用指南
- [ ] 9.3 更新部署配置文档
- [ ] 9.4 准备生产环境部署

## 📁 涉及的目录和文件结构

### 🔧 **需要修改的现有文件**

#### 1. **数据库相关**
```
db.sql                                    # 需要添加 source 字段的 SQL 脚本
backend/core/models/repository.py         # Repository 模型类，添加 source 字段
backend/core/services/repository.py       # RepositoryService，支持多源操作
```

#### 2. **现有文件迁移和重构**
```
backend/utils/github.py                   # 🔄 迁移到 core/git/utils/github.py
backend/tasks/repository_processor.py     # 🔧 修改：支持多平台的后台任务处理
backend/routes/repository.py              # 🔧 修改：更新仓库 API 支持多源
backend/core/models/api.py                # 🔧 修改：API 模型，添加 source 相关字段
backend/config/settings.py               # 🔧 修改：添加 GitLab 配置支持
backend/main.py                          # 🔧 修改：更新服务初始化和导入路径
```

#### 3. **前端文件**
```
frontend/app/page.tsx                    # 🔧 修改：主页仓库列表，显示源类型
frontend/components/                     # 🔧 修改：需要更新的组件（待具体分析）
```

### 🆕 **需要创建的新文件和目录**

#### 1. **Git 平台核心模块**
```
backend/core/git/                        # 🆕 新目录：Git 平台相关代码
├── __init__.py                         # 🆕 新建
├── github.py                           # 🔄 从 utils/github.py 重构：GitHub 适配器
├── gitlab.py                           # 🆕 新建：GitLab 适配器
└── utils.py                            # 🆕 新建：Git 工具函数（URL 解析、平台检测等）
```

#### 2. **工厂类扩展（复用现有目录）**
```
backend/core/factories/git.py            # 🆕 新建：GitFactory
```

#### 3. **前端新组件**
```
frontend/components/git-platforms/       # 🆕 新目录：Git 平台相关组件
├── PlatformIcon.tsx                    # 🆕 新建：平台图标组件
├── PlatformSelector.tsx                # 🆕 新建：平台选择器
├── UrlValidator.tsx                    # 🆕 新建：URL 验证组件
└── ConfigPanel.tsx                     # 🆕 新建：配置面板
```

### 📊 **文件统计总结**

#### **按阶段分类**
- **Phase 1 (数据库)**: 3 个文件修改
- **Phase 2-3 (Git 核心模块)**: 4 个新文件 + 1 个重构
- **Phase 4 (GitLab 集成)**: 1 个依赖文件修改
- **Phase 5-6 (配置和服务)**: 4 个文件修改
- **Phase 7-8 (API 和前端)**: 6-8 个文件修改/新建

#### **总计统计**
- **修改现有文件**: ~10-12 个
- **新建文件**: ~12-15 个
- **新建目录**: ~2-3 个
- **重构文件**: 1 个 (`utils/github.py` → `core/git/github.py`)
- **总计影响文件**: ~22-27 个

### 🎯 **核心目录结构变化**

```
backend/
├── core/
│   ├── git/                    # 🆕 新增：Git 平台核心模块
│   │   ├── __init__.py         # 🆕 新建
│   │   ├── github.py           # 🔄 从 utils/github.py 重构
│   │   ├── gitlab.py           # 🆕 新建：GitLab 适配器
│   │   └── utils.py            # 🆕 新建：Git 工具函数
│   ├── factories/
│   │   └── git.py              # 🆕 新增：Git 工厂
│   ├── models/                 # 🔧 修改：添加 source 支持
│   └── services/               # 🔧 修改：多源支持
├── utils/
│   └── github.py               # 🔄 重构到 core/git/github.py
└── config/
    └── settings.py             # 🔧 修改：添加 GitLab 配置

frontend/
├── components/
│   └── git-platforms/          # 🆕 新增：平台相关组件
└── app/
    └── page.tsx                # 🔧 修改：显示源类型
```

## 技术细节

### 环境变量配置
```bash
# GitHub (默认使用 github.com，可选指定企业版URL)
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_URL=https://github.com  # 可选，默认值

# GitHub Enterprise Server 示例
# GITHUB_URL=https://github.company.com
# GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# GitLab (默认使用 gitlab.com，可选指定自托管URL)
GITLAB_TOKEN=glpat_xxxxxxxxxxxx
GITLAB_URL=https://gitlab.com  # 可选，默认值

# 自托管 GitLab 示例
# GITLAB_URL=https://gitlab.company.com
# GITLAB_TOKEN=glpat_xxxxxxxxxxxx
```

### 具体实现设计

#### 1. GitHub 适配器实现
```python
class GitHubAdapter(GitPlatformAdapter):
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('GITHUB_URL', 'https://github.com')
        self.api_url = self._get_api_url()

    def get_git_token(self) -> str:
        """重构自 get_github_token()"""
        return os.getenv("GITHUB_TOKEN", "")

    def parse_git_url(self, url: str) -> str:
        """重构自 parse_github_url()，支持自定义域名"""
        # 支持自定义 GitHub 企业版域名
        domain_pattern = self._get_domain_pattern()
        # 复用现有的 URL 解析逻辑

    def get_git_name(self) -> str:
        return "github"

    def get_git_api_base_url(self) -> str:
        return self.api_url

    def _get_api_url(self):
        if self.base_url == 'https://github.com':
            return 'https://api.github.com'
        else:
            return f"{self.base_url}/api/v3"
```

#### 2. GitLab 适配器实现
```python
class GitLabAdapter(GitPlatformAdapter):
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('GITLAB_URL', 'https://gitlab.com')
        self.api_url = f"{self.base_url}/api/v4"

    def get_git_token(self) -> str:
        return os.getenv("GITLAB_TOKEN", "")

    def parse_git_url(self, url: str) -> str:
        """解析 GitLab URL，类似 GitHub 逻辑"""
        # 支持 gitlab.com 和自托管 GitLab

    def get_git_name(self) -> str:
        return "gitlab"

    def get_git_api_base_url(self) -> str:
        return self.api_url

    async def download_md_files_with_progress(self, repo_url: str, output_dir: str, progress_callback=None):
        """使用 python-gitlab 库实现，保持与 GitHub 相同的接口"""
        # 1. 解析 URL
        # 2. 获取项目
        # 3. 遍历文件树
        # 4. 下载 Markdown 文件
        # 5. 进度回调
```

#### 3. Git 工厂类 (`backend/core/factories/git.py`)
```python
from core.git.github import GitHubAdapter
from core.git.gitlab import GitLabAdapter
from core.git.utils import GitUrlParser

class GitFactory:
    @staticmethod
    def create_adapter(url: str):
        """根据 URL 自动检测平台并创建适配器"""
        if GitUrlParser.is_github_url(url):
            return GitHubAdapter()
        elif GitUrlParser.is_gitlab_url(url):
            return GitLabAdapter()
        else:
            raise ValueError(f"Unsupported platform URL: {url}")

    @staticmethod
    def create_adapter_by_platform(platform: str):
        """根据平台名称创建适配器"""
        if platform == "github":
            return GitHubAdapter()
        elif platform == "gitlab":
            return GitLabAdapter()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
```

#### 4. Git 工具函数 (`backend/core/git/utils.py`)
```python
import os

class GitUrlParser:
    @staticmethod
    def is_github_url(url: str) -> bool:
        """检测是否为 GitHub URL"""
        github_domains = [
            'github.com',
            os.getenv('GITHUB_URL', '').replace('https://', '').replace('http://', '')
        ]
        return any(domain in url for domain in github_domains if domain)

    @staticmethod
    def is_gitlab_url(url: str) -> bool:
        """检测是否为 GitLab URL"""
        gitlab_domains = [
            'gitlab.com',
            os.getenv('GITLAB_URL', '').replace('https://', '').replace('http://', '')
        ]
        return any(domain in url for domain in gitlab_domains if domain)

class PlatformDetector:
    @staticmethod
    def detect_platform(url: str) -> str:
        """自动检测 Git 平台类型"""
        if GitUrlParser.is_github_url(url):
            return "github"
        elif GitUrlParser.is_gitlab_url(url):
            return "gitlab"
        else:
            raise ValueError(f"Unsupported platform URL: {url}")
```

### 数据库变更
```sql
ALTER TABLE repositories
ADD COLUMN source ENUM('github', 'gitlab') NOT NULL DEFAULT 'github';

-- 更新现有数据
UPDATE repositories SET source = 'github' WHERE source IS NULL;
```

### API 端点设计
```
POST /api/repositories           # 统一仓库创建接口，自动检测平台
GET  /api/repositories           # 列表（包含 source 信息）
GET  /api/platforms/config       # 获取平台配置状态
POST /api/platforms/validate     # 验证平台配置
```

### 重构现有代码的映射关系

#### **文件迁移和重构**
```
现有文件                          -> 新文件位置
utils/github.py                  -> core/git/github.py (重构为适配器)
```

#### **方法映射关系**
```
现有方法                          -> 新接口方法
get_github_token()               -> GitHubAdapter.get_git_token()
parse_github_url()               -> GitHubAdapter.parse_git_url()
extract_org_repo()               -> GitHubAdapter.extract_org_repo()
get_repo_contents_using_trees()  -> GitHubAdapter.get_repo_contents_using_trees()
download_md_files_with_progress() -> GitHubAdapter.download_md_files_with_progress()
```

#### **导入路径变更**
```
旧导入路径                        -> 新导入路径
from utils.github import *       -> from core.git.github import GitHubAdapter
                                 -> from core.git.gitlab import GitLabAdapter
                                 -> from core.git.utils import GitUrlParser, PlatformDetector
                                 -> from core.factories.git import GitFactory
```

## 风险和注意事项

1. **API 差异**: GitLab API 结构与 GitHub 有差异，需要适配
2. **认证安全**: Token 存储和传输安全
3. **向后兼容**: 确保现有 GitHub 功能不受影响
4. **错误处理**: 不同平台的错误码和消息处理
5. **性能**: GitLab API 性能可能与 GitHub 不同

## 预估时间
- Phase 1-3: 数据库和抽象层 (2-3 天)
- Phase 4-6: GitLab 集成和重构 (3-4 天)
- Phase 7-9: API、前端和文档 (2-3 天)
- **总计**: 7-10 天

## 成功标准
- [ ] 支持 GitHub 和 GitLab 仓库索引
- [ ] 保持现有 GitHub 功能完全兼容
- [ ] 统一的用户界面
- [ ] 性能不低于现有系统
