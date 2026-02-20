"""Run the ZenML ingestion pipeline from the project root.

Use this to trigger a pipeline run so it shows up in the ZenML dashboard.
Run from project root after `zenml init` and `zenml login --local` (or --local --blocking).

Example:
    python scripts/run_zenml_pipeline.py path/to/document.pdf
"""

import sys
from pathlib import Path

# Ensure project root and src are on path when run as script
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_zenml_pipeline.py <path/to/document.pdf>")
        print()
        print("Run from project root after: zenml init && zenml login --local")
        print("The pipeline run will appear in the ZenML dashboard.")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    if file_path.suffix.lower() != ".pdf":
        print("Warning: File is not a PDF; parser may fail.")

    from rag_system.pipelines.ingestion import ingestion_pipeline

    print(f"Ingesting: {file_path}")
    doc_id = ingestion_pipeline(file_path=str(file_path.resolve()))
    print(f"Document ID: {doc_id}")
    print("Check the ZenML dashboard for this run.")


if __name__ == "__main__":
    main()
