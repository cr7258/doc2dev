#!/usr/bin/env python3
"""
Query routes for Doc2Dev API
"""

from fastapi import APIRouter, Depends
from core.models.api import QueryRequest, QueryResponse
from core.services.document import DocumentService
from core.database.router import DatabaseRouter
from api.auth import get_current_user_optional
from config.settings import Settings

router = APIRouter()


@router.post("/query/", response_model=QueryResponse)
async def query_vector_database(
    query_request: QueryRequest,
    current_user_id: str = Depends(get_current_user_optional)
):
    """
    Query the vector database for documents similar to the query.

    Args:
        query_request: Query request containing query string and table name

    Returns:
        JSON response with query results
    """
    try:
        # Initialize DocumentService with settings and db_router
        settings = Settings()
        db_router = DatabaseRouter(settings)
        document_service = DocumentService(settings, db_router)
        
        # Create filter for table name (if provided)
        filter_dict = {}
        # if query_request.table_name:
        #     filter_dict = {"table_name": query_request.table_name}
        
        if query_request.summarize:
            # Use search_with_summary for summarized results
            result = document_service.search_with_summary(
                query=query_request.query,
                table_name=query_request.table_name,
                k=query_request.k,
                filter=filter_dict,
                user_id=current_user_id
            )
            
            # Format results from search_with_summary
            formatted_results = []
            for i, doc_data in enumerate(result.get("documents", [])):
                formatted_results.append({
                    "id": str(i + 1),
                    "source": doc_data.get("metadata", {}).get("source", "Unknown"),
                    "content": doc_data.get("content", "")
                })
            
            return QueryResponse(
                status="success",
                message=f"Found {result.get('document_count', 0)} results for query: '{query_request.query}'",
                results=formatted_results,
                summary=result.get("summary", "")
            )
        else:
            # Use regular search_documents for non-summarized results
            results = document_service.search_documents(
                query=query_request.query,
                table_name=query_request.table_name,
                k=query_request.k,
                filter=filter_dict,
                user_id=current_user_id
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
                summary=None
            )

    except Exception as e:
        return QueryResponse(
            status="error",
            message=f"Error querying vector database: {str(e)}"
        )
