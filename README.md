# RAG System

A general-purpose Retrieval-Augmented Generation (RAG) system built with modern ML tools. This system provides a scalable, modular architecture for document processing, vector storage, and intelligent querying.

## Features

- **Document Parsing**: Docling-based parser for PDF documents (extensible to other formats)
- **Vector Storage**: Weaviate integration for efficient similarity search
- **Embeddings**: Local embedding generation using sentence-transformers
- **LLM Integration**: Support for Ollama (local) and Azure OpenAI
- **API**: FastAPI-based REST API for easy integration
- **ML Pipelines**: ZenML pipelines for data processing and indexing
- **Experiment Tracking**: MLflow integration for tracking and prompt registry
- **Scalable Architecture**: Modular design for easy extension

## Architecture

```
┌─────────────┐
│   Open WebUI│
│  (Frontend) │
└──────┬──────┘
       │
┌──────▼─────────────────────────────────────┐
│         FastAPI Endpoints                   │
│  - Document Upload                         │
│  - Query                                   │
│  - Health                                  │
└──────┬──────────────────────────────────────┘
       │
┌──────▼─────────────────────────────────────┐
│         Core RAG Pipeline                  │
│  Parse → Chunk → Embed → Store → Retrieve │
└──────┬──────────────────────────────────────┘
       │
┌──────▼─────────────────────────────────────┐
│         Storage & ML Tools                 │
│  - Weaviate (Vector DB)                    │
│  - ZenML (Pipelines)                       │
│  - MLflow (Tracking)                       │
└────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.10+
- Docker (for Weaviate)
- [uv](https://github.com/astral-sh/uv) package manager
- Ollama (for local LLM) or Azure OpenAI credentials

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

3. **Create virtual environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start Weaviate** (using Docker):
   ```bash
   python scripts/setup_weaviate.py
   ```
   Or manually:
   ```bash
   docker run -d --name weaviate -p 8080:8080 -p 50051:50051 \
     -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
     semitechnologies/weaviate:latest
   ```

6. **Start MLflow** (optional, for experiment tracking):
   ```bash
   mlflow ui --host 0.0.0.0 --port 5000
   ```

## Quick Start

### 1. Start the API Server

```bash
uvicorn rag_system.api.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### 2. Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

### 3. Query the System

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the document?",
    "top_k": 5
  }'
```

## Configuration

All configuration is done through environment variables. See `.env.example` for available options:

- **Weaviate**: `WEAVIATE_URL`, `WEAVIATE_API_KEY`
- **Embeddings**: `EMBEDDING_MODEL_NAME`, `EMBEDDING_DEVICE`
- **LLM**: `LLM_PROVIDER` (ollama/azure_openai), `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- **Azure OpenAI**: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, etc.
- **Chunking**: `CHUNK_SIZE`, `CHUNK_OVERLAP`
- **Retrieval**: `RETRIEVAL_TOP_K`, `RETRIEVAL_SCORE_THRESHOLD`

## Project Structure

```
rag_system/
├── src/rag_system/
│   ├── api/              # FastAPI application
│   ├── chunking/         # Text chunking strategies
│   ├── embeddings/       # Embedding generation
│   ├── generation/       # LLM generation
│   ├── models/           # Data models
│   ├── parsers/          # Document parsers
│   ├── pipelines/        # ZenML pipelines
│   ├── retrieval/        # Retrieval system
│   └── storage/          # Weaviate integration
├── tests/                # Test suite
├── scripts/               # Utility scripts
├── examples/             # Usage examples
└── docs/                 # Documentation
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /health/ready` - Readiness check
- `POST /documents/upload` - Upload and process document
- `GET /documents` - List all documents
- `GET /documents/{doc_id}` - Get document by ID
- `DELETE /documents/{doc_id}` - Delete document
- `POST /query` - Query the RAG system
- `POST /query/stream` - Stream query response

## Usage Examples

See `examples/basic_usage.py` for a complete example.

### Using ZenML Pipelines

```python
from rag_system.pipelines import ingestion_pipeline

# Process a single document
doc_id = ingestion_pipeline(file_path="document.pdf")
```

### Using MLflow Tracking

```python
from rag_system.pipelines.mlflow_integration import MLflowTracker

tracker = MLflowTracker()
with tracker.start_run():
    tracker.log_retrieval_metrics(query, chunks, latency)
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
ruff check src/ tests/
```

## Deployment

For production deployment:

1. Configure environment variables appropriately
2. Set up proper authentication for Weaviate
3. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
4. Set up reverse proxy (nginx, Traefik, etc.)
5. Configure monitoring and logging

## Roadmap

- [ ] Support for additional document formats (DOCX, TXT, MD)
- [ ] Hybrid search (vector + keyword)
- [ ] Re-ranking support
- [ ] Multi-modal document support
- [ ] Advanced chunking strategies
- [ ] Cloud deployment guides

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]

## Support

For issues and questions, please open an issue on the repository.
