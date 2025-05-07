#!/usr/bin/env python3
"""
数据库操作模块，用于管理仓库信息
"""

import os
import pymysql
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DB_CONNECTION_ARGS = {
    "host": "127.0.0.1",
    "port": 2881,
    "user": "root@test",
    "password": "admin",
    "database": "doc2dev",
    "charset": "utf8mb4"
}

def get_db_connection():
    """
    获取数据库连接
    
    Returns:
        pymysql.Connection: 数据库连接对象
    """
    try:
        connection = pymysql.connect(**DB_CONNECTION_ARGS)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        raise

def get_all_repositories():
    """
    获取所有仓库信息
    
    Returns:
        List[Dict]: 仓库信息列表
    """
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT id, name, description, repo, repo_url, 
                   tokens, snippets, repo_status, created_at, updated_at
            FROM repositories
            ORDER BY name
            """
            
            # 执行原始查询
            cursor.execute(sql)
            repositories = cursor.fetchall()
            
            return repositories
    except Exception as e:
        print(f"获取仓库信息失败: {str(e)}")
        return []
    finally:
        if connection:
            connection.close()

def get_repository_by_name(name: str):
    """
    根据名称获取仓库信息
    
    Args:
        name: 仓库名称
        
    Returns:
        Dict: 仓库信息
    """
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT id, name, description, repo, repo_url, 
                   tokens, snippets, repo_status, created_at, updated_at
            FROM repositories
            WHERE name = %s
            """
            cursor.execute(sql, (name,))
            repository = cursor.fetchone()
            
            return repository
    except Exception as e:
        print(f"获取仓库信息失败: {str(e)}")
        return None
    finally:
        if connection:
            connection.close()

def get_repository_by_path(repo_path: str):
    """
    根据仓库路径获取仓库信息
    
    Args:
        repo_path: 仓库路径，格式为 /owner/repo
        
    Returns:
        Dict: 仓库信息，如果不存在返回 None
    """
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT id, name, description, repo, repo_url, 
                   tokens, snippets, repo_status, created_at, updated_at
            FROM repositories
            WHERE repo = %s
            """
            cursor.execute(sql, (repo_path,))
            repository = cursor.fetchone()
            
            return repository
    except Exception as e:
        print(f"根据路径获取仓库信息失败: {str(e)}")
        return None
    finally:
        if connection:
            connection.close()

def add_repository(name: str, description: str, repo: str, repo_url: str, repo_status: str, tokens: int = 0, snippets: int = 0):
    """
    添加仓库信息
    
    Args:
        name: 仓库名称
        description: 仓库描述
        repo: 仓库路径
        repo_url: 仓库URL
        repo_status: 仓库状态，可选值为 'in_progress', 'completed', 'failed', 'pending'
        tokens: 文档中的 token 数量，默认为 0
        snippets: 文档中的代码块数量，默认为 0
        
    Returns:
        bool: 是否添加成功
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO repositories (name, description, repo, repo_url, repo_status, tokens, snippets)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, description, repo, repo_url, repo_status, tokens, snippets))
            connection.commit()
            return True
    except Exception as e:
        print(f"添加仓库信息失败: {str(e)}")
        return False
    finally:
        if connection:
            connection.close()

def update_repository(id: int, name: str, description: str, repo: str, repo_url: str):
    """
    更新仓库信息
    
    Args:
        id: 仓库ID
        name: 仓库名称
        description: 仓库描述
        repo: 仓库路径
        repo_url: 仓库URL
        
    Returns:
        bool: 是否更新成功
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            UPDATE repositories
            SET name = %s, description = %s, repo = %s, repo_url = %s
            WHERE id = %s
            """
            cursor.execute(sql, (name, description, repo, repo_url, id))
            connection.commit()
            return True
    except Exception as e:
        print(f"更新仓库信息失败: {str(e)}")
        return False
    finally:
        if connection:
            connection.close()

def delete_repository(id: int):
    """
    删除仓库信息
    
    Args:
        id: 仓库ID
        
    Returns:
        bool: 是否删除成功
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            DELETE FROM repositories
            WHERE id = %s
            """
            cursor.execute(sql, (id,))
            connection.commit()
            return True
    except Exception as e:
        print(f"删除仓库信息失败: {str(e)}")
        return False
    finally:
        if connection:
            connection.close()

def delete_vector_table(table_name: str):
    """
    删除向量表
    
    Args:
        table_name: 要删除的向量表名称
        
    Returns:
        bool: 是否删除成功
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 安全地格式化表名
            safe_table_name = table_name.replace('-', '_')
            sql = f"DROP TABLE IF EXISTS {safe_table_name}"
            cursor.execute(sql)
            connection.commit()
            return True
    except Exception as e:
        print(f"删除向量表失败: {str(e)}")
        return False
    finally:
        if connection:
            connection.close()

def get_repository_by_id(id: int):
    """
    根据 ID 获取仓库信息
    
    Args:
        id: 仓库ID
        
    Returns:
        Dict: 仓库信息，如果不存在返回 None
    """
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT id, name, description, repo, repo_url, 
                   tokens, snippets, repo_status, created_at, updated_at
            FROM repositories
            WHERE id = %s
            """
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(f"获取仓库信息失败: {str(e)}")
        return None
    finally:
        if connection:
            connection.close()


def update_repository_status(id: int, repo_status: str):
    """
    更新仓库状态
    
    Args:
        id: 仓库ID
        repo_status: 仓库状态，可选值为 'in_progress', 'completed', 'failed', 'pending'
        
    Returns:
        bool: 是否更新成功
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            UPDATE repositories
            SET repo_status = %s
            WHERE id = %s
            """
            cursor.execute(sql, (repo_status, id))
            connection.commit()
            return True
    except Exception as e:
        print(f"更新仓库状态失败: {str(e)}")
        return False
    finally:
        if connection:
            connection.close()
