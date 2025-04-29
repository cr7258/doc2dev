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
                   created_at, updated_at
            FROM repositories
            ORDER BY name
            """
            cursor.execute(sql)
            repositories = cursor.fetchall()
            
            # 查询每个仓库的向量表信息
            for repo in repositories:
                repo_name = repo["name"].lower().replace("-", "_")
                try:
                    # 查询向量表中的文档数量
                    sql_count = f"""
                    SELECT COUNT(*) as count FROM {repo_name}_vectors
                    """
                    cursor.execute(sql_count)
                    result = cursor.fetchone()
                    if result:
                        repo["tokens"] = result["count"] * 1536  # 假设每个向量是1536维
                        repo["snippets"] = result["count"]
                    else:
                        repo["tokens"] = 0
                        repo["snippets"] = 0
                except Exception as e:
                    # 如果表不存在，设置为0
                    repo["tokens"] = 0
                    repo["snippets"] = 0
            
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
                   created_at, updated_at
            FROM repositories
            WHERE name = %s
            """
            cursor.execute(sql, (name,))
            repository = cursor.fetchone()
            
            if repository:
                # 查询向量表信息
                repo_name = repository["name"].lower().replace("-", "_")
                try:
                    # 查询向量表中的文档数量
                    sql_count = f"""
                    SELECT COUNT(*) as count FROM {repo_name}_vectors
                    """
                    cursor.execute(sql_count)
                    result = cursor.fetchone()
                    if result:
                        repository["tokens"] = result["count"] * 1536  # 假设每个向量是1536维
                        repository["snippets"] = result["count"]
                    else:
                        repository["tokens"] = 0
                        repository["snippets"] = 0
                except Exception as e:
                    # 如果表不存在，设置为0
                    repository["tokens"] = 0
                    repository["snippets"] = 0
            
            return repository
    except Exception as e:
        print(f"获取仓库信息失败: {str(e)}")
        return None
    finally:
        if connection:
            connection.close()

def add_repository(name: str, description: str, repo: str, repo_url: str):
    """
    添加仓库信息
    
    Args:
        name: 仓库名称
        description: 仓库描述
        repo: 仓库路径
        repo_url: 仓库URL
        
    Returns:
        bool: 是否添加成功
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO repositories (name, description, repo, repo_url)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (name, description, repo, repo_url))
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
