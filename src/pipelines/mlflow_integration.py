"""MLflow integration for experiment tracking and prompt registry."""

import mlflow
from mlflow.tracking import MlflowClient

from ..config import settings


class MLflowTracker:
    """MLflow tracker for RAG experiments."""

    def __init__(self):
        """Initialize MLflow tracker."""
        mlflow.set_tracking_uri(settings.mlflow.tracking_uri)
        mlflow.set_experiment(settings.mlflow.experiment_name)
        self.client = MlflowClient()

    def start_run(self, run_name: str | None = None):
        """Start a new MLflow run."""
        return mlflow.start_run(run_name=run_name)

    def log_metrics(self, metrics: dict, step: int | None = None):
        """Log metrics to MLflow."""
        mlflow.log_metrics(metrics, step=step)

    def log_params(self, params: dict):
        """Log parameters to MLflow."""
        mlflow.log_params(params)

    def log_retrieval_metrics(self, query: str, retrieved_chunks: list, latency: float):
        """
        Log retrieval-specific metrics.

        Args:
            query: Query text
            retrieved_chunks: Retrieved chunks
            latency: Query latency in seconds
        """
        metrics = {
            "retrieval_latency": latency,
            "retrieved_chunks_count": len(retrieved_chunks),
            "avg_chunk_score": (
                sum(c.score for c in retrieved_chunks) / len(retrieved_chunks)
                if retrieved_chunks
                else 0.0
            ),
        }
        self.log_metrics(metrics)

    def register_prompt(self, name: str, prompt_template: str, version: int = 1):
        """
        Register a prompt template in MLflow.

        Args:
            name: Prompt name
            prompt_template: Prompt template string
            version: Prompt version
        """
        # Store prompt as artifact
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(prompt_template)
            temp_path = f.name

        try:
            mlflow.log_artifact(temp_path, artifact_path="prompts")
            # Register as model (prompt template)
            self.client.create_registered_model(name)
            self.client.create_model_version(
                name=name,
                source=temp_path,
                run_id=mlflow.active_run().info.run_id if mlflow.active_run() else None,
            )
        finally:
            os.unlink(temp_path)

    def get_prompt(self, name: str, version: int | None = None) -> str:
        """
        Retrieve a prompt template from MLflow.

        Args:
            name: Prompt name
            version: Prompt version (latest if None)

        Returns:
            Prompt template string
        """
        if version:
            model_version = self.client.get_model_version(name, version)
        else:
            model_versions = self.client.get_latest_versions(name, stages=["None"])
            if not model_versions:
                raise ValueError(f"Prompt '{name}' not found")
            model_version = model_versions[0]

        # Download and read prompt file
        import os
        import tempfile

        download_path = self.client.download_artifacts(
            model_version.run_id, "prompts", dst_path=tempfile.mkdtemp()
        )

        prompt_files = [f for f in os.listdir(download_path) if f.endswith(".txt")]
        if not prompt_files:
            raise ValueError(f"Prompt file not found for '{name}'")

        prompt_path = os.path.join(download_path, prompt_files[0])
        with open(prompt_path, "r") as f:
            return f.read()
