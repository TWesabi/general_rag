# Architecture Documentation

## Overview

The RAG System is built with a modular, scalable architecture that separates concerns and allows for easy extension and customization.

## Core Components

### 1. Document Parsing (`parsers/`)

- **DoclingParser**: Wraps Docling library for PDF parsing
- Extracts text content and metadata
- Returns standardized `Document` objects
- Extensible for other formats (DOCX, TXT, MD)

### 2. Text Chunking (`chunking/`)

- **Chunker**: Implements multiple chunking strategies
- Configurable chunk size and overlap
- Preserves metadata per chunk
- Strategies: Recursive, Fixed

### 3. Embedding Generation (`embeddings/`)

- **Embedder**: Uses sentence-transformers for local embeddings
- Default model: `all-MiniLM-L6-v2`
- Batch processing support
- Extensible for OpenAI embeddings

### 4. Vector Storage (`storage/`)

- **WeaviateClient**: Wraps Weaviate Python client
- Schema management for documents and chunks
- CRUD operations
- Vector similarity search

### 5. Retrieval System (`retrieval/`)

- **Retriever**: Implements vector-based retrieval
- Configurable top-k and score threshold
- Returns ranked chunks with metadata
- Future: Hybrid search support

### 6. LLM Generation (`generation/`)

- **Generator**: Supports multiple LLM providers
- Ollama (local) and Azure OpenAI support
- RAG prompt templates
- Streaming response support

### 7. API Layer (`api/`)

- **FastAPI**: RESTful API with async support
- Modular route structure
- Dependency injection for components
- OpenAPI documentation

### 8. ML Pipelines (`pipelines/`)

- **ZenML**: Pipeline orchestration
- Ingestion pipeline: Parse → Chunk → Embed → Store
- Indexing pipeline: Batch processing
- Artifact tracking

### 9. Experiment Tracking (`pipelines/mlflow_integration.py`)

- **MLflowTracker**: MLflow integration
- Experiment tracking
- Prompt registry
- Metrics logging

## Data Flow

### Document Ingestion Flow

```
PDF File
  ↓
DoclingParser (parse)
  ↓
Document (with metadata)
  ↓
Chunker (chunk)
  ↓
List[DocumentChunk]
  ↓
Embedder (embed)
  ↓
List[Embeddings]
  ↓
WeaviateClient (store)
  ↓
Stored in Weaviate
```

### Query Flow

```
User Query
  ↓
Embedder (embed query)
  ↓
Query Vector
  ↓
WeaviateClient (vector search)
  ↓
Retrieved Chunks
  ↓
Generator (build context + generate)
  ↓
Answer
```

## Configuration Management

All configuration is managed through `pydantic-settings`:

- Environment-based configuration
- Type-safe settings
- Separate config classes per component
- Support for local and cloud deployments

## Extension Points

### Adding New Document Formats

1. Create new parser in `parsers/`
2. Implement `parse()` method returning `Document`
3. Register in parser factory (if needed)

### Adding New LLM Providers

1. Add provider enum to `LLMProvider`
2. Implement generation methods in `Generator`
3. Add configuration in `LLMConfig`

### Adding New Chunking Strategies

1. Add strategy enum to `ChunkingStrategy`
2. Implement chunking method in `Chunker`
3. Update `chunk_document()` method

## Scalability Considerations

- **Async Operations**: FastAPI endpoints use async/await
- **Batch Processing**: Embeddings and storage support batching
- **Modular Design**: Components can be scaled independently
- **Configuration**: All parameters are configurable
- **Plugin Architecture**: Easy to add new parsers/generators

## Future Enhancements

- Hybrid search (vector + keyword)
- Re-ranking models
- Multi-modal support
- Advanced chunking strategies
- Distributed processing
- Caching layer
