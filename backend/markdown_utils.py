#!/usr/bin/env python3
"""
Markdown 处理工具模块
"""

from markdown_it import MarkdownIt
from typing import List
from langchain_core.documents import Document

def count_code_blocks(markdown_text: str) -> int:
    """
    统计 Markdown 文本中的代码块数量
    
    Args:
        markdown_text: Markdown 文本内容
        
    Returns:
        int: 代码块数量
    """
    md = MarkdownIt()
    tokens = md.parse(markdown_text)

    code_block_count = 0

    for token in tokens:
        if token.type == 'fence':  # ``` fenced code block
            code_block_count += 1

    return code_block_count

def count_code_blocks_in_documents(documents: List[Document]) -> int:
    """
    统计文档列表中的代码块总数
    
    Args:
        documents: Document 对象列表
        
    Returns:
        int: 所有文档中的代码块总数
    """
    total_code_blocks = 0
    
    for doc in documents:
        total_code_blocks += count_code_blocks(doc.page_content)
    
    return total_code_blocks
