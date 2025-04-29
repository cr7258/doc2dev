#!/usr/bin/env python3
"""
验证 GitHub token 是否有效的脚本
"""

from github import Github, Auth
import os
from dotenv import load_dotenv

def validate_github_token(token):
    """
    验证 GitHub token 是否有效
    
    Args:
        token (str): GitHub token
        
    Returns:
        bool: token 是否有效
    """
    try:
        # 创建 Auth 对象
        auth = Auth.Token(token)
        # 初始化 Github 客户端
        g = Github(auth=auth)
        # 获取用户信息
        user = g.get_user()
        print(f"✅ Token 有效! 已验证为用户: {user.login}")
        print(f"用户名: {user.name}")
        print(f"邮箱: {user.email}")
        
        # 获取速率限制信息
        rate_limit = g.get_rate_limit()
        print(f"API 速率限制: {rate_limit.core.remaining}/{rate_limit.core.limit} 请求可用")
        print(f"重置时间: {rate_limit.core.reset}")
        
        return True
    except Exception as e:
        print(f"❌ Token 验证失败: {str(e)}")
        return False
    finally:
        # 关闭连接
        if 'g' in locals():
            g.close()

if __name__ == "__main__":
    # 尝试从 .env 文件加载 token
    load_dotenv()
    env_token = os.getenv("GITHUB_TOKEN")
    
    if env_token:
        print("从 .env 文件中找到 GITHUB_TOKEN，正在验证...")
        validate_github_token(env_token)
    
    # 无论是否有环境变量 token，都允许用户输入 token 进行验证
    print("\n您也可以手动输入 token 进行验证:")
    token = input("请输入您的 GitHub token (直接回车跳过): ")
    
    if token:
        validate_github_token(token)
    elif not env_token:
        print("未提供 token，无法验证。")
