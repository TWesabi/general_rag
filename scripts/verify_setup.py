"""Script to verify the RAG system setup."""

import sys

print("RAG System Setup Verification")
print("=" * 50)

# Check Python version
print("\n1. Checking Python version...")
if sys.version_info < (3, 10):
    print(
        f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} detected. Python 3.10+ required."
    )
    sys.exit(1)
else:
    print(
        f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

# Check imports
print("\n2. Checking imports...")
try:
    import fastapi  # noqa: F401

    print("   ✅ FastAPI")
except ImportError:
    print("   ❌ FastAPI not installed")
    sys.exit(1)

try:
    import weaviate

    print("   ✅ Weaviate client")
except ImportError:
    print("   ❌ Weaviate client not installed")
    sys.exit(1)

try:
    import docling  # noqa: F401

    print("   ✅ Docling")
except ImportError:
    print("   ❌ Docling not installed")
    sys.exit(1)

try:
    import sentence_transformers  # noqa: F401

    print("   ✅ Sentence Transformers")
except ImportError:
    print("   ❌ Sentence Transformers not installed")
    sys.exit(1)

try:
    import zenml  # noqa: F401

    print("   ✅ ZenML")
except ImportError:
    print("   ❌ ZenML not installed")
    sys.exit(1)

try:
    import mlflow  # noqa: F401

    print("   ✅ MLflow")
except ImportError:
    print("   ❌ MLflow not installed")
    sys.exit(1)

# Check Weaviate connection
print("\n3. Checking Weaviate connection...")
try:
    import weaviate

    client = weaviate.connect_to_local()
    if client.is_ready():
        print("   ✅ Weaviate is accessible")
        client.close()
    else:
        print("   ⚠️  Weaviate is not ready")
        client.close()
except Exception as e:
    print(f"   ⚠️  Could not connect to Weaviate: {e}")
    print("   Make sure Docker Desktop is running and Weaviate is started")
    print("   Run: python scripts/setup_weaviate.py")

# Check configuration
print("\n4. Checking configuration...")
try:
    from rag_system.config import settings

    print("   ✅ Configuration loaded")
    print(f"      Weaviate URL: {settings.weaviate.url}")
    print(f"      LLM Provider: {settings.llm.provider}")
    print(f"      Embedding Model: {settings.embedding.model_name}")
except Exception as e:
    print(f"   ⚠️  Configuration issue: {e}")

print("\n" + "=" * 50)
print("Setup verification complete!")
print("\nNext steps:")
print("  1. Start the API: python run_api.py")
print("  2. Visit http://localhost:8000/docs for API documentation")
