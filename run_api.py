"""Main entry point for running the API server."""

import os

# SSL workaround for Hugging Face downloads (Docling, embeddings, etc.)
# Checks both DISABLE_SSL_VERIFY and EMBEDDING_DISABLE_SSL_VERIFY for backwards compat
_disable_ssl = any(
    os.environ.get(k, "").strip().lower() in ("true", "1", "on")
    for k in ("DISABLE_SSL_VERIFY", "EMBEDDING_DISABLE_SSL_VERIFY")
)

if _disable_ssl:
    import ssl
    import urllib3

    # Suppress SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Patch ssl module BEFORE any other imports
    _original_create_default_context = ssl.create_default_context

    def _no_verify_context(purpose=ssl.Purpose.SERVER_AUTH, *, cafile=None, capath=None, cadata=None):
        ctx = _original_create_default_context(purpose, cafile=cafile, capath=capath, cadata=cadata)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    ssl.create_default_context = _no_verify_context

    # Also patch requests.Session to default verify=False
    import requests
    _original_session_init = requests.Session.__init__

    def _patched_session_init(self, *args, **kwargs):
        _original_session_init(self, *args, **kwargs)
        self.verify = False

    requests.Session.__init__ = _patched_session_init

    # Configure huggingface_hub backend
    try:
        from huggingface_hub import configure_http_backend

        def _hf_backend_factory():
            s = requests.Session()
            s.verify = False
            return s

        configure_http_backend(backend_factory=_hf_backend_factory)
    except Exception:
        pass

import sys
from pathlib import Path

# Add src to path so imports work
_PROJECT_ROOT = Path(__file__).resolve().parent
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import uvicorn

from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
    )
