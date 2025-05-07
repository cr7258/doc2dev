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
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from github import Github, Auth, GithubException

# 导入自定义模块
from embed_and_store import load_markdown_files, split_documents, embed_and_store
from query_oceanbase import search_documents, connect_to_vector_store
from repository_db import (
    get_all_repositories, get_repository_by_name, get_repository_by_path,
    add_repository, update_repository, delete_repository, get_repository_by_id,
    update_repository_status, update_repository_counts, delete_vector_table
)
from markdown_utils import count_code_blocks_in_documents

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def embed_and_store_with_progress(documents, table_name, drop_old=False, progress_callback=None):
    """
    嵌入文档并存储到向量数据库，支持进度回调
    
    Args:
        documents: 要嵌入的文档列表
        table_name: 向量表名称
        drop_old: 是否删除旧表
        progress_callback: 进度回调函数
        
    Returns:
        OceanbaseVectorStore: 向量存储对象
    """
    import asyncio
    total_docs = len(documents)
    
    # 调用原始的 embed_and_store 函数，但在过程中添加进度更新
    try:
        # 初始化进度
        if progress_callback:
            await progress_callback(0, total_docs, "开始嵌入文档...")
        
        # 使用 asyncio.to_thread 将同步函数转换为异步操作
        # 这样可以避免阻塞事件循环
        vector_store = await asyncio.to_thread(
            embed_and_store, 
            documents, 
            table_name=table_name, 
            drop_old=drop_old
        )
        
        # 完成进度
        if progress_callback:
            await progress_callback(total_docs, total_docs, "文档嵌入完成")
            
        return vector_store
    except Exception as e:
        if progress_callback:
            await progress_callback(0, 1, f"嵌入文档时出错: {str(e)}")
        raise e

# Load environment variables from .env file
# 强制重新加载 .env 文件，忽略缓存
load_dotenv(override=True)

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
        try:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_json(data)
            else:
                print(f"Warning: Client {client_id} not found in active connections")
        except Exception as e:
            print(f"Error sending message to client {client_id}: {str(e)}")
            # 如果发送失败，尝试移除连接
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                print(f"Removed client {client_id} due to send error. Total connections: {len(self.active_connections)}")
            return False
        return True

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
    table_name: Optional[str] = None  # 表名，用于跳转到查询页面
    query_url: Optional[str] = None  # 查询页面的 URL，用于前端生成链接
    repo_path: Optional[str] = None  # 仓库路径，用于前端显示

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

def get_repo_contents_using_trees(repo):
    """
    使用Git Trees API获取仓库所有内容，比递归方式更高效。

    Args:
        repo: GitHub repository object

    Returns:
        list: 包含文件信息的列表，每个元素有path和sha属性
    """
    try:
        # 获取默认分支
        default_branch = repo.default_branch
        logger.info(f"Using default branch: {default_branch}")
        
        # 获取树结构，recursive=True获取所有子目录
        tree = repo.get_git_tree(default_branch, recursive=True)
        logger.info(f"Got repository tree with {len(tree.tree)} items")
        
        # 返回所有文件
        return tree.tree
    except Exception as e:
        logger.error(f"Error getting repository tree: {e}")
        return []

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
            # 使用 asyncio.to_thread 将同步的 GitHub API 调用转换为异步操作
            import asyncio
            g = Github(token)
            # 检查 API 速率限制
            rate_limit = await asyncio.to_thread(g.get_rate_limit)
            logger.info(f"GitHub API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit} requests remaining")
        except Exception as e:
            logger.error(f"Error initializing GitHub API: {str(e)}")
            if progress_callback:
                await progress_callback(0, 1, f"初始化 GitHub API 时出错: {str(e)}")
            return []

        # 获取仓库
        try:
            logger.info(f"Getting repository: {repo_name}")
            repo = await asyncio.to_thread(g.get_repo, repo_name)
            logger.info(f"Successfully got repository: {repo.full_name}")
        except Exception as e:
            logger.error(f"Error getting repository {repo_name}: {str(e)}")
            if progress_callback:
                await progress_callback(0, 1, f"获取仓库时出错: {str(e)}")
            return []

        # 发送进度更新：开始获取仓库内容
        if progress_callback:
            await progress_callback(0, 1, "正在获取仓库内容...")

        # 使用树结构API获取所有内容
        try:
            logger.info("Getting repository contents using tree API...")
            # 使用 asyncio.to_thread 将同步函数转换为异步操作
            all_contents = await asyncio.to_thread(get_repo_contents_using_trees, repo)
            logger.info(f"Found {len(all_contents)} total items in repository")
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
                
                # 使用blob获取内容，更高效
                try:
                    # 使用 asyncio.to_thread 将同步的 GitHub API 调用转换为异步操作
                    blob = await asyncio.to_thread(repo.get_git_blob, content.sha)
                    # 根据编码方式解码内容
                    if blob.encoding == 'base64':
                        import base64
                        file_content = base64.b64decode(blob.content)
                    else:
                        file_content = blob.content.encode('utf-8')
                except Exception as blob_error:
                    logger.warning(f"Error getting blob for {content.path}: {blob_error}, falling back to get_contents")
                    # 如果获取blob失败，回退到使用get_contents
                    contents = await asyncio.to_thread(repo.get_contents, content.path)
                    file_content = contents.decoded_content

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

# 后台处理仓库的函数
async def process_repository_background(repo_url: str, library_name: Optional[str] = None, client_id: Optional[str] = None):
    """
    在后台处理仓库下载和索引任务
    
    Args:
        repo_url: 仓库 URL
        library_name: 可选的库名称
        client_id: 可选的客户端 ID，用于 WebSocket 更新
    """
    try:
        # 从 URL 提取组织和仓库名称
        org, repo = extract_org_repo(str(repo_url))
        
        # 检查仓库是否已经存在
        repo_path = f"{org}/{repo}"
        existing_repo = get_repository_by_path(repo_path)
        
        # 如果仓库已存在，直接返回
        if existing_repo:
            return
            
        # 如果没有提供 library_name，则自动生成
        table_name = library_name
        if not table_name:
            table_name = f"{org}_{repo}"
        
        # 确保表名中的连字符替换为下划线
        table_name = table_name.replace("-", "_")
        
        # 将仓库状态设置为 in_progress
        repo_id = None
        try:
            # 首先将仓库添加到数据库，状态为 in_progress
            repo_name = repo.replace("-", " ").title()
            repo_url_full = f"https://github.com/{org}/{repo}"
            
            # 添加到 repositories 表
            add_repository(repo_name, "", repo_path, repo_url_full, "in_progress", 0, 0)
            
            # 获取新添加的仓库 ID
            added_repo = get_repository_by_path(repo_path)
            if added_repo:
                repo_id = added_repo['id']
                logger.info(f"Added repository with ID: {repo_id}")
        except Exception as e:
            logger.error(f"Error adding repository to database: {str(e)}")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {temp_dir}")
        
        # 发送初始进度信息
        websocket_connected = True
        if client_id:
            websocket_connected = await manager.send_json({
                "type": "download",
                "status": "started",
                "progress": 0,
                "message": f"开始下载 {org}/{repo} 仓库..."
            }, client_id)
            
            # 如果 WebSocket 连接失败，记录日志但继续处理
            if not websocket_connected:
                logger.warning(f"WebSocket connection to client {client_id} failed, but continuing with repository processing")
                # 将 client_id 设置为 None，避免后续尝试发送消息
                client_id = None

        # 定义下载进度回调函数
        async def download_progress_callback(current, total, message):
            nonlocal client_id, websocket_connected
            if client_id and websocket_connected:
                progress = int((current / total) * 100) if total > 0 else 0
                websocket_connected = await manager.send_json({
                    "type": "download",
                    "status": "in_progress",
                    "progress": progress,
                    "current": current,
                    "total": total,
                    "message": message
                }, client_id)
                
                # 如果 WebSocket 连接失败，记录日志并停止尝试发送
                if not websocket_connected:
                    logger.warning(f"WebSocket connection to client {client_id} failed during download progress update")
                    client_id = None  # 避免后续尝试发送

        # 下载 Markdown 文件，使用带进度的版本
        md_files = await download_md_files_with_progress(
            repo_url, 
            temp_dir, 
            progress_callback=download_progress_callback if client_id else None
        )
        
        if not md_files:
            if client_id and websocket_connected:
                websocket_connected = await manager.send_json({
                    "type": "download",
                    "status": "error",
                    "progress": 0,
                    "message": "仓库中未找到 Markdown 文件"
                }, client_id)
                
                if not websocket_connected:
                    logger.warning(f"WebSocket connection to client {client_id} failed when sending error message")
                    client_id = None
            
            # 如果有仓库 ID，将状态更新为 failed
            if repo_id:
                try:
                    update_repository_status(repo_id, "failed")
                    logger.info(f"Updated repository status to 'failed' for ID: {repo_id}")
                except Exception as e:
                    logger.error(f"Error updating repository status: {str(e)}")
            
            shutil.rmtree(temp_dir)
            return

        # 下载完成通知
        if client_id and websocket_connected:
            websocket_connected = await manager.send_json({
                "type": "download",
                "status": "completed",
                "progress": 100,
                "message": f"已下载 {len(md_files)} 个 Markdown 文件"
            }, client_id)
            
            if not websocket_connected:
                logger.warning(f"WebSocket connection to client {client_id} failed when sending download completion message")
                client_id = None
        
        # 加载 Markdown 文件
        documents = load_markdown_files(md_files)
        
        # 分割文档
        docs = split_documents(documents)

        # 嵌入并存储文档，使用带进度的版本
        if client_id and websocket_connected:
            websocket_connected = await manager.send_json({
                "type": "embedding",
                "status": "started",
                "progress": 0,
                "message": "开始嵌入文档..."
            }, client_id)
            
            if not websocket_connected:
                logger.warning(f"WebSocket connection to client {client_id} failed when sending embedding start message")
                client_id = None
        
        # 定义嵌入进度回调函数
        async def embedding_progress_callback(current, total, message):
            nonlocal client_id, websocket_connected
            if client_id and websocket_connected:
                websocket_connected = await manager.send_json({
                    "type": "embedding",
                    "status": "in_progress",
                    "progress": int((current / total) * 100) if total > 0 else 0,
                    "current": current,
                    "total": total,
                    "message": message
                }, client_id)
                
                if not websocket_connected:
                    logger.warning(f"WebSocket connection to client {client_id} failed during embedding progress update")
                    client_id = None  # 避免后续尝试发送
                    
        try:
            # 嵌入并存储文档
            vector_store = await embed_and_store_with_progress(
                docs, 
                table_name=table_name, 
                drop_old=True,
                progress_callback=embedding_progress_callback
            )
            
            # 完成通知
            if client_id and websocket_connected:
                try:
                    websocket_connected = await manager.send_json({
                        "type": "embedding",
                        "status": "completed",
                        "progress": 100,
                        "message": f"成功嵌入 {len(docs)} 个文档到表 {table_name}"
                    }, client_id)
                except Exception as e:
                    logger.error(f"Error sending embedding completion message: {str(e)}")
                    websocket_connected = False
                    client_id = None
            
            # 如果有仓库 ID，将状态更新为 completed
            if repo_id:
                try:
                    # 计算文档中的 token 数量和代码块数量
                    tokens_count = sum(len(doc.page_content.split()) for doc in documents)
                    snippets_count = count_code_blocks_in_documents(documents)
                    
                    # 更新仓库状态
                    update_repository_status(repo_id, "completed")
                    logger.info(f"Updated repository status to 'completed' for ID: {repo_id}")
                    
                    # 更新仓库的 tokens 和代码片段数量
                    update_repository_counts(repo_id, tokens_count, snippets_count)
                    logger.info(f"Updated repository counts for ID: {repo_id} - Tokens: {tokens_count}, Snippets: {snippets_count}")
                except Exception as e:
                    logger.error(f"Error updating repository status or counts: {str(e)}")
            
            # 将仓库信息写入数据库
            try:
                # 从 URL 提取仓库名称
                repo_name = repo.replace("-", " ").title()
                repo_url_full = f"https://github.com/{org}/{repo}"
                
                # 计算文档中的 token 数量和代码块数量
                tokens_count = sum(len(doc.page_content.split()) for doc in documents)
                snippets_count = count_code_blocks_in_documents(documents)
                
                # 添加到 repositories 表
                add_repository(repo_name, "", repo_path, repo_url_full, "completed", tokens_count, snippets_count)
                
                if client_id and websocket_connected:
                    try:
                        await manager.send_json({
                            "type": "database",
                            "status": "completed",
                            "message": f"已将仓库信息添加到数据库"
                        }, client_id)
                    except Exception as e:
                        logger.error(f"Error sending database completion message: {str(e)}")
                        websocket_connected = False
                        client_id = None
            except Exception as e:
                logger.error(f"将仓库信息写入数据库时出错: {str(e)}")
                if client_id and websocket_connected:
                    try:
                        await manager.send_json({
                            "type": "database",
                            "status": "error",
                            "message": f"将仓库信息写入数据库时出错: {str(e)}"
                        }, client_id)
                    except Exception as ws_err:
                        logger.error(f"Error sending database error message: {str(ws_err)}")
                        websocket_connected = False
                        client_id = None
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            
            # 发送错误通知
            if client_id and websocket_connected:
                try:
                    await manager.send_json({
                        "type": "embedding",
                        "status": "error",
                        "progress": 0,
                        "message": f"嵌入文档时出错: {str(e)}"
                    }, client_id)
                except Exception as ws_err:
                    logger.error(f"Error sending embedding error message: {str(ws_err)}")
                
            # 如果有仓库 ID，将状态更新为 failed
            if repo_id:
                try:
                    update_repository_status(repo_id, "failed")
                    logger.info(f"Updated repository status to 'failed' for ID: {repo_id}")
                except Exception as status_err:
                    logger.error(f"Error updating repository status: {str(status_err)}")
        
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {str(e)}")
            
    except Exception as e:
        logger.error(f"Background task error: {str(e)}")
        if client_id:
            await manager.send_json({
                "type": "error",
                "message": f"处理仓库时出错: {str(e)}"
            }, client_id)

