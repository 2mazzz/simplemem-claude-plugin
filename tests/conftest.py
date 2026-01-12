"""
Shared pytest configuration and fixtures for SimpleMem plugin tests.

This module provides:
- SimpleMem installation fixture (session-scoped for efficiency)
- Test database isolation (function-scoped)
- OpenAI API mocking to avoid costs
- Project context fixtures for testing project-specific functionality
"""

import os
import sys
import json
import shutil
import tempfile
import hashlib
import subprocess
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Generator, Dict, Any

# Test constants
TEST_SIMPLEMEM_DIR = Path("/tmp/SimpleMem_test")
TEST_API_KEY = "sk-test-fake-key-for-testing-12345"


@pytest.fixture(scope="session")
def simplemem_installation() -> Generator[Path, None, None]:
    """
    Session-scoped fixture: Install SimpleMem once for all tests.

    This fixture:
    1. Checks if SimpleMem is already installed in test location
    2. If not, clones and installs it
    3. Creates a test config with fake API key
    4. Yields the installation path
    5. Optionally cleans up after all tests
    """
    install_dir = TEST_SIMPLEMEM_DIR

    # Install if not present
    if not (install_dir / "main.py").exists():
        print(f"\n📦 Installing SimpleMem to {install_dir} for testing...")

        # Create directory
        install_dir.mkdir(parents=True, exist_ok=True)

        # Clone repository
        result = subprocess.run(
            ["git", "clone", "https://github.com/aiming-lab/SimpleMem.git", str(install_dir)],
            capture_output=True,
            timeout=120
        )

        if result.returncode != 0:
            # If clone fails, clean up and skip
            shutil.rmtree(install_dir, ignore_errors=True)
            print(f"Warning: Failed to clone SimpleMem: {result.stderr.decode()}")
            # Still yield even on failure so tests can handle the error
            yield install_dir
            return

        # Install dependencies
        try:
            subprocess.run(
                ["pip", "install", "-r", str(install_dir / "requirements.txt")],
                capture_output=True,
                timeout=300
            )
        except subprocess.TimeoutExpired:
            print("Warning: SimpleMem dependency installation timed out")

    # Create test config
    config_file = install_dir / "config.py"
    config_content = f"""# Test configuration - DO NOT USE IN PRODUCTION
OPENAI_API_KEY = "{TEST_API_KEY}"
"""
    config_file.write_text(config_content)

    yield install_dir

    # Optional: Clean up after all tests (commented out to preserve for debugging)
    # shutil.rmtree(install_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def test_db_path(tmp_path: Path) -> Path:
    """
    Function-scoped fixture: Create isolated database for each test.

    Returns a unique temporary directory for the test database.
    Each test gets a fresh database to ensure complete isolation.
    """
    db_path = tmp_path / "test_simplemem_db"
    db_path.mkdir(parents=True, exist_ok=True)
    return db_path


@pytest.fixture(scope="function")
def mock_openai_embeddings(mocker):
    """
    Mock OpenAI API calls for embeddings to avoid costs.

    This fixture patches the OpenAI client creation to return a mock
    that provides fake but consistent embeddings.
    """
    fake_embedding = [0.1] * 1024  # 1024-dimensional fake embedding

    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=fake_embedding)]

    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = mock_response

    # Patch the OpenAI client creation at the module level
    # This patches where SimpleMem imports OpenAI
    mocker.patch("openai.OpenAI", return_value=mock_client)

    return mock_client


@pytest.fixture(scope="function")
def mock_openai_completions(mocker):
    """
    Mock OpenAI completion calls for semantic compression.

    SimpleMem uses LLM completions during finalize() for compression.
    This fixture mocks those calls to return predictable results.
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Compressed: Test compression result"))]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    mocker.patch("openai.OpenAI", return_value=mock_client)

    return mock_client


@pytest.fixture(scope="function")
def mock_openai_all(mocker):
    """
    Convenience fixture that mocks all OpenAI operations.

    Use this fixture (via decorator) for tests that need to avoid
    any real OpenAI API calls.
    """
    # Create a comprehensive mock client
    fake_embedding = [0.1] * 1024

    mock_response_embeddings = MagicMock()
    mock_response_embeddings.data = [MagicMock(embedding=fake_embedding)]

    mock_response_completions = MagicMock()
    mock_response_completions.choices = [MagicMock(message=MagicMock(content="Compressed: Test compression result"))]

    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = mock_response_embeddings
    mock_client.chat.completions.create.return_value = mock_response_completions

    mocker.patch("openai.OpenAI", return_value=mock_client)

    return mock_client


@pytest.fixture(scope="function")
def project_context(tmp_path: Path, monkeypatch) -> Generator[Dict[str, Any], None, None]:
    """
    Mock a project directory context for testing project-specific functionality.

    This fixture:
    1. Creates a temporary "project" directory
    2. Changes cwd to that directory
    3. Yields the project path and expected hash
    4. Restores original cwd
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(parents=True)

    # Calculate expected hash (same as tools do)
    project_hash = hashlib.md5(str(project_dir).encode()).hexdigest()[:16]

    # Store original directory
    original_cwd = os.getcwd()

    # Change to project directory
    monkeypatch.chdir(project_dir)

    yield {
        "path": project_dir,
        "hash": project_hash,
        "db_path": Path.home() / ".claude" / "projects" / f"simplemem-{project_hash}"
    }

    # Cleanup: Remove project-specific database if created
    projects_dir = Path.home() / ".claude" / "projects"
    if projects_dir.exists():
        db_dir = projects_dir / f"simplemem-{project_hash}"
        if db_dir.exists():
            shutil.rmtree(db_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def clean_project_dbs():
    """
    Cleanup fixture to remove any project-specific databases created during tests.

    This ensures no cross-test contamination of project-specific memory databases.
    """
    yield

    # Clean up test project databases
    projects_dir = Path.home() / ".claude" / "projects"
    if projects_dir.exists():
        for db_dir in projects_dir.glob("simplemem-*"):
            if db_dir.is_dir():
                shutil.rmtree(db_dir, ignore_errors=True)


@pytest.fixture
def tools_path() -> Path:
    """
    Return the absolute path to the tools directory.

    This fixture provides the path to where the CLI tools are located,
    useful for subprocess tests that need to invoke the tools directly.
    """
    return Path(__file__).parent.parent / "tools"


@pytest.fixture
def mock_subprocess_run(mocker):
    """
    Mock subprocess.run for testing installation and CLI execution.

    Use this fixture when you need to mock subprocess calls without
    actually running external commands.
    """
    return mocker.patch("subprocess.run")


@pytest.fixture
def monkeypatch_env(monkeypatch):
    """
    Fixture to manage environment variables cleanly.

    Provides a way to set and unset environment variables without
    affecting other tests.
    """
    def set_env(key: str, value: str):
        monkeypatch.setenv(key, value)

    def delete_env(key: str):
        monkeypatch.delenv(key, raising=False)

    return {"set": set_env, "delete": delete_env}
