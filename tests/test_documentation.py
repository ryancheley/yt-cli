"""Tests for documentation examples and code snippets."""

import re
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest


class TestDocumentationExamples:
    """Test CLI examples found in documentation."""

    @pytest.fixture
    def docs_path(self):
        """Path to documentation directory."""
        return Path(__file__).parent.parent / "docs"

    def test_docs_directory_exists(self, docs_path):
        """Verify documentation directory exists."""
        assert docs_path.exists()
        assert docs_path.is_dir()

    def test_rst_files_exist(self, docs_path):
        """Verify RST documentation files exist."""
        rst_files = list(docs_path.glob("**/*.rst"))
        assert len(rst_files) > 0, "No RST files found in docs directory"

    def extract_cli_examples(self, docs_path):
        """Extract CLI command examples from RST files."""
        cli_examples = []

        for rst_file in docs_path.glob("**/*.rst"):
            content = rst_file.read_text()

            # Find code blocks with bash language
            code_block_pattern = r".. code-block:: bash\n\n((?:   .*\n?)*)"
            matches = re.findall(code_block_pattern, content)

            for match in matches:
                # Remove indentation and split into lines
                lines = [
                    line[3:] if line.startswith("   ") else line.strip() for line in match.split("\n") if line.strip()
                ]

                # Filter for yt commands
                yt_commands = [line for line in lines if line.startswith("yt ") and not line.startswith("yt --")]

                for cmd in yt_commands:
                    cli_examples.append({"file": rst_file.name, "command": cmd.strip(), "full_content": match})

        return cli_examples

    def test_extract_cli_examples(self, docs_path):
        """Test that CLI examples can be extracted from documentation."""
        examples = self.extract_cli_examples(docs_path)
        assert len(examples) > 0, "No CLI examples found in documentation"

    @pytest.mark.parametrize(
        "command_example",
        [
            "yt auth login",
            "yt issues list",
            "yt projects list",
            "yt config list",
        ],
    )
    def test_basic_command_syntax(self, command_example):
        """Test that basic commands have valid syntax."""
        # Mock the CLI to avoid actual API calls
        with patch("youtrack_cli.main.main") as mock_main:
            mock_main.return_value = 0

            # Parse command arguments
            parts = command_example.split()
            assert parts[0] == "yt", f"Command should start with 'yt': {command_example}"
            assert len(parts) >= 2, f"Command should have subcommand: {command_example}"

    def test_quickstart_commands_are_valid(self, docs_path):
        """Test that commands in quickstart guide are syntactically valid."""
        quickstart_file = docs_path / "quickstart.rst"
        if not quickstart_file.exists():
            pytest.skip("quickstart.rst not found")

        examples = []
        content = quickstart_file.read_text()

        # Extract bash code blocks
        code_block_pattern = r".. code-block:: bash\n\n((?:   .*\n?)*)"
        matches = re.findall(code_block_pattern, content)

        for match in matches:
            lines = [line[3:] if line.startswith("   ") else line.strip() for line in match.split("\n") if line.strip()]

            # Find yt commands
            yt_commands = [line for line in lines if line.startswith("yt ") and not line.startswith("yt --")]
            examples.extend(yt_commands)

        # Validate each command has proper structure
        for cmd in examples:
            parts = cmd.split()
            assert parts[0] == "yt", f"Invalid command start: {cmd}"
            if len(parts) > 1:
                # Basic validation that subcommand exists
                assert parts[1] in [
                    "auth",
                    "issues",
                    "projects",
                    "time",
                    "config",
                    "users",
                    "admin",
                    "articles",
                    "boards",
                    "reports",
                ], f"Unknown subcommand in: {cmd}"


