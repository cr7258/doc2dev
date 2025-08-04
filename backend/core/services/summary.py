"""
Summary Service

This service handles document summarization using OpenAI API via LangChain.
"""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models.base import BaseLanguageModel

from config.settings import Settings
from core.factories.llm import LLMFactory


class SummaryService:
    """
    Service for summarizing search results using OpenAI API.
    
    This service provides functionality to summarize document search results
    using LangChain's ChatOpenAI integration.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize SummaryService with configuration.
        
        Args:
            settings: Application settings containing OpenAI configuration
        """
        self.settings = settings
        self._chat_model: Optional[BaseLanguageModel] = None
    
    def _initialize_chat_model(self):
        """Initialize LLM model if not already initialized"""
        if self._chat_model is None:
            print(f"Initializing {self.settings.llm.config.type} LLM model...")
            
            try:
                self._chat_model = LLMFactory.create_llm(self.settings.llm)
                print(f"✅ {self.settings.llm.config.type} LLM model initialized successfully")
            except Exception as e:
                error_msg = f"Failed to initialize LLM model: {e}"
                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg) from e
    
    def summarize_search_results(self, documents: List[Document], query: str) -> str:
        """
        Summarize search results using OpenAI API.
        
        Args:
            documents: List of Document objects containing search results
            query: The original search query
            
        Returns:
            Summarized text
        """
        if not documents:
            return "No documents found to summarize."
        
        try:
            # Ensure chat model is initialized
            self._initialize_chat_model()
            
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
            
            # Create messages for the chat model
            messages = [
                SystemMessage(content="You are a helpful assistant that summarizes technical documentation."),
                HumanMessage(content=prompt)
            ]
            
            logger.info(f"Generating summary for query: '{query}'")
            
            # Generate the summary
            response = self._chat_model.invoke(messages)
            
            # Extract the summary from the response
            summary = response.content
            logger.info("✅ Summary generated successfully")
            
            return summary
        
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return error_msg
    

