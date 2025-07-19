"""
Document Factories

This module contains factories for document loading and splitting operations.
"""

from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


class DocumentLoaderFactory:
    """Document loader factory - supports md, txt, pdf"""
    
    @staticmethod
    def get_loader(file_type: str):
        """Get appropriate LangChain DocumentLoader based on file type"""
        
        match file_type:
            case "markdown" | "md":
                return UnstructuredMarkdownLoader
                
            case "txt" | "text":
                return TextLoader
                
            case "pdf":
                return PyPDFLoader
                
            case _:
                raise ValueError(f"Unsupported file type: {file_type}. Supported types: md, txt, pdf")
    
    @staticmethod
    def get_supported_extensions() -> List[str]:
        """Return supported file extensions"""
        return ['.md', '.markdown', '.txt', '.text', '.pdf']


class DocumentSplitterFactory:
    """Document splitter factory - focused on markdown, default for others"""
    
    @staticmethod
    def get_splitter(file_type: str, **kwargs):
        """Get appropriate LangChain TextSplitter based on file type"""
        
        match file_type:
            case "markdown" | "md":
                return MarkdownHeaderTextSplitter(
                    headers_to_split_on=[
                        ("#", "Header 1"),
                        ("##", "Header 2"), 
                        ("###", "Header 3"),
                        ("####", "Header 4"),
                        ("#####", "Header 5"),
                        ("######", "Header 6"),
                    ],
                    strip_headers=False  # Keep consistent with existing code
                )
                
            case _:
                # All other file types use default recursive character splitter
                return RecursiveCharacterTextSplitter(
                    chunk_size=kwargs.get('chunk_size', 1000),
                    chunk_overlap=kwargs.get('chunk_overlap', 200)
                )
