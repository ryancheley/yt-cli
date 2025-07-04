# Publishing Setup

This project uses trusted publishers for secure PyPI publishing without API tokens.

## Trusted Publisher Configuration

### PyPI (Production)
- URL: https://pypi.org/manage/account/publishing/
- Project name: `youtrack-cli`
- Owner: `ryancheley`
- Repository: `yt-cli`
- Workflow: `release.yml`
- Environment: PyPI

### Test PyPI (Testing)
- URL: https://test.pypi.org/manage/account/publishing/
- Project name: `youtrack-cli`
- Owner: `ryancheley`
- Repository: `yt-cli`
- Workflow: `release.yml`
- Environment: TestPyPI

## Creating a Release

1. Update version in `pyproject.toml`
2. Create and push a git tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```
3. GitHub Actions will automatically:
   - Run tests
   - Build the package
   - Publish to Test PyPI (if configured)
   - Publish to PyPI (if configured)
   - Create a GitHub release

## Benefits of Trusted Publishing

- ✅ No API tokens to manage or rotate
- ✅ More secure OIDC-based authentication
- ✅ Automatic token generation per publish
- ✅ Reduced attack surface
- ✅ PyPI best practice recommendation

## Security

The workflow uses:
- `id-token: write` permission for OIDC
- `contents: write` for GitHub releases
- No stored secrets required
