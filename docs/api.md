# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, implement proper authentication.

## Endpoints

### Health Check

#### GET `/health`

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "service": "rag-system"
}
```

#### GET `/health/ready`

Check API readiness (checks dependencies).

**Response:**

```json
{
  "status": "ready"
}
```

### Document Management

#### POST `/documents/upload`

Upload and process a document.

**Request:**

- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing the PDF file

**Response:**

```json
{
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "chunks_count": 42,
  "status": "processed"
}
```

**Status Codes:**

- `201`: Document processed successfully
- `400`: Invalid file type or missing file
- `500`: Processing error

#### GET `/documents`

List all documents.

**Query Parameters:**

- `limit` (optional): Maximum number of documents (default: 100)

**Response:**

```json
{
  "documents": [
    {
      "id": "uuid-string",
      "source": "path/to/document.pdf",
      "file_type": "pdf",
      "file_size": 12345,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "count": 1
}
```

#### GET `/documents/{document_id}`

Get a specific document by ID.

**Response:**

```json
{
  "id": "uuid-string",
  "content": "Full document text...",
  "source": "path/to/document.pdf",
  "file_type": "pdf",
  "file_size": 12345,
  "created_at": "2024-01-01T00:00:00"
}
```

**Status Codes:**

- `200`: Document found
- `404`: Document not found

#### DELETE `/documents/{document_id}`

Delete a document and all its chunks.

**Response:**

```json
{
  "status": "deleted",
  "document_id": "uuid-string"
}
```

**Status Codes:**

- `200`: Document deleted successfully
- `404`: Document not found

### Query

#### POST `/query`

Query the RAG system.

**Request Body:**

```json
{
  "query": "What is the main topic?",
  "top_k": 5,
  "score_threshold": 0.0,
  "include_metadata": true,
  "filters": null
}
```

**Fields:**

- `query` (required): Query text
- `top_k` (optional): Number of results (default: 5)
- `score_threshold` (optional): Minimum score (default: 0.0)
- `include_metadata` (optional): Include metadata (default: true)
- `filters` (optional): Additional filters

**Response:**

```json
{
  "query": "What is the main topic?",
  "retrieved_chunks": [
    {
      "chunk_id": "uuid-string",
      "content": "Chunk content...",
      "score": 0.85,
      "metadata": {
        "chunk_index": 0,
        "document_id": "doc-uuid",
        "source": "document.pdf",
        "file_type": "pdf"
      },
      "document_id": "doc-uuid"
    }
  ],
  "answer": "Generated answer based on retrieved chunks...",
  "metadata": {
    "chunks_count": 5,
    "provider": "ollama"
  }
}
```

#### POST `/query/stream`

Query with streaming response.

**Request:** Same as `/query`

**Response:** Streaming text/plain response

**Usage Example:**

```python
import httpx

async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "http://localhost:8000/query/stream",
        json={"query": "What is the main topic?"}
    ) as response:
        async for chunk in response.aiter_text():
            print(chunk, end="")
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message"
}
```

**Common Status Codes:**

- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

Visit `http://localhost:8000/redoc` for ReDoc documentation.

## Example Usage

### Python

```python
import httpx

# Upload document
with open("document.pdf", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/documents/upload",
        files={"file": f}
    )
doc_id = response.json()["document_id"]

# Query
response = httpx.post(
    "http://localhost:8000/query",
    json={"query": "What is this about?", "top_k": 3}
)
result = response.json()
print(result["answer"])
```

### cURL

```bash
# Upload
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf"

# Query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this about?"}'
```
