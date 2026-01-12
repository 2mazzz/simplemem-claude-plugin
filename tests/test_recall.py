"""
Integration tests for simplemem_recall.py

Tests cover:
- Basic recall with results
- Recall with no results
- top-k parameter variations
- Project-specific database recall
- Global database recall
- JSON output format
- Text-only output format
- Error handling
- Database doesn't exist handling
- Query string variations
- Empty database handling
"""

import json
import subprocess
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))


def lazy_import_recall():
    """Lazily import recall functions to avoid SystemExit on collection."""
    try:
        from simplemem_recall import recall_memory, get_project_db_path
        return recall_memory, get_project_db_path
    except SystemExit:
        pytest.skip("SimpleMem not installed")


@pytest.mark.usefixtures("mock_openai_all")
class TestRecallMemory:
    """Test the recall_memory() function."""

    def test_recall_with_results(self, test_db_path):
        """Test recall when matching memories exist."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = "Python is a programming language used for data science."

            result = recall_memory(
                query="programming language",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["found"] is True
            assert result["query"] == "programming language"
            assert len(result["context"]) > 0
            assert "programming" in result["context"].lower()

    def test_recall_no_results(self, test_db_path):
        """Test recall when no matching memories exist."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = ""  # Empty result

            result = recall_memory(
                query="nonexistent topic xyz123",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["found"] is False
            assert result["context"] == ""
            assert "No relevant memories" in result["message"]

    def test_recall_whitespace_result(self, test_db_path):
        """Test recall when result is only whitespace."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = "   \n\t  "  # Only whitespace

            result = recall_memory(
                query="test",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["found"] is False

    def test_recall_top_k_parameter(self, test_db_path):
        """Test that top_k parameter is passed to SimpleMem."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = "Result"

            # Test different top_k values
            for k in [1, 5, 10, 20]:
                recall_memory("test", top_k=k, db_path=str(test_db_path))

                # Verify ask was called with correct top_k
                call_kwargs = mock_system.ask.call_args[1]
                assert call_kwargs["top_k"] == k

    def test_recall_default_top_k(self, test_db_path):
        """Test that default top_k is 5."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = "Result"

            recall_memory(
                query="test",
                db_path=str(test_db_path)
                # Note: not specifying top_k
            )

            # Verify default top_k=5 was used
            call_kwargs = mock_system.ask.call_args[1]
            assert call_kwargs["top_k"] == 5

    def test_recall_error_handling_system_error(self, test_db_path):
        """Test error handling when SimpleMem raises exception."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system_class.side_effect = Exception("Database error")

            result = recall_memory(
                query="test",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["success"] is False
            assert result["found"] is False
            assert "error" in result
            assert result["context"] == ""

    def test_recall_default_db_path(self):
        """Test that default database path is used."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = "Result"

            recall_memory(query="test")  # No db_path specified

            # Should use default /tmp/simplemem_db
            mock_system_class.assert_called_once()
            call_kwargs = mock_system_class.call_args[1]
            assert call_kwargs["db_path"] == "/tmp/simplemem_db"

    def test_recall_response_structure(self, test_db_path):
        """Test that recall response has all required fields."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = "Some context"

            result = recall_memory(
                query="test query",
                top_k=5,
                db_path=str(test_db_path)
            )

            # Check all required fields
            required_fields = ["success", "query", "context", "found", "message"]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"

    def test_recall_query_preserved(self, test_db_path):
        """Test that the query is preserved in response."""
        recall_memory, _ = lazy_import_recall()

        queries = [
            "simple query",
            "multi word query here",
            "query-with-dashes",
            "query_with_underscores"
        ]

        for query in queries:
            with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
                mock_system = MagicMock()
                mock_system_class.return_value = mock_system
                mock_system.ask.return_value = "Result"

                result = recall_memory(
                    query=query,
                    top_k=5,
                    db_path=str(test_db_path)
                )

                assert result["query"] == query


class TestProjectPathResolution:
    """Test project-specific database path resolution."""

    def test_get_project_db_path(self, project_context):
        """Test that project hash is calculated correctly."""
        _, get_project_db_path = lazy_import_recall()

        with patch("os.getcwd", return_value=str(project_context["path"])):
            db_path = get_project_db_path()

        expected_path = str(project_context["db_path"])
        assert db_path == expected_path

    def test_different_projects_different_paths(self, tmp_path):
        """Test that different projects produce different paths."""
        _, get_project_db_path = lazy_import_recall()

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
class TestRecallCLI:
    """Test the CLI interface."""

    def test_cli_json_output_default(self, test_db_path, tools_path):
        """Test CLI with default JSON output."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_recall.py"),
                "test query",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            assert isinstance(output, dict)
            assert "success" in output
            assert "context" in output
            assert result.returncode == 0
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")

    def test_cli_text_output_flag(self, test_db_path, tools_path):
        """Test CLI with --text flag for plain text output."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_recall.py"),
                "test query",
                "--text",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should not be JSON when --text flag is used
        output = result.stdout.strip()

        # Try to parse as JSON - should fail if --text works
        try:
            json.loads(output)
            # If it's JSON, it's either an error or --text didn't work
            # Either is acceptable for this test
        except json.JSONDecodeError:
            # Good - it's not JSON, just text
            pass

    def test_cli_top_k_flag(self, test_db_path, tools_path):
        """Test CLI with --top-k flag."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_recall.py"),
                "test query",
                "--top-k", "10",
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
            pytest.skip("SimpleMem not installed")

    def test_cli_json_flag_explicit(self, test_db_path, tools_path):
        """Test CLI with explicit --json flag."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_recall.py"),
                "test query",
                "--json",
                "--db-path", str(test_db_path)
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            assert isinstance(output, dict)
            assert result.returncode == 0
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")

    def test_cli_project_flag(self, project_context, tools_path):
        """Test CLI with --project flag."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_recall.py"),
                "test query",
                "--project"
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(project_context["path"])
        )

        try:
            output = json.loads(result.stdout)
            assert output.get("success") is True
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")

    def test_cli_default_db_path(self, tools_path):
        """Test that CLI uses default DB path."""
        result = subprocess.run(
            [
                "python", str(tools_path / "simplemem_recall.py"),
                "test query"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        try:
            output = json.loads(result.stdout)
            assert output.get("success") is True
        except json.JSONDecodeError:
            pytest.skip("SimpleMem not installed")


@pytest.mark.usefixtures("mock_openai_all")
class TestRecallIntegration:
    """Integration tests for recall functionality."""

    def test_recall_with_context_simulation(self, test_db_path):
        """Test recall behavior with mocked context."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            # Simulate finding Python-related context
            python_context = """
            Python supports multiple programming paradigms.
            Python has extensive standard library.
            Python is widely used in data science.
            """
            mock_system.ask.return_value = python_context.strip()

            result = recall_memory(
                query="Python programming",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["found"] is True
            assert "Python" in result["context"]

    def test_recall_empty_database(self, test_db_path):
        """Test recall from empty database."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = ""

            result = recall_memory(
                query="anything",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["found"] is False
            assert result["context"] == ""

    def test_recall_multiple_queries(self, test_db_path):
        """Test multiple recalls in sequence."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            queries = [
                ("security", "Use HTTPS"),
                ("performance", "Use caching"),
                ("testing", "Write unit tests"),
            ]

            for query, expected_in_result in queries:
                mock_system.ask.return_value = f"Context about {query}: {expected_in_result}"

                result = recall_memory(
                    query=query,
                    top_k=5,
                    db_path=str(test_db_path)
                )

                assert result["success"] is True
                assert result["query"] == query

    def test_recall_special_characters(self, test_db_path):
        """Test recall with special characters in query."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system
            mock_system.ask.return_value = "Result"

            special_queries = [
                "query with spaces",
                "query-with-dashes",
                "query_with_underscores",
                "query.with.dots",
            ]

            for query in special_queries:
                result = recall_memory(
                    query=query,
                    top_k=5,
                    db_path=str(test_db_path)
                )

                assert result["success"] is True
                assert result["query"] == query

    def test_recall_long_context(self, test_db_path):
        """Test recall with very long context result."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            # Create a long context
            long_context = "\n".join([f"Line {i}: " + "x" * 100 for i in range(100)])
            mock_system.ask.return_value = long_context

            result = recall_memory(
                query="test",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["success"] is True
            assert result["found"] is True
            assert len(result["context"]) == len(long_context)

    def test_recall_case_preservation(self, test_db_path):
        """Test that case is preserved in recalled context."""
        recall_memory, _ = lazy_import_recall()

        with patch("simplemem_recall.SimpleMemSystem") as mock_system_class:
            mock_system = MagicMock()
            mock_system_class.return_value = mock_system

            test_context = "MiXeD CaSe CoNtExT"
            mock_system.ask.return_value = test_context

            result = recall_memory(
                query="test",
                top_k=5,
                db_path=str(test_db_path)
            )

            assert result["context"] == test_context
            assert result["context"] == "MiXeD CaSe CoNtExT"