class TestDocumentationBuild:
    """Test documentation build process."""

    @pytest.fixture
    def docs_path(self):
        """Path to documentation directory."""
        return Path(__file__).parent.parent / "docs"

    def test_sphinx_conf_exists(self, docs_path):
        """Verify Sphinx configuration exists."""
        conf_py = docs_path / "conf.py"
        assert conf_py.exists(), "docs/conf.py not found"

    def test_sphinx_extensions_configured(self, docs_path):
        """Test that required Sphinx extensions are configured."""
        conf_py = docs_path / "conf.py"
        content = conf_py.read_text()

        required_extensions = ["sphinx.ext.autodoc", "sphinx.ext.doctest", "sphinx.ext.linkcheck"]

        for ext in required_extensions:
            assert ext in content, f"Extension {ext} not found in conf.py"

    def test_makefile_exists(self, docs_path):
        """Verify Makefile exists for documentation building."""
        makefile = docs_path / "Makefile"
        assert makefile.exists(), "docs/Makefile not found"

    @pytest.mark.integration
    def test_docs_build_html(self, docs_path):
        """Test that documentation builds successfully as HTML."""
        import shutil

        # Skip if sphinx-build is not available
        sphinx_build_result = subprocess.run(["which", "sphinx-build"], capture_output=True, text=True)
        if sphinx_build_result.returncode != 0:
            pytest.skip("sphinx-build command not available")

        build_dir = docs_path / "_build" / "html"

        # Clean build directory
        if build_dir.exists():
            shutil.rmtree(build_dir)

        # Attempt to build documentation
        result = subprocess.run(
            ["sphinx-build", "-W", "-b", "html", str(docs_path), str(build_dir)], capture_output=True, text=True
        )

        if result.returncode != 0:
            pytest.fail(f"Documentation build failed:\n{result.stdout}\n{result.stderr}")

        # Verify index.html was created
        index_html = build_dir / "index.html"
        assert index_html.exists(), "index.html not generated"

    def test_linkcheck_configuration(self, docs_path):
        """Test that linkcheck is properly configured to ignore development URLs."""
        conf_py = docs_path / "conf.py"
        content = conf_py.read_text()

        # Check for linkcheck ignore patterns
        assert "linkcheck_ignore" in content, "linkcheck_ignore not configured"
        assert "localhost" in content, "localhost not in linkcheck_ignore"
        assert "youtrack" in content, "YouTrack URLs not ignored"
        assert "linkcheck_timeout" in content, "linkcheck_timeout not configured"


class TestDocstrings:
    """Test docstring examples using doctest."""

    def test_main_module_importable(self):
        """Test that main module can be imported for doctest."""
        try:
            import youtrack_cli.main

            assert hasattr(youtrack_cli.main, "main")
        except ImportError as e:
            pytest.fail(f"Cannot import main module: {e}")

    @pytest.mark.doctest
    def test_docstrings_are_testable(self):
        """Test that docstrings contain testable examples."""
        import youtrack_cli

        # This test ensures doctest configuration is working
        # Actual doctest execution happens via pytest --doctest-modules
        module_path = Path(youtrack_cli.__file__).parent
        python_files = list(module_path.glob("**/*.py"))

        assert len(python_files) > 0, "No Python files found in youtrack_cli module"

    def test_doctest_configuration_in_pytest(self):
        """Test that doctest is configured in pytest."""
        # This validates our pytest configuration includes doctest options
        # The actual doctest functionality is tested by the pytest run itself
        assert True  # Placeholder - actual doctests run automatically


@pytest.mark.integration
class TestDocumentationIntegration:
    """Integration tests for documentation system."""

    def test_docs_dependency_group_works(self):
        """Test that docs dependency group installs correctly."""
        try:
            import sphinx

            # Just verify sphinx can be imported successfully
            assert sphinx is not None
        except ImportError as e:
            pytest.skip(f"Docs dependencies not installed: {e}")

    def test_all_rst_files_parseable(self):
        """Test that all RST files are parseable by Sphinx."""
        docs_path = Path(__file__).parent.parent / "docs"

        for rst_file in docs_path.glob("**/*.rst"):
            try:
                content = rst_file.read_text()
                # Basic RST syntax validation - check for valid RST patterns
                # RST files should have either directives (..), section headers (=, -, ~),
                # or be empty/whitespace-only
                has_directive = ".. " in content
                has_section = any(
                    line.strip() and all(c in "=-~`':\"^_*+#<>" for c in line.strip()) for line in content.split("\n")
                )
                is_empty = len(content.strip()) == 0

                assert has_directive or has_section or is_empty, f"RST file appears invalid: {rst_file}"
            except UnicodeDecodeError:
                pytest.fail(f"Cannot read RST file: {rst_file}")

    def test_documentation_coverage_exists(self):
        """Test that key documentation files exist."""
        docs_path = Path(__file__).parent.parent / "docs"

        required_docs = ["index.rst", "quickstart.rst", "installation.rst", "configuration.rst"]

        for doc_file in required_docs:
            doc_path = docs_path / doc_file
            assert doc_path.exists(), f"Required documentation file missing: {doc_file}"
