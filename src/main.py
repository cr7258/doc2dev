#!/usr/bin/env python3
"""
FastAPI server that receives GitHub repository URLs and downloads markdown files.
"""

import os
import re
import sys
import time
import asyncio
import logging
import json
import tempfile
import shutil
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urlparse
from dotenv import load_dotenv

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from github import Github, Auth, GithubException
from embed_and_store import load_markdown_files, split_documents, embed_and_store
from query_oceanbase import search_documents, connect_to_vector_store
from repository_db import get_all_repositories, get_repository_by_name, add_repository, update_repository, delete_repository

# 添加带进度回调的 embed_and_store 函数
async def embed_and_store_with_progress(documents, table_name, drop_old=False, progress_callback=None):
    """
    嵌入文档并存储到向量数据库，支持进度回调
    """
    total_docs = len(documents)
    
    # 调用原始的 embed_and_store 函数，但在过程中添加进度更新
    try:
        # 初始化进度
        if progress_callback:
            await progress_callback(0, total_docs, "开始嵌入文档...")
        
        # 创建向量存储
        vector_store = embed_and_store(documents, table_name=table_name, drop_old=drop_old)
        
        # 完成进度
        if progress_callback:
            await progress_callback(total_docs, total_docs, "文档嵌入完成")
            
        return vector_store
    except Exception as e:
        if progress_callback:
            await progress_callback(0, 1, f"嵌入文档时出错: {str(e)}")
        raise e

# Load environment variables from .env file
load_dotenv()

# Get GitHub token from environment variables
DEFAULT_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
print(f"Loaded GitHub token from .env: {'*' * (len(DEFAULT_GITHUB_TOKEN) - 4) + DEFAULT_GITHUB_TOKEN[-4:] if DEFAULT_GITHUB_TOKEN else 'No token found'}")

app = FastAPI(
    title="GitHub Markdown Downloader",
    description="A service that downloads markdown files from GitHub repositories",
    version="1.0.0"
)

# 创建一个连接管理器，用于管理 WebSocket 连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_json(self, data: Dict[str, Any], client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(data)
        else:
            print(f"Warning: Client {client_id} not found in active connections")

    async def broadcast(self, data: Dict[str, Any]):
        for connection in self.active_connections.values():
            await connection.send_json(data)

manager = ConnectionManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 前后端分离架构，不再需要挂载静态文件目录

class RepositoryRequest(BaseModel):
    """Request model for repository URL"""
    repo_url: HttpUrl
    library_name: Optional[str] = None  # 可选参数，如果前端没有提供，则自动从 URL 生成
    client_id: Optional[str] = None  # 客户端 ID，用于 WebSocket 连接

class DownloadResponse(BaseModel):
    """Response model for download status"""
    status: str
    message: str
    files_count: int = 0
    files: List[str] = []
    download_url: Optional[str] = None
    embedding_status: Optional[str] = None
    embedding_count: int = 0

# No need to store temporary directories anymore - files are saved directly to the project directory