@app.post("/download/", response_model=DownloadResponse)
async def download_repository(repo_request: RepositoryRequest, background_tasks: BackgroundTasks):
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
        
        # 检查仓库是否已经存在
        repo_path = f"{org}/{repo}"
        existing_repo = get_repository_by_path(repo_path)
        
        # 如果没有提供 library_name，则自动生成
        table_name = repo_request.library_name
        if not table_name:
            table_name = f"{org}_{repo}"
        
        # 确保表名中的连字符替换为下划线
        table_name = table_name.replace("-", "_")
        
        # 如果仓库已存在，返回提示信息
        if existing_repo:
            repo_name = existing_repo['name']
            repo_path = existing_repo['repo']
            
            # 生成查询页面的 URL，包含表名、仓库名称和仓库路径
            
            # 使用实际的表名，而不是当前生成的 table_name
            # 表名应该是仓库路径中的斜杠替换为下划线，连字符替换为下划线
            actual_table_name = repo_path.replace('/', '_').replace('-', '_')
            
            # 生成查询页面 URL
            query_url = f"http://localhost:3000/query?table={actual_table_name}&repo_name={repo_name}&repo_path={repo_path}"
            
            return DownloadResponse(
                status="exists",
                message=f"This repository has already been submitted. Check {repo_path} to see it.",
                table_name=actual_table_name,
                query_url=query_url,
                repo_path=repo_path
            )
        
        # 在后台任务中处理仓库下载和索引
        background_tasks.add_task(
            process_repository_background,
            str(repo_request.repo_url),
            repo_request.library_name,
            repo_request.client_id
        )
        
        # 生成查询页面 URL
        query_url = f"http://localhost:3000/query?table={table_name}&repo_name={repo.replace('-', ' ').title()}&repo_path={repo_path}"
        
        # 返回响应，表示任务已在后台启动
        return DownloadResponse(
            status="accepted",
            message=f"Repository processing started in background. You can continue using the application while the repository is being processed.",
            table_name=table_name,
            query_url=query_url,
            repo_path=repo_path
        )

    except ValueError as e:
        logger.error(f"ValueError in download_repository: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exception in download_repository: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
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
        
        # 将时间转换为 ISO 格式，保留时区信息
        for repo in repositories:
            if "created_at" in repo and repo["created_at"]:
                # 转换为 ISO 格式字符串
                repo["created_at"] = repo["created_at"].isoformat()
            if "updated_at" in repo and repo["updated_at"]:
                # 转换为 ISO 格式字符串
                repo["updated_at"] = repo["updated_at"].isoformat()
        
        return {"status": "success", "repositories": repositories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仓库信息失败: {str(e)}")

# 获取特定仓库的详细信息
@app.get("/repositories/{repo_path}")
async def get_repository_details(repo_path: str):
    """
    获取特定仓库的详细信息
    
    Args:
        repo_path: 仓库路径，格式为 owner/repo
        
    Returns:
        JSON 响应，包含仓库详细信息
    """
    try:
        # 将路径中的下划线替换为斜杠
        repo_path = repo_path.replace("_", "/")
        
        # 获取仓库信息
        repository = get_repository_by_path(repo_path)
        
        if not repository:
            raise HTTPException(status_code=404, detail=f"未找到仓库: {repo_path}")
        
        # 将时间转换为 ISO 格式，保留时区信息
        if "created_at" in repository and repository["created_at"]:
            # 转换为 ISO 格式字符串
            repository["created_at"] = repository["created_at"].isoformat()
        
        if "updated_at" in repository and repository["updated_at"]:
            # 转换为 ISO 格式字符串
            repository["updated_at"] = repository["updated_at"].isoformat()
        
        return {"status": "success", "repository": repository}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仓库详细信息失败: {str(e)}")

# 删除仓库的 API 端点
@app.delete("/repositories/{repo_id}")
async def delete_repository_endpoint(repo_id: int):
    """
    删除仓库
    
    Args:
        repo_id: 仓库ID
        
    Returns:
        JSON response with delete status
    """
    try:
        # 使用 repository_db.py 中的函数获取仓库信息
        repository = get_repository_by_id(repo_id)
        
        if not repository:
            raise HTTPException(status_code=404, detail=f"仓库不存在: ID {repo_id}")
        
        # 获取仓库路径，用于生成表名
        repo_path = repository['repo']
        # 确保路径没有前导斜杠
        if repo_path.startswith('/'):
            repo_path = repo_path[1:]
        
        # 生成表名
        table_name = repo_path.replace('/', '_').replace('-', '_')
        
        # 删除向量表
        try:
            # 使用 repository_db.py 中的函数删除向量表
            vector_table_deleted = delete_vector_table(table_name)
            if vector_table_deleted:
                logger.info(f"已删除向量表: {table_name}")
            else:
                logger.warning(f"删除向量表失败: {table_name}")
        except Exception as e:
            logger.error(f"删除向量表失败: {str(e)}")
            # 即使删除向量表失败，我们仍然尝试删除数据库记录
        
        # 删除数据库记录
        success = delete_repository(repo_id)
        
        if success:
            return {
                "status": "success",
                "message": f"已成功删除仓库: {repository['name']}"
            }
        else:
            raise HTTPException(status_code=500, detail="删除仓库记录失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除仓库失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除仓库失败: {str(e)}")

if __name__ == "__main__":
    main()
