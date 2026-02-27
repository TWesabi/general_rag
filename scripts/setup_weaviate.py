"""Script to set up Weaviate locally using Docker."""

import subprocess
import sys
import time
from urllib.parse import urlparse


def get_weaviate_port():
    """Get Weaviate HTTP port from WEAVIATE_URL (e.g. .env). Default 8080."""
    try:
        from rag_system.config import settings

        parsed = urlparse(settings.weaviate.url)
        return parsed.port if parsed.port is not None else 8080
    except Exception:
        return 8080


def check_docker():
    """Check if Docker is available and running."""
    try:
        # Check if docker command exists
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        # Check if Docker daemon is running
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def weaviate_container_status():
    """
    Check if a container named 'weaviate' exists and whether it is running.
    Returns: ("running" | "stopped" | "missing")
    """
    result = subprocess.run(
        ["docker", "inspect", "weaviate", "--format", "{{.State.Running}}"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        return "missing"
    return "running" if result.stdout.strip().lower() == "true" else "stopped"


def start_existing_weaviate():
    """Start the existing 'weaviate' container (docker start)."""
    print("Starting existing Weaviate container...")
    try:
        subprocess.run(["docker", "start", "weaviate"], check=True)
        print("Weaviate container started.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")
        return False


def create_weaviate_container(port=8080):
    """Create and run a new Weaviate container (docker run)."""
    print("Creating and starting Weaviate with Docker...")

    # Use same image as official docs; single-node env vars avoid "leader not found" on /v1/schema
    weaviate_image = "cr.weaviate.io/semitechnologies/weaviate:1.35.4"
    docker_cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        "weaviate",
        "-p",
        f"{port}:8080",
        "-p",
        "50051:50051",
        "-e",
        "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true",
        "-e",
        "PERSISTENCE_DATA_PATH=/var/lib/weaviate",
        "-e",
        "CLUSTER_HOSTNAME=node1",
        "-e",
        "RAFT_BOOTSTRAP_EXPECT=1",
        "-v",
        "weaviate_data:/var/lib/weaviate",
        weaviate_image,
    ]

    try:
        subprocess.run(docker_cmd, check=True)
        print("Weaviate container created and started.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error starting Weaviate: {e}")
        return False


def check_weaviate_connection():
    """Check if Weaviate is ready (uses WEAVIATE_URL). Uses /.well-known/ready to avoid schema/leader."""
    print("Checking Weaviate connection...")
    try:
        from rag_system.config import settings

        url = settings.weaviate.url
    except Exception:
        url = "http://localhost:8080"
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.hostname or 'localhost'}:{parsed.port or 8080}"
    ready_url = f"{base}/v1/.well-known/ready"
    max_retries = 20
    sleep_sec = 3
    for i in range(max_retries):
        try:
            import urllib.request

            req = urllib.request.Request(ready_url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    print("Weaviate is ready!")
                    return True
        except Exception:
            pass
        if i < max_retries - 1:
            print(f"Waiting for Weaviate... ({i+1}/{max_retries}, next in {sleep_sec}s)")
            time.sleep(sleep_sec)
    print("Failed to connect to Weaviate (ready endpoint did not respond in time).")
    return False


def main():
    """Main setup function."""
    print("Weaviate Setup Script")
    print("=" * 50)

    # Check Docker
    if not check_docker():
        print("ERROR: Docker is not installed or Docker Desktop is not running.")
        print("Please:")
        print("  1. Install Docker Desktop: https://www.docker.com/products/docker-desktop")
        print("  2. Start Docker Desktop")
        print("  3. Wait for Docker to be ready")
        print("  4. Run this script again")
        sys.exit(1)

    print("Docker is available")

    status = weaviate_container_status()

    # Already running: verify connection and exit
    if status == "running":
        if check_weaviate_connection():
            try:
                from rag_system.config import settings

                url = settings.weaviate.url
            except Exception:
                url = "http://localhost:8080"
            print(f"\nWeaviate is already running at {url}")
            sys.exit(0)
        print("\nContainer is running but Weaviate did not become ready.")
        print("Check: docker logs weaviate")
        print(
            "To recreate with single-node settings: docker rm -f weaviate then run this script again."
        )
        sys.exit(1)

    # Stopped: start existing container
    if status == "stopped":
        if not start_existing_weaviate():
            sys.exit(1)
        if check_weaviate_connection():
            try:
                from rag_system.config import settings

                url = settings.weaviate.url
            except Exception:
                url = "http://localhost:8080"
            print(f"\nSetup complete! Weaviate is running at {url}")
            sys.exit(0)
        print("\nContainer started but connection check failed. Try: docker logs weaviate")
        sys.exit(1)

    # No container: create new one
    port = get_weaviate_port()
    if not create_weaviate_container(port=port):
        sys.exit(1)
    if check_weaviate_connection():
        try:
            from rag_system.config import settings

            url = settings.weaviate.url
        except Exception:
            url = "http://localhost:8080"
        print(f"\nSetup complete! Weaviate is running at {url}")
    else:
        print("\nSetup started but connection check failed. Try: docker logs weaviate")
        sys.exit(1)


if __name__ == "__main__":
    main()
