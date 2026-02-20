# RAG System – Command Reference

Short reference for starting services and running pipelines. Use in this order when starting from scratch.

---

## Bootstrap (create env from pyproject.toml)

**Do this first** so the virtual environment and dependencies are managed by `uv` from `pyproject.toml`:

```bash
# From project root: create .venv and install all dependencies (keeps uv in sync)
uv sync
```

To include dev dependencies (pytest, black, ruff, mypy):

```bash
uv sync --all-extras
```

Then activate and run as usual (or use `uv run` so the venv is used automatically):

```bash
# Windows
.venv\Scripts\activate

# Or run without activating (uv uses .venv automatically)
uv run python run_api.py
```

---

## Start order (when starting everything)

1. **Docker** – ensure Docker Desktop is running (for Weaviate).
2. **Weaviate** – vector DB (required for API and pipelines).
3. **FastAPI** – RAG API (upload, query).
4. **MLflow** (optional) – experiment tracking UI.
5. **ZenML** (optional) – pipeline UI and runs.

---

## Infrastructure

### Weaviate (vector DB)

Port is set by `WEAVIATE_URL` in `.env`. If 8080 is in use (e.g. Open WebUI), set e.g. `WEAVIATE_URL=http://localhost:8081`.

The script starts the existing `weaviate` container if it exists (running or stopped); it only creates a new container when none exists. New containers are created with single-node settings (no "leader not found" on `/v1/schema`). If you already see that error, remove the container and run the script again: `docker rm -f weaviate` then `python scripts/setup_weaviate.py`.

```bash
# Start Weaviate (starts existing container or creates one)
python scripts/setup_weaviate.py
```

```bash
# Or start Weaviate manually (change first 8081 if you use another host port)
docker run -d --name weaviate -p 8081:8080 -p 50051:50051 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -v weaviate_data:/var/lib/weaviate \
  semitechnologies/weaviate:latest
```

```bash
# Stop Weaviate
docker stop weaviate
```

```bash
# Remove Weaviate container (data in volume persists)
docker rm weaviate
```

---

## API server

### FastAPI (RAG API)

```bash
# Start API (uses host/port from .env, default port 8010)
python run_api.py
```

```bash
# Or with uvicorn directly
uvicorn rag_system.api.main:app --host 0.0.0.0 --port 8010 --reload
```

- API: `http://localhost:8010`
- Swagger: `http://localhost:8010/docs`

---

## MLflow (experiment tracking)

### MLflow UI

```bash
# Start MLflow UI (port 5000)
mlflow ui --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

```bash# Or via script
python scripts/init_mlflow.py
```

- UI: `http://localhost:5000`

---

## ZenML (pipelines)

### ZenML server + dashboard

```bash
# Start local ZenML server and open dashboard (stores in .zen)
zenml login --local
```

**Windows:** ZenML cannot run the server as a background daemon. Use blocking mode (keeps the terminal open):

```bash
zenml login --local --blocking
```

If you get `ModuleNotFoundError: No module named 'sqlalchemy_utils'`, install the extra dependency:

```bash
uv pip install sqlalchemy-utils
```

Or run the server in Docker: `zenml login --local --docker`.

- Dashboard URL is printed in the terminal after login.

### Custom project name (ZenML Pro)

By default ZenML uses the project name `default`. **On ZenML OSS (free), only the `default` project is fully supported in the dashboard.** Pipelines and runs in custom projects (e.g. `rag-system`) will not appear there; that behavior requires [ZenML Pro](https://zenml.io/pro).

**To see pipelines and runs in the dashboard (OSS):** use the `default` project:

```bash
zenml project set default
```

Then run your pipelines from the project root; runs will show under **Runs** in the dashboard.

**Where is the “current” project?** On ZenML OSS there is only one project visible in the dashboard: **default**. The dashboard you see (Pipelines, Runs, Stacks in the sidebar) is that single project—there is no project switcher. To confirm from the repo: check `.zen/config.yaml`; `active_project_id` is the active project (the UUID for `default` after `zenml project set default`).

If you use ZenML Pro and want a custom project name:

```bash
zenml project register rag-system --set --set-default
zenml project set rag-system   # switch later
zenml project list              # list projects
```

### See pipelines in the dashboard

Pipelines and runs only appear after you **initialize the project** and **run a pipeline** at least once.

1. **Initialize ZenML in this project** (from project root). This creates a `.zen` directory and sets the source root so the dashboard can associate runs with this repo:

   ```bash
   zenml init
   ```

   If you want a custom project name instead of `default`, run **after** login: `zenml project register <name> --set --set-default` (see [Custom project name](#custom-project-name)).

2. **Run a pipeline from the project root** so a run is registered (Weaviate and ZenML server must be running). For example, ingest one PDF:

   ```bash
   python scripts/run_zenml_pipeline.py path/to/your/document.pdf
   ```

   Or run the ingestion pipeline inline (replace the path):

   ```bash
   python -c "
   from rag_system.pipelines.ingestion import ingestion_pipeline
   doc_id = ingestion_pipeline(file_path='path/to/document.pdf')
   print('Document ID:', doc_id)
   "
   ```

   After that, open the dashboard URL from the terminal; you should see the pipeline run under **Runs** (and the pipeline under **Pipelines** once it has run).

3. **Optional:** Register this repo as a [code repository](https://docs.zenml.io/user-guide/production-guide/connect-code-repository) (e.g. GitHub) so ZenML tracks code versions and can speed up Docker builds.

### Run pipelines (Python)

```bash
# From project root, with venv activated
python -c "
from rag_system.pipelines.ingestion import ingestion_pipeline
doc_id = ingestion_pipeline(file_path='path/to/document.pdf')
print('Document ID:', doc_id)
"
```

```bash
# Batch indexing – all PDFs in a directory
python -c "
from rag_system.pipelines.indexing import indexing_pipeline
doc_ids = indexing_pipeline(directory='path/to/pdf/folder')
print('Document IDs:', doc_ids)
"
```

Replace `path/to/document.pdf` and `path/to/pdf/folder` with real paths.

---

## Scripts

### Verify setup

```bash
# Check Python, imports, Weaviate connection, config
python scripts/verify_setup.py
```

### Run ZenML pipeline (for dashboard)

```bash
# Ingest one PDF via ZenML pipeline (run appears in ZenML dashboard)
python scripts/run_zenml_pipeline.py path/to/file.pdf
```

Run from project root after `zenml init` and `zenml login --local`.

### Test document pipeline (no API)

```bash
# Run parse → chunk → embed → store for one PDF (with timing)
python scripts/test_document_processing.py path/to/file.pdf
```

---

## Ollama (local LLM) – required for query answers

The **query** endpoint needs Ollama running to generate answers. Without it you get a 404 on `/api/generate`.

```bash
# Start Ollama (if installed)
ollama serve
# In another terminal, pull the model set in .env (e.g. OLLAMA_MODEL=llama2)
ollama pull  qwen
```

---

## Troubleshooting

**SSL error when downloading models** (`certificate verify failed` when contacting Hugging Face — affects Docling, embeddings): set in `.env`:
```bash
DISABLE_SSL_VERIFY=true
```
Use only in dev / behind corporate proxy; re-enable verification in production.

---

## Port summary

| Service   | Default port | Note |
|----------|--------------|------|
| Weaviate | 8080 (HTTP), 50051 (gRPC) | Set `WEAVIATE_URL=http://localhost:8081` if 8080 is taken (e.g. Open WebUI) |
| FastAPI  | 8010 | Set `API_PORT` in `.env` |
| MLflow   | 5000 | |
| Ollama   | 11434 | |
