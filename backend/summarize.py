#!/usr/bin/env python3
"""
Module to summarize search results using OpenAI API via LangChain.
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Get API keys from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

def summarize_search_results(documents: List[Document], query: str) -> str:
    """
    Summarize search results using LangChain's ChatOpenAI.
    
    Args:
        documents: List of Document objects containing search results
        query: The original search query
        
    Returns:
        Summarized text
    """
    if not documents:
        return "No documents found to summarize."
    
    # Prepare the content for the API request
    content = f"Search Query: {query}\n\n"
    
    for i, doc in enumerate(documents):
        content += f"Document {i+1}:\n{doc.page_content}\n\n"
    
    # Prepare the prompt for summarization
    prompt = f"""
You are an expert at summarizing technical documentation. 
Analyze the following search results and provide a concise, well-structured summary.
Focus on extracting the most relevant information related to the search query.
Format your response as follows:

TITLE: [A clear, concise title that captures the main topic]
DESCRIPTION: [A brief description of the main content]

LANGUAGE: [Programming language if code is present]
CODE:
```
[Any relevant code snippets, properly formatted]
```

If there are multiple distinct topics, separate them with a line of dashes (----------------------------------------).
Keep your summary focused, technical, and informative.

{content}
"""

    # Initialize the ChatOpenAI model
    try:
        # Create a ChatOpenAI instance
        chat = ChatOpenAI(
            model="openai/gpt-4o",
            temperature=0.3,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_API_BASE,
            max_tokens=2000
        )
        
        # Create messages for the chat model
        messages = [
            SystemMessage(content="You are a helpful assistant that summarizes technical documentation."),
            HumanMessage(content=prompt)
        ]
        
        # Generate the summary
        response = chat.invoke(messages)
        
        # Extract the summary from the response
        summary = response.content
        return summary
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"

if __name__ == "__main__":
    # Test the summarization function
    import argparse
    
    parser = argparse.ArgumentParser(description="Summarize search results")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--documents", required=True, help="JSON file containing document data")
    
    args = parser.parse_args()
    
    # Load documents from JSON file
    with open(args.documents, "r") as f:
        doc_data = json.load(f)
    
    # Convert to Document objects
    documents = [
        Document(page_content=item["content"], metadata={"source": item["source"]})
        for item in doc_data
    ]
    
    # Generate summary
    summary = summarize_search_results(documents, args.query)
    
    # Print the summary
    print(summary)
