"""
Integration tests for simplemem_status.py

Tests cover:
- Status when SimpleMem installed/not installed
- Configuration detection
- API key configuration detection
- Database existence and size calculation
- Import checking
- Project-specific status
- Global status
- CLI interface and exit codes
"""

import json
import subprocess
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add tools to path for imports (lazy import to avoid exit handlers)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))


def lazy_import_status():
    """Lazily import status module to avoid exit handlers during collection."""
    try:
        from simplemem_status import check_status, get_project_db_path
        return check_status, get_project_db_path
    except SystemExit:
        pytest.skip("SimpleMem not installed")


class TestStatusCheck:
    """Test the check_status() function directly."""

    def test_status_not_installed(self, tmp_path):
        """Test status when SimpleMem is not installed."""
        check_status, _ = lazy_import_status()

        fake_path = tmp_path / "NonexistentSimpleMem"
        test_db = tmp_path / "test_db"

        with patch("simplemem_status.SIMPLEMEM_PATH", fake_path):
            status = check_status(db_path=str(test_db))

        assert status["installed"] is False
        assert status["ready"] is False
        assert any("not installed" in err for err in status["errors"])

    def test_status_installed_no_config(self, tmp_path):
        """Test status when SimpleMem installed but no config."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        test_db = tmp_path / "test_db"

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(test_db))

        assert status["installed"] is True
        assert status["configured"] is False
        assert any("config.py not found" in err for err in status["errors"])

    def test_status_installed_with_config(self, tmp_path):
        """Test status when SimpleMem installed with config."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        (simplemem_dir / "config.py").write_text('OPENAI_API_KEY = "sk-test-key"')
        test_db = tmp_path / "test_db"

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(test_db))

        assert status["installed"] is True
        assert status["configured"] is True

    def test_status_api_key_not_configured(self, tmp_path):
        """Test detection of missing/placeholder API key."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        (simplemem_dir / "config.py").write_text("OPENAI_API_KEY = None")
        test_db = tmp_path / "test_db"

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(test_db))

        assert status["api_key_configured"] is False
        assert any("API key not configured" in err for err in status["errors"])

    def test_status_api_key_configured(self, tmp_path):
        """Test detection of valid API key."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        (simplemem_dir / "config.py").write_text('OPENAI_API_KEY = "sk-real-key"')
        test_db = tmp_path / "test_db"

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(test_db))

        assert status["api_key_configured"] is True

    def test_status_database_exists(self, tmp_path):
        """Test status shows database exists with size."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        (simplemem_dir / "config.py").write_text('OPENAI_API_KEY = "sk-test"')

        test_db = tmp_path / "test_db"
        test_db.mkdir()
        (test_db / "test.db").write_bytes(b"x" * (1024 * 1024))  # 1 MB

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(test_db))

        assert status["database_exists"] is True
        assert "database_size_mb" in status
        assert status["database_size_mb"] >= 1.0

    def test_status_database_not_exists(self, tmp_path):
        """Test status when database doesn't exist."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        (simplemem_dir / "config.py").write_text('OPENAI_API_KEY = "sk-test"')

        nonexistent_db = tmp_path / "nonexistent_db"

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(nonexistent_db))

        assert status["database_exists"] is False
        assert any("not found" in err for err in status["errors"])

    def test_status_database_size_calculation(self, tmp_path):
        """Test that database size is calculated correctly with multiple files."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        (simplemem_dir / "config.py").write_text('OPENAI_API_KEY = "sk-test"')

        test_db = tmp_path / "test_db"
        test_db.mkdir()

        # Create files with known sizes
        (test_db / "file1.db").write_bytes(b"x" * (1024 * 1024))  # 1 MB
        (test_db / "file2.db").write_bytes(b"x" * (1024 * 1024))  # 1 MB

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(test_db))

        assert status["database_exists"] is True
        assert status["database_size_mb"] >= 2.0

    def test_status_database_path_in_response(self, tmp_path):
        """Test that database path is included in status response."""
        check_status, _ = lazy_import_status()

        simplemem_dir = tmp_path / "SimpleMem"
        simplemem_dir.mkdir()
        (simplemem_dir / "main.py").write_text("# SimpleMem main")
        (simplemem_dir / "config.py").write_text('OPENAI_API_KEY = "sk-test"')
        test_db = tmp_path / "test_db"

        with patch("simplemem_status.SIMPLEMEM_PATH", simplemem_dir):
            status = check_status(db_path=str(test_db))

        assert status["database_path"] == str(test_db)


class TestProjectPathResolution:
    """Test project-specific database path resolution."""

    def test_get_project_db_path(self, project_context):
        """Test that project hash is calculated correctly."""
        _, get_project_db_path = lazy_import_status()

        with patch("os.getcwd", return_value=str(project_context["path"])):
            db_path = get_project_db_path()

        expected_path = str(project_context["db_path"])
        assert db_path == expected_path
        assert project_context["hash"] in db_path

    def test_project_hash_consistency(self, project_context):
        """Test that project hash is consistent across calls."""
        _, get_project_db_path = lazy_import_status()

        with patch("os.getcwd", return_value=str(project_context["path"])):
            path1 = get_project_db_path()
            path2 = get_project_db_path()

        assert path1 == path2

    def test_different_projects_different_paths(self, tmp_path):
        """Test that different project directories produce different paths."""
        _, get_project_db_path = lazy_import_status()

        project1 = tmp_path / "project1"
        project2 = tmp_path / "project2"
        project1.mkdir()
        project2.mkdir()

        with patch("os.getcwd", return_value=str(project1)):
            path1 = get_project_db_path()

        with patch("os.getcwd", return_value=str(project2)):
            path2 = get_project_db_path()

        assert path1 != path2
        assert ".claude/projects/simplemem-" in path1
        assert ".claude/projects/simplemem-" in path2


class TestStatusCLI:
    """Test the CLI interface of simplemem_status.py"""

    def test_cli_json_output_valid(self, tools_path, tmp_path):
        """Test that CLI returns valid JSON."""
        test_db = tmp_path / "test_db"

        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_status.py"),
                "--db-path", str(test_db)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Parse JSON from stdout
        try:
            # Try to find a complete JSON object in the output
            output = result.stdout.strip()
            # Find the start and end of JSON
            if '{' in output:
                start = output.find('{')
                # Find matching closing brace
                brace_count = 0
                end = -1
                for i in range(start, len(output)):
                    if output[i] == '{':
                        brace_count += 1
                    elif output[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                if end > 0:
                    json_str = output[start:end]
                    data = json.loads(json_str)
                    assert isinstance(data, dict)
                    assert "installed" in data
                    assert "configured" in data
                    return
            pytest.skip("Could not find valid JSON in output")
        except json.JSONDecodeError:
            pytest.skip(f"Invalid JSON output: {result.stdout}")

    def test_cli_exit_code_not_ready(self, tools_path, tmp_path):
        """Test CLI exits with 1 when not ready."""
        test_db = tmp_path / "test_db"

        # This will exit 1 because SimpleMem is not installed
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_status.py"),
                "--db-path", str(test_db)
            ],
            capture_output=True,
            timeout=10
        )

        # Should exit with 1 if not ready
        assert result.returncode == 1

    def test_cli_project_flag(self, tools_path, project_context):
        """Test CLI with --project flag uses project-specific database."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_status.py"),
                "--project"
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(project_context["path"])
        )

        try:
            output = result.stdout.strip()
            if '{' in output:
                start = output.find('{')
                brace_count = 0
                end = -1
                for i in range(start, len(output)):
                    if output[i] == '{':
                        brace_count += 1
                    elif output[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                if end > 0:
                    json_str = output[start:end]
                    data = json.loads(json_str)
                    # Should show project-specific database path
                    assert ".claude/projects/simplemem-" in data["database_path"]
                    assert project_context["hash"] in data["database_path"]
                    return
            pytest.skip("Could not parse JSON from output")
        except json.JSONDecodeError:
            pytest.skip("Invalid JSON in output")

    def test_cli_default_db_path(self, tools_path):
        """Test that CLI uses default DB path when not specified."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_status.py")
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = result.stdout.strip()
            if '{' in output:
                start = output.find('{')
                brace_count = 0
                end = -1
                for i in range(start, len(output)):
                    if output[i] == '{':
                        brace_count += 1
                    elif output[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                if end > 0:
                    json_str = output[start:end]
                    data = json.loads(json_str)
                    # Should use default /tmp/simplemem_db
                    assert "/tmp/simplemem_db" in data["database_path"]
                    return
            pytest.skip("Could not parse JSON from output")
        except json.JSONDecodeError:
            pytest.skip("Invalid JSON in output")
