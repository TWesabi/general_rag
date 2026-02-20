"""Script to initialize MLflow tracking server."""

import subprocess
import sys
import time

import requests


def check_mlflow_running():
    """Check if MLflow is already running."""
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def start_mlflow():
    """Start MLflow tracking server."""
    print("Starting MLflow tracking server...")

    mlflow_cmd = [
        "mlflow",
        "ui",
        "--host",
        "0.0.0.0",
        "--port",
        "5000",
        "--backend-store-uri",
        "sqlite:///mlflow.db",
    ]

    try:
        print("MLflow UI will be available at http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        subprocess.run(mlflow_cmd, check=True)
    except KeyboardInterrupt:
        print("\nMLflow server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting MLflow: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: MLflow is not installed.")
        print("Install it with: pip install mlflow")
        sys.exit(1)


def main():
    """Main initialization function."""
    print("MLflow Setup Script")
    print("=" * 50)

    if check_mlflow_running():
        print("MLflow is already running at http://localhost:5000")
        sys.exit(0)

    start_mlflow()


if __name__ == "__main__":
    main()