def parse_github_url(url: str) -> str:
    """
    Parse a GitHub URL to extract the repository name in the format 'owner/repo'.

    Args:
        url: GitHub repository URL

    Returns:
        Repository name in the format 'owner/repo'
    """
    # 记录原始 URL 用于调试
    logger.info(f"Parsing GitHub URL: {url}")
    
    # 移除 URL 中的空白字符
    url = url.strip()
    
    # 移除末尾的 .git 后缀（如果存在）
    if url.endswith(".git"):
        url = url[:-4]
    
    # 处理不同的 URL 格式
    try:
        # 使用正则表达式匹配常见的 GitHub URL 格式
        if re.search(r'github\.com[/:]([\w.-]+)/([\w.-]+)', url):
            match = re.search(r'github\.com[/:]([\w.-]+)/([\w.-]+)', url)
            if match:
                owner, repo = match.groups()
                logger.info(f"Extracted owner: {owner}, repo: {repo}")
                return f"{owner}/{repo}"
        
        # 尝试解析 HTTPS URL 格式
        if "github.com/" in url:
            parts = url.split("github.com/")
            if len(parts) > 1 and "/" in parts[1]:
                repo_parts = parts[1].split("/")
                if len(repo_parts) >= 2:
                    owner, repo = repo_parts[0], repo_parts[1]
                    logger.info(f"Extracted from HTTPS URL - owner: {owner}, repo: {repo}")
                    return f"{owner}/{repo}"
        
        # 尝试解析 SSH URL 格式
        if "git@github.com:" in url:
            parts = url.split("git@github.com:")
            if len(parts) > 1 and "/" in parts[1]:
                repo_parts = parts[1].split("/")
                if len(repo_parts) >= 2:
                    owner, repo = repo_parts[0], repo_parts[1]
                    logger.info(f"Extracted from SSH URL - owner: {owner}, repo: {repo}")
                    return f"{owner}/{repo}"
    
        # 如果上述方法都失败，尝试直接从 URL 中提取最后两个路径组件
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split("/") if p]
        if len(path_parts) >= 2:
            owner, repo = path_parts[-2], path_parts[-1]
            logger.info(f"Extracted from URL path - owner: {owner}, repo: {repo}")
            return f"{owner}/{repo}"
            
        raise ValueError(f"无法从 URL 中提取仓库信息")
    except Exception as e:
        logger.error(f"Error parsing GitHub URL: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"解析 GitHub URL 时出错: {str(e)}")
    
    raise ValueError(f"无效的 GitHub URL 格式: {url}")

def extract_org_repo(url: str) -> Tuple[str, str]:
    """
    从 GitHub URL 中提取组织和仓库名称

    Args:
        url: GitHub 仓库 URL

    Returns:
        Tuple[str, str]: 组织名和仓库名的元组
    """
    repo_name = parse_github_url(url)
    parts = repo_name.split('/')
    
    if len(parts) != 2:
        raise ValueError(f"Invalid repository name format: {repo_name}")
        
    return parts[0], parts[1]

def get_contents_recursively(repo, path):
    """
    Recursively get all contents of a repository.

    Args:
        repo: GitHub repository object
        path: Path to get contents from

    Returns:
        list: List of content objects
    """
    contents = []

    try:
        items = repo.get_contents(path)

        for item in items:
            if item.type == "dir":
                # Recursively get contents of directories
                contents.extend(get_contents_recursively(repo, item.path))
            else:
                contents.append(item)
    except Exception as e:
        print(f"Error accessing {path}: {e}")

    return contents

async def download_md_files_with_progress(repo_url, output_dir, progress_callback=None):
    """
    下载 GitHub 仓库中的所有 Markdown 文件，支持进度回调

    Args:
        repo_url (str): GitHub 仓库 URL
        output_dir (str): 保存下载文件的目录
        progress_callback (callable, optional): 进度回调函数，接收 current, total, message 参数

    Returns:
        list: 下载的 Markdown 文件路径列表
    """
    try:
        # 解析 GitHub URL 获取仓库名称
        try:
            repo_name = parse_github_url(str(repo_url))
            logger.info(f"Parsed repo name: {repo_name}")
        except ValueError as e:
            logger.error(f"Error parsing GitHub URL: {str(e)}")
            if progress_callback:
                await progress_callback(0, 1, f"URL 格式错误: {str(e)}")
            return []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")
        
        # 发送进度更新
        if progress_callback:
            await progress_callback(3, 10, f"已创建输出目录: {output_dir}")

        # 获取 GitHub 令牌
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            logger.error("GitHub token not found in environment variables")
            if progress_callback:
                await progress_callback(0, 1, "GitHub token not found in environment variables")
            return []

        # 打印令牌信息（隐藏大部分内容）
        masked_token = '*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'
        logger.info(f"Loaded GitHub token from .env: {masked_token}")
        
        # 创建 GitHub 实例
        try:
            g = Github(token)
            # 检查 API 速率限制
            rate_limit = g.get_rate_limit()
            logger.info(f"GitHub API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit} requests remaining")
        except Exception as e:
            logger.error(f"Error initializing GitHub API: {str(e)}")
            if progress_callback:
                await progress_callback(0, 1, f"初始化 GitHub API 时出错: {str(e)}")
            return []

        # 获取仓库
        try:
            logger.info(f"Getting repository: {repo_name}")
            repo = g.get_repo(repo_name)
            logger.info(f"Successfully got repository: {repo.full_name}")
        except Exception as e:
            logger.error(f"Error getting repository {repo_name}: {str(e)}")
            if progress_callback:
                await progress_callback(0, 1, f"获取仓库时出错: {str(e)}")
            return []

        # 发送进度更新：开始获取仓库内容
        if progress_callback:
            await progress_callback(0, 1, "正在获取仓库内容...")

        # 递归获取所有内容
        try:
            logger.info("Getting repository contents recursively...")
            all_contents = get_contents_recursively(repo, "")
            logger.info(f"Found {len(all_contents)} total files in repository")
        except Exception as e:
            logger.error(f"Error getting repository contents: {str(e)}")
            if progress_callback:
                await progress_callback(0, 1, f"获取仓库内容时出错: {str(e)}")
            return []

        # 过滤出 Markdown 文件
        md_files = [content for content in all_contents if content.path.lower().endswith(".md")]
        logger.info(f"Found {len(md_files)} Markdown files in repository")

        if not md_files:
            logger.warning("No Markdown files found in repository")
            if progress_callback:
                await progress_callback(0, 1, "仓库中未找到 Markdown 文件")
            return []

        # 发送进度更新：开始下载文件
        if progress_callback:
            await progress_callback(0, len(md_files), f"找到 {len(md_files)} 个 Markdown 文件，开始下载...")

        # 下载 Markdown 文件
        downloaded_files = []
        for i, content in enumerate(md_files):
            try:
                # 创建必要的目录结构
                file_path = os.path.join(output_dir, content.path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # 下载文件内容
                logger.info(f"Downloading file: {content.path}")
                file_content = repo.get_contents(content.path).decoded_content

                # 保存文件
                with open(file_path, "wb") as f:
                    f.write(file_content)

                downloaded_files.append(file_path)
                logger.info(f"Successfully downloaded: {file_path}")

                # 更新进度
                if progress_callback:
                    await progress_callback(i + 1, len(md_files), f"已下载 {i + 1}/{len(md_files)}: {content.path}")
            except Exception as e:
                logger.error(f"Error downloading file {content.path}: {str(e)}")
                # 继续下载其他文件，不中断整个过程

        return downloaded_files

    except GithubException as e:
        error_message = f"GitHub API error: {e.status} - {e.data.get('message', str(e))}"
        print(f"GitHub Exception: {error_message}")
        print(f"Exception details: {e}")
        
        # 发送错误进度更新
        if progress_callback:
            await progress_callback(0, 1, error_message)
            
        return []
    except Exception as e:
        error_message = f"Error downloading markdown files: {str(e)}"
        print(error_message)
        
        # 发送错误进度更新
        if progress_callback:
            await progress_callback(0, 1, error_message)
        
        return []

@app.get("/")
async def root():
    """API 根端点，返回基本信息"""
    return {
        "status": "success",
        "message": "Doc2Dev API is running",
        "version": "1.0.0",
        "endpoints": [
            "/api/info",
            "/download/",
            "/query/"
        ]
    }

@app.get("/api/info")
async def api_info():
    """API info endpoint that returns basic information about the API"""
    return {"message": "GitHub Markdown Downloader API", "version": "1.0.0"}

@app.post("/download/", response_model=DownloadResponse)
async def download_repository(repo_request: RepositoryRequest):
    """
    Download markdown files from a GitHub repository directly to the project directory
    and automatically embed them if embedding functionality is available.

    Args:
        repo_request: Repository request containing URL and optional client_id for WebSocket updates

    Returns:
        JSON response with download status and embedding status
    """
    try:
        # 从 URL 提取组织和仓库名称
        org, repo = extract_org_repo(str(repo_request.repo_url))
        
        # 如果没有提供 library_name，则自动生成
        table_name = repo_request.library_name
        if not table_name:
            table_name = f"{org}_{repo}"
        
        # 确保表名中的连字符替换为下划线
        table_name = table_name.replace("-", "_")
        
        # 获取客户端 ID（如果有）
        client_id = repo_request.client_id
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {temp_dir}")
        
        # 发送初始进度信息
        if client_id:
            await manager.send_json({
                "type": "download",
                "status": "started",
                "progress": 0,
                "message": f"开始下载 {org}/{repo} 仓库..."
            }, client_id)

        # 定义下载进度回调函数
        async def download_progress_callback(current, total, message):
            if client_id:
                progress = int((current / total) * 100) if total > 0 else 0
                await manager.send_json({
                    "type": "download",
                    "status": "in_progress",
                    "progress": progress,
                    "current": current,
                    "total": total,
                    "message": message
                }, client_id)

        # 下载 Markdown 文件，使用带进度的版本
        md_files = await download_md_files_with_progress(
            repo_request.repo_url, 
            temp_dir, 
            progress_callback=download_progress_callback if client_id else None
        )
        
        if not md_files:
            if client_id:
                await manager.send_json({
                    "type": "download",
                    "status": "error",
                    "progress": 0,
                    "message": "仓库中未找到 Markdown 文件"
                }, client_id)
            
            shutil.rmtree(temp_dir)
            return DownloadResponse(
                status="error",
                message="No markdown files found in the repository"
            )

        # 下载完成通知
        if client_id:
            await manager.send_json({
                "type": "download",
                "status": "completed",
                "progress": 100,
                "message": f"已下载 {len(md_files)} 个 Markdown 文件"
            }, client_id)
        
        # 加载 Markdown 文件
        documents = load_markdown_files(md_files)
        
        # 分割文档
        docs = split_documents(documents)

        # 嵌入并存储文档，使用带进度的版本
        if client_id:
            await manager.send_json({
                "type": "embedding",
                "status": "started",
                "progress": 0,
                "message": "开始嵌入文档..."
            }, client_id)
        
        # 定义嵌入进度回调函数
        async def embedding_progress_callback(current, total, message):
            if client_id:
                await manager.send_json({
                    "type": "embedding",
                    "status": "in_progress",
                    "progress": int((current / total) * 100) if total > 0 else 0,
                    "current": current,
                    "total": total,
                    "message": message
                }, client_id)
                    
        try:
            # 嵌入并存储文档
            vector_store = await embed_and_store_with_progress(
                docs, 
                table_name=table_name, 
                drop_old=True,
                progress_callback=embedding_progress_callback
            )
            
            # 嵌入完成通知
            if client_id:
                await manager.send_json({
                    "type": "embedding",
                    "status": "completed",
                    "progress": 100,
                    "message": f"成功嵌入 {len(docs)} 个文档片段到表 '{table_name}'"
                }, client_id)
                
            # 将仓库信息写入数据库
            try:
                # 从 URL 提取仓库名称
                repo_name = repo.replace("-", " ").title()
                repo_path = f"/{org}/{repo}"
                repo_url = f"https://github.com/{org}/{repo}"
                
                # 添加到 repositories 表
                add_repository(repo_name, "", repo_path, repo_url)
                
                if client_id:
                    await manager.send_json({
                        "type": "database",
                        "status": "completed",
                        "message": f"已将仓库信息添加到数据库"
                    }, client_id)
            except Exception as e:
                logger.error(f"将仓库信息写入数据库时出错: {str(e)}")
                if client_id:
                    await manager.send_json({
                        "type": "database",
                        "status": "error",
                        "message": f"将仓库信息写入数据库时出错: {str(e)}"
                    }, client_id)
        except Exception as e:
            # 嵌入出错通知
            if client_id:
                await manager.send_json({
                    "type": "embedding",
                    "status": "error",
                    "progress": 0,
                    "message": f"嵌入文档时出错: {str(e)}"
                }, client_id)
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            return DownloadResponse(
                status="error",
                message=f"Error embedding documents: {str(e)}"
            )
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return DownloadResponse(
            status="success",
            message=f"Successfully downloaded and embedded {len(md_files)} markdown files",
            table_name=table_name
        )

    except ValueError as e:
        logger.error(f"ValueError in download_repository: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exception in download_repository: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Endpoint for downloading ZIP files removed - files are now saved directly to the project directory

class QueryRequest(BaseModel):
    """Request model for vector database query"""
    query: str
    table_name: str
    k: int = 5
    summarize: bool = False

class QueryResponse(BaseModel):
    """Response model for vector database query"""
    status: str
    message: str
    results: List[Dict[str, str]] = []
    summary: Optional[str] = None

@app.post("/query/", response_model=QueryResponse)
async def query_vector_database(query_request: QueryRequest):
    """
    Query the vector database for documents similar to the query.

    Args:
        query_request: Query request containing query string and table name

    Returns:
        JSON response with query results
    """
    try:
        # Search for documents with optional summarization
        results, summary = search_documents(
            query=query_request.query,
            k=query_request.k,
            table_name=query_request.table_name,
            summarize=query_request.summarize
        )

        # Format results
        formatted_results = []
        for i, doc in enumerate(results):
            formatted_results.append({
                "id": str(i + 1),
                "source": doc.metadata.get("source", "Unknown"),
                "content": doc.page_content
            })

        return QueryResponse(
            status="success",
            message=f"Found {len(results)} results for query: '{query_request.query}'",
            results=formatted_results,
            summary=summary
        )

    except Exception as e:
        return QueryResponse(
            status="error",
            message=f"Error querying vector database: {str(e)}"
        )

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 添加 WebSocket 端点，用于实时进度更新
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # 保持连接活跃，等待消息
            data = await websocket.receive_text()
            # 可以处理从客户端接收的消息，但这里我们主要是保持连接
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# 添加仓库API端点
@app.get("/repositories/")
async def get_repositories():
    """
    获取所有仓库信息
    
    Returns:
        JSON 响应，包含所有仓库信息
    """
    try:
        repositories = get_all_repositories()
        
        # 格式化日期时间为字符串
        for repo in repositories:
            if "created_at" in repo and repo["created_at"]:
                repo["created_at"] = repo["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            if "updated_at" in repo and repo["updated_at"]:
                # 计算相对时间（例如：1天前，2小时前）
                time_diff = time.time() - repo["updated_at"].timestamp()
                if time_diff < 3600:  # 小于1小时
                    repo["last_updated"] = f"{int(time_diff / 60)}分钟前"
                elif time_diff < 86400:  # 小于1天
                    repo["last_updated"] = f"{int(time_diff / 3600)}小时前"
                elif time_diff < 2592000:  # 小于30天
                    repo["last_updated"] = f"{int(time_diff / 86400)}天前"
                else:
                    repo["last_updated"] = repo["updated_at"].strftime("%Y-%m-%d")
                repo["updated_at"] = repo["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
        
        return {"status": "success", "repositories": repositories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仓库信息失败: {str(e)}")

@app.get("/repositories/{name}")
async def get_repository(name: str):
    """
    根据名称获取仓库信息
    
    Args:
        name: 仓库名称
        
    Returns:
        JSON 响应，包含仓库信息
    """
    try:
        repository = get_repository_by_name(name)
        if not repository:
            raise HTTPException(status_code=404, detail=f"仓库 {name} 不存在")
        
        # 格式化日期时间为字符串
        if "created_at" in repository and repository["created_at"]:
            repository["created_at"] = repository["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        if "updated_at" in repository and repository["updated_at"]:
            # 计算相对时间（例如：1天前，2小时前）
            time_diff = time.time() - repository["updated_at"].timestamp()
            if time_diff < 3600:  # 小于1小时
                repository["last_updated"] = f"{int(time_diff / 60)}分钟前"
            elif time_diff < 86400:  # 小于1天
                repository["last_updated"] = f"{int(time_diff / 3600)}小时前"
            elif time_diff < 2592000:  # 小于30天
                repository["last_updated"] = f"{int(time_diff / 86400)}天前"
            else:
                repository["last_updated"] = repository["updated_at"].strftime("%Y-%m-%d")
            repository["updated_at"] = repository["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
        
        return {"status": "success", "repository": repository}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仓库信息失败: {str(e)}")

if __name__ == "__main__":
    main()
