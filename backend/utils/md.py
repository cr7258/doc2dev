#!/usr/bin/env python3
"""
Markdown processing utilities module
"""

from markdown_it import MarkdownIt
from typing import List
from langchain_core.documents import Document

def count_code_blocks(markdown_text: str) -> int:
    """
    Count the number of code blocks in Markdown text
    
    Args:
        markdown_text: Markdown text content
        
    Returns:
        int: Number of code blocks
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
    Count total code blocks in a list of documents
    
    Args:
        documents: List of Document objects
        
    Returns:
        int: Total number of code blocks in all documents
    """
    total_code_blocks = 0
    
    for doc in documents:
        total_code_blocks += count_code_blocks(doc.page_content)
    
    return total_code_blocks
