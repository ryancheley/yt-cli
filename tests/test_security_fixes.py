"""Regression tests for security findings #740, #741, #742.

Each test fails against the pre-fix code and passes after the fix:
- #740: article attachment download must not honor traversal in the
  server-supplied filename.
- #741: an ``http://`` base URL must emit a cleartext warning.
- #742: the tutorial executor must not run commands through a shell.
"""

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from click.testing import CliRunner

from youtrack_cli.auth import warn_if_insecure_url
from youtrack_cli.commands.articles import download as articles_download
from youtrack_cli.tutorial.executor import ClickCommandExecutor


class TestAttachmentPathTraversal:
    """#740 — server-supplied attachment filename must be sanitized."""

    def _run_download(self, filename: str, tmp_path, monkeypatch):
        # Run with cwd = tmp_path so relative writes land there and persist for
        # the assertions (unlike isolated_filesystem, which deletes on exit).
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_manager = MagicMock()
        mock_manager.download_attachment = AsyncMock(
            return_value={
                "status": "success",
                "data": {
                    "content": b"payload",
                    "filename": filename,
                    "metadata": {"mimeType": "text/plain"},
                },
            }
        )
        with patch("youtrack_cli.articles.ArticleManager", return_value=mock_manager):
            return runner.invoke(articles_download, ["ART-1", "att-1"], obj={"config": {}})

    def test_relative_traversal_stays_in_cwd(self, tmp_path, monkeypatch):
        result = self._run_download("../../pwned", tmp_path, monkeypatch)
        assert result.exit_code == 0, result.output
        # Written under the bare name inside the working directory...
        assert (tmp_path / "pwned").is_file()
        # ...and NOT two directories up, where the raw name would have landed.
        assert not (tmp_path.parent.parent / "pwned").exists()

    def test_absolute_path_is_neutralized(self, tmp_path, monkeypatch):
        # An absolute server filename must not be written to that absolute path.
        target = Path("/tmp/yt_cli_pwned_sentinel")
        if target.exists():
            target.unlink()
        result = self._run_download("/tmp/yt_cli_pwned_sentinel", tmp_path, monkeypatch)
        assert result.exit_code == 0, result.output
        assert not target.exists()
        assert (tmp_path / "yt_cli_pwned_sentinel").is_file()

    def test_normal_filename_unchanged(self, tmp_path, monkeypatch):
        result = self._run_download("report.pdf", tmp_path, monkeypatch)
        assert result.exit_code == 0, result.output
        assert (tmp_path / "report.pdf").is_file()


class TestCleartextUrlWarning:
    """#741 — http:// base URL must warn before the token is sent."""

    def test_http_warns(self):
        with patch("youtrack_cli.auth.get_error_console") as mock_console:
            warn_if_insecure_url("http://youtrack.example.com")
        mock_console.return_value.print.assert_called_once()
        message = mock_console.return_value.print.call_args[0][0]
        assert "cleartext" in message.lower()

    def test_https_does_not_warn(self):
        with patch("youtrack_cli.auth.get_error_console") as mock_console:
            warn_if_insecure_url("https://youtrack.example.com")
        mock_console.return_value.print.assert_not_called()


class TestTutorialExecutorNoShell:
    """#742 — executor must not interpret shell metacharacters."""

    def test_metacharacters_do_not_spawn_secondary_command(self, tmp_path):
        sentinel = tmp_path / "pwned_sentinel"
        # Allowed prefix ("yt --version") followed by a shell injection attempt.
        payload = f"yt --version; touch {sentinel}"
        executor = ClickCommandExecutor()
        # With shell=True this would run `touch <sentinel>`; with exec it is an
        # inert argument to `yt`, so the sentinel must never be created.
        asyncio.run(executor.execute_command(payload, require_confirmation=False))
        assert not sentinel.exists()
        assert not os.path.exists(sentinel)
