"""Query endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.api.dependencies import get_generator, get_retriever
from src.generation import Generator
from src.retrieval import Retriever
from src.schemas.query import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    retriever: Retriever = Depends(get_retriever),
    generator: Generator = Depends(get_generator),
):
    """
    Query the RAG system.

    Args:
        request: Query request
        retriever: Retriever instance
        generator: LLM generator instance

    Returns:
        Query response with retrieved chunks and answer
    """
    try:
        # Retrieve relevant chunks
        retrieved_chunks = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )

        # Build context from retrieved chunks
        context = "\n\n".join([chunk.content for chunk in retrieved_chunks])

        # Generate answer
        answer = await generator.generate(
            prompt=request.query,
            context=context if context else None,
        )

        return QueryResponse(
            query=request.query,
            retrieved_chunks=retrieved_chunks,
            answer=answer,
            metadata={
                "chunks_count": len(retrieved_chunks),
                "provider": generator.provider.value,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/stream")
async def query_stream(
    request: QueryRequest,
    retriever: Retriever = Depends(get_retriever),
    generator: Generator = Depends(get_generator),
):
    """
    Query the RAG system with streaming response.

    Args:
        request: Query request
        retriever: Retriever instance
        generator: LLM generator instance

    Returns:
        Streaming response
    """
    try:
        # Retrieve relevant chunks
        retrieved_chunks = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )

        # Build context from retrieved chunks
        context = "\n\n".join([chunk.content for chunk in retrieved_chunks])

        # Generate streaming answer
        async def generate():
            async for chunk in generator.generate_stream(
                prompt=request.query,
                context=context if context else None,
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/self_query")
async def self_query(query: str) -> list[str]:
    """
    Self-query endpoint for extracting metadata from query with an LLM judge.

    Args:
        query: Input query string
    """
    pass


@router.post("/query_exapnsion")
async def query_expansion(query: str, num_queries: int = 3) -> list[str]:
    """
    Query expansion endpoint for generating related queries.

    Args:
        query: Input query string
        num_queries: Number of related queries to generate
    """
    pass
