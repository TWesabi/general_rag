# New PC Setup — Development Environment

> Generated from project analysis. Edit as needed before handing to IT.

---

## Core Tools

| Tool | Version | Notes |
|---|---|---|
| **Python** | 3.10 (exact) | Project targets py310 |
| **uv** | Latest | Fast Python package manager by Astral |
| **Git** | Latest | |
| **Docker Desktop** | Latest | Requires WSL2 on Windows |
| **VS Code** | Latest | |

---

## VS Code Extensions

Install these after VS Code is set up:

| Extension | ID |
|---|---|
| Python | ms-python.python |
| Pylance | ms-python.vscode-pylance |
| Ruff | charliermarsh.ruff |
| Black Formatter | ms-python.black-formatter |
| GitLens | eamodio.gitlens |

---

## Local Services

| Service | Version | How | Port |
|---|---|---|---|
| **PostgreSQL** | 16 | Docker Compose (included in project) | 5432 |
| **Weaviate** | Latest | Docker | 8080 |
| **Ollama** | Latest | Native install — ollama.com/download | 11434 |
| **MLflow** | 3.8.1 | Python package (auto-installed) | 5000 |
| **ZenML** | 0.93.1 | Python package (auto-installed) | — |

---

## Ollama Models to Pull

After Ollama is installed, run these commands:

```bash
ollama pull bge-m3:latest     # embedding model
ollama pull llama2            # LLM (default, can be changed in .env)
```

---

## Project Setup Steps

```bash
# 1. Clone the repo
git clone <repo-url>
cd rag_system

# 2. Install Python 3.10 via uv
uv python install 3.10

# 3. Install all dependencies from lock file
uv sync

# 4. Install pre-commit hooks
uv run pre-commit install

# 5. Start Docker services (PostgreSQL + Weaviate)
docker compose up -d

# 6. Copy and configure environment
cp .env.example .env
# Edit .env with correct values
```

---

## Key Python Dependencies (for reference)

These are installed automatically via `uv sync` — no manual action needed.

| Package | Version |
|---|---|
| fastapi | 0.115.8 |
| uvicorn | 0.40.0 |
| sqlalchemy | 2.0.46 |
| sqlmodel | 0.0.18 |
| pydantic | 2.11.9 |
| docling | 2.70.0 |
| sentence-transformers | 5.2.1 |
| torch | 2.10.0 |
| transformers | 4.57.6 |
| ollama | 0.6.1 |
| mlflow | 3.8.1 |
| zenml | 0.93.1 |
| psycopg2-binary | Latest |
| alembic | 1.15.2 |
| numpy | 2.2.6 |
| pandas | 2.3.3 |
| black | 26.1.0 |
| ruff | 0.12.9 |
| mypy | Latest |
| pytest | Latest |
| pre-commit | Latest |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
# Database
DATABASE_URL=postgresql://rag_user:rag_password@localhost:5432/rag_db

# Weaviate (vector DB)
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=
WEAVIATE_USE_GRPC=false

# Ollama (local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Embeddings
EMBEDDING_PROVIDER=ollama
EMBEDDING_OLLAMA_MODEL=bge-m3:latest
EMBEDDING_OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=rag-system

# ZenML
ZENML_STORE_TYPE=local
ZENML_STORE_PATH=.zen

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Azure OpenAI (optional)
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## Summary for IT

**Must install manually:**

1. Python 3.10
2. uv — `winget install astral-sh.uv` or `pip install uv`
3. Git
4. Docker Desktop (enable WSL2 integration)
5. VS Code
6. Ollama — https://ollama.com/download

**Everything else** (Python packages, PostgreSQL, Weaviate) is handled automatically by `uv sync` and `docker compose up -d`.

---

## Notes / To-Do

- [ ] Add repo URL above
- [ ] Confirm Ollama model names with team
- [ ] Add any Azure OpenAI credentials needed
- [ ] Add any other tools or accounts needed (e.g., GitHub access, cloud credentials)


SSH Keys — what to copy, where to place it, how to fix permissions
Git Config — copy .gitconfig or re-apply the commands with your name/email
AWS Config & Credentials — copy the .aws folder
Azure CLI — re-login after install
Active Project .env files — list of files to manually copy
Conda Environments — export/import commands
Licenses — PDF-XChange PRO, Copilot, M365
Final Checklist — one list for IT to tick off everything