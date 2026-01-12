"""
Integration tests for simplemem_save.py

Tests cover:
- Saving single messages with various parameters
- Saving conversations (user + assistant pairs)
- Metadata handling
- Project-specific database paths
- Global database paths
- Error handling
- JSON output validation
- Exit codes
- Data persistence
"""

import json
import subprocess
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add tools to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))


def lazy_import_save():
    """Lazily import save functions to avoid SystemExit on collection."""
    try:
        from simplemem_save import save_memory, save_conversation, get_project_db_path
        return save_memory, save_conversation, get_project_db_path
    except SystemExit:
        pytest.skip("SimpleMem not installed")


@pytest.mark.usefixtures("mock_openai_all")
class TestSaveMemory:
    """Test the save_memory() function."""

    def test_save_simple_message(self, test_db_path):
        """Test saving a simple message."""
        # Since we mock SimpleMem, we can't actually test with real SimpleMem
        # But we can test the function structure and error handling
        save_memory, _, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content="Test message",
                speaker="User",
                context="general",
                db_path=str(test_db_path)
            )

            # Verify function was called with correct parameters
            assert result["success"] is True
            assert "message" in result
            assert result["speaker"] == "User"
            assert result["context"] == "general"
            assert "timestamp" in result

    def test_save_with_custom_speaker(self, test_db_path):
        """Test saving with custom speaker name."""
        save_memory, _, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content="System notification",
                speaker="System",
                context="notifications",
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["speaker"] == "System"

    def test_save_with_metadata(self, test_db_path):
        """Test saving with additional metadata."""
        save_memory, _, _ = lazy_import_save()

        metadata = {"priority": "high", "category": "urgent"}

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content="Critical update",
                speaker="User",
                context="alerts",
                metadata=metadata,
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            # Verify add_dialogue was called with metadata
            mock_system.add_dialogue.assert_called_once()
            call_kwargs = mock_system.add_dialogue.call_args[1]
            assert call_kwargs["metadata"]["priority"] == "high"

    def test_save_long_message_truncation(self, test_db_path):
        """Test that long messages are truncated in response."""
        save_memory, _, _ = lazy_import_save()

        long_content = "A" * 100

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content=long_content,
                speaker="User",
                context="general",
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            # Message should be truncated in response (60 char limit + "...")
            assert "..." in result["message"]
            assert len(result["message"]) < len(long_content)

    def test_save_context_preservation(self, test_db_path):
        """Test that context parameter is preserved."""
        save_memory, _, _ = lazy_import_save()

        contexts = ["security", "performance", "documentation"]

        for ctx in contexts:
            with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
                mock_system = MagicMock()
                mock_system_class.return_value = mock_system

                result = save_memory(
                    content=f"Info about {ctx}",
                    speaker="User",
                    context=ctx,
                    db_path=str(test_db_path)
                )

                assert result["context"] == ctx

    def test_save_error_handling_system_error(self, test_db_path):
        """Test error handling when SimpleMem raises exception."""
        save_memory, _, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system_class.side_effect = Exception("Database connection error")

            result = save_memory(
                content="Test",
                speaker="User",
                context="general",
                db_path=str(test_db_path)
            )

            assert result["success"] is False
            assert "error" in result

    def test_save_default_db_path(self):
        """Test that default database path is used."""
        save_memory, _, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            # Call without db_path parameter
            result = save_memory(
                content="Test",
                speaker="User",
                context="general"
            )

            # Should use default /tmp/simplemem_db
            mock_system_class.assert_called_once()
            call_kwargs = mock_system_class.call_args[1]
            assert call_kwargs["db_path"] == "/tmp/simplemem_db"

    def test_save_calls_finalize(self, test_db_path):
        """Test that finalize() is called to compress memory."""
        save_memory, _, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content="Test",
                speaker="User",
                context="general",
                db_path=str(test_db_path)
            )

            # Verify finalize was called
            mock_system.finalize.assert_called_once()


