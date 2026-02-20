# Setup Guide

## Prerequisites

### Required

- **Python 3.10+**: The project requires Python 3.10 or higher
- **Docker**: For running Weaviate locally
- **uv**: Modern Python package manager

### Optional

- **Ollama**: For local LLM inference
- **MLflow**: For experiment tracking (can run locally)

## Step-by-Step Setup

### 1. Install uv

```bash
pip install uv
```

Or follow the [official installation guide](https://github.com/astral-sh/uv).

### 2. Create Virtual Environment

```bash
uv venv
```

Activate the environment:

- **Linux/Mac**: `source .venv/bin/activate`
- **Windows**: `.venv\Scripts\activate`

### 3. Install Dependencies

```bash
uv pip install -e .
```

This installs all project dependencies including development dependencies.

### 4. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Weaviate (defaults work for local Docker setup)
WEAVIATE_URL=http://localhost:8080

# Embeddings (defaults work out of the box)
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# LLM Provider (choose one)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Or for Azure OpenAI
# LLM_PROVIDER=azure_openai
# AZURE_OPENAI_API_KEY=your-key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
```

### 5. Start Weaviate

#### Option A: Using Setup Script

```bash
python scripts/setup_weaviate.py
```

#### Option B: Manual Docker Command

```bash
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -p 50051:50051 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -v weaviate_data:/var/lib/weaviate \
  semitechnologies/weaviate:latest
```

Verify Weaviate is running:

```bash
curl http://localhost:8080/v1/.well-known/ready
```

### 6. Start Ollama (if using local LLM)

Download and install from [ollama.ai](https://ollama.ai).

Pull a model:

```bash
ollama pull llama2
```

Verify it's running:

```bash
curl http://localhost:11434/api/tags
```

### 7. Start MLflow (Optional)

```bash
mlflow ui --host 0.0.0.0 --port 5000
```

Access MLflow UI at `http://localhost:5000`

### 8. Start the API Server

```bash
uvicorn rag_system.api.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Verification

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "healthy", "service": "rag-system"}
```

### Test Document Upload

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.pdf"
```

### Test Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "top_k": 3}'
```

## Troubleshooting

### Weaviate Connection Issues

- Ensure Docker is running
- Check if Weaviate container is running: `docker ps`
- Check logs: `docker logs weaviate`
- Verify port 8080 is not in use

### Ollama Connection Issues

- Ensure Ollama is running: `ollama list`
- Check if model is downloaded: `ollama list`
- Verify port 11434 is accessible

### Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `uv pip install -e .`
- Check Python version: `python --version` (should be 3.10+)

### Embedding Model Download

The first run will download the embedding model (~80MB). This is automatic but may take a few minutes depending on your connection.

## Next Steps

- Read the [API Documentation](api.md)
- Check out [Architecture Documentation](architecture.md)
- Try the [Basic Usage Example](../examples/basic_usage.py)