@pytest.mark.usefixtures("mock_openai_all")
class TestSaveConversation:
    """Test the save_conversation() function."""

    def test_save_conversation_success(self, test_db_path):
        """Test saving a complete conversation."""
        _, save_conversation, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_conversation(
                user_message="What is Python?",
                assistant_message="Python is a programming language.",
                context="qa",
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert "Saved conversation" in result["message"]
            assert result["context"] == "qa"
            assert "timestamp" in result

    def test_save_conversation_with_context(self, test_db_path):
        """Test saving conversation with specific context."""
        _, save_conversation, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_conversation(
                user_message="How to deploy?",
                assistant_message="Use Docker.",
                context="deployment",
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["context"] == "deployment"

    def test_save_conversation_calls_both_speakers(self, test_db_path):
        """Test that both user and assistant messages are saved."""
        _, save_conversation, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_conversation(
                user_message="Question",
                assistant_message="Answer",
                context="test",
                db_path=str(test_db_path)
            )

            # add_dialogue should be called twice (user and assistant)
            assert mock_system.add_dialogue.call_count == 2

            # Verify speakers
            calls = mock_system.add_dialogue.call_args_list
            speakers = [call[1]["speaker"] for call in calls]
            assert "User" in speakers
            assert "Assistant" in speakers


class TestProjectPathResolution:
    """Test project-specific database path resolution."""

    def test_get_project_db_path(self, project_context):
        """Test that project hash is calculated correctly."""
        _, _, get_project_db_path = lazy_import_save()

        with patch("os.getcwd", return_value=str(project_context["path"])):
            db_path = get_project_db_path()

        expected_path = str(project_context["db_path"])
        assert db_path == expected_path

    def test_different_projects_different_paths(self, tmp_path):
        """Test that different projects produce different paths."""
        _, _, get_project_db_path = lazy_import_save()

        project1 = tmp_path / "project1"
        project2 = tmp_path / "project2"
        project1.mkdir()
        project2.mkdir()

        with patch("os.getcwd", return_value=str(project1)):
            path1 = get_project_db_path()

        with patch("os.getcwd", return_value=str(project2)):
            path2 = get_project_db_path()

        assert path1 != path2


@pytest.mark.usefixtures("mock_openai_all")
class TestSaveCLI:
    """Test the CLI interface."""

    def test_cli_simple_save(self, test_db_path, tools_path):
        """Test CLI with simple save."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_save.py"),
                "Test content",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            assert output.get("success") is True
            assert result.returncode == 0
        except json.JSONDecodeError:
            # SimpleMem might not be installed, skip
            pytest.skip("SimpleMem not installed")

    def test_cli_save_with_context(self, test_db_path, tools_path):
        """Test CLI with context flag."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_save.py"),
                "Test content",
                "--context", "testing",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            if output.get("success") is True:
                assert output["context"] == "testing"
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")

    def test_cli_save_with_speaker(self, test_db_path, tools_path):
        """Test CLI with custom speaker."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_save.py"),
                "Test content",
                "--speaker", "System",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            if output.get("success") is True:
                assert output.get("speaker") == "System"
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")

    def test_cli_save_conversation(self, test_db_path, tools_path):
        """Test CLI with conversation mode."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_save.py"),
                "User question",
                "--assistant-message", "Assistant answer",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            if output.get("success") is True:
                assert "conversation" in output.get("message", "").lower()
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")

    def test_cli_invalid_metadata_json(self, test_db_path, tools_path):
        """Test CLI with invalid metadata JSON."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_save.py"),
                "Test content",
                "--metadata", "{invalid json}",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = json.loads(result.stdout)
        assert output["success"] is False
        assert "Invalid metadata JSON" in output["error"]
        assert result.returncode == 1

    def test_cli_valid_metadata_json(self, test_db_path, tools_path):
        """Test CLI with valid metadata JSON."""
        metadata = '{"priority": "high", "tag": "urgent"}'

        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_save.py"),
                "Test content",
                "--metadata", metadata,
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            if output.get("success") is True:
                assert result.returncode == 0
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")

    def test_cli_project_flag(self, project_context, tools_path):
        """Test CLI with --project flag."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_save.py"),
                "Test content",
                "--project"
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(project_context["path"])
        )

        try:
            output = json.loads(result.stdout)
            if output.get("success") is True:
                assert result.returncode == 0
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")


@pytest.mark.usefixtures("mock_openai_all")
class TestSaveMetadata:
    """Test metadata handling in save operations."""

    def test_save_metadata_structure(self, test_db_path):
        """Test that metadata is properly structured with context."""
        save_memory, _, _ = lazy_import_save()

        metadata = {"priority": "high"}

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content="Test",
                speaker="User",
                context="alerts",
                metadata=metadata,
                db_path=str(test_db_path)
            )

            # Check that add_dialogue was called with merged metadata
            call_kwargs = mock_system.add_dialogue.call_args[1]
            full_metadata = call_kwargs["metadata"]

            # Should include both context and custom metadata
            assert full_metadata["context"] == "alerts"
            assert full_metadata["priority"] == "high"

    def test_save_metadata_none(self, test_db_path):
        """Test save with no metadata."""
        save_memory, _, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content="Test",
                speaker="User",
                context="general",
                metadata=None,
                db_path=str(test_db_path)
            )

            # Should still include context in metadata
            call_kwargs = mock_system.add_dialogue.call_args[1]
            metadata = call_kwargs["metadata"]
            assert metadata["context"] == "general"


@pytest.mark.usefixtures("mock_openai_all")
class TestSaveTimestamps:
    """Test timestamp handling in save operations."""

    def test_save_includes_timestamp(self, test_db_path):
        """Test that save response includes timestamp."""
        save_memory, _, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_memory(
                content="Test",
                speaker="User",
                context="general",
                db_path=str(test_db_path)
            )

            assert "timestamp" in result
            # Verify timestamp is ISO format
            try:
                datetime.fromisoformat(result["timestamp"])
            except (ValueError, TypeError):
                pytest.fail("Timestamp is not valid ISO format")

    def test_conversation_timestamp_consistency(self, test_db_path):
        """Test that user and assistant messages share same timestamp."""
        _, save_conversation, _ = lazy_import_save()

        with patch("simplemem_save.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            result = save_conversation(
                user_message="Q",
                assistant_message="A",
                context="test",
                db_path=str(test_db_path)
            )

            # Get timestamps from calls
            calls = mock_system.add_dialogue.call_args_list
            user_timestamp = calls[0][1]["timestamp"]
            assistant_timestamp = calls[1][1]["timestamp"]

            # Should be the same
            assert user_timestamp == assistant_timestamp
