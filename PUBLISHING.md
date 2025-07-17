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

**Automated Release Process (Recommended)**

Use the automated release command that includes comprehensive validation:

```bash
just release 0.1.1
```

This command will:
1. **Pre-flight checks**:
   - Verify you're on the main branch
   - Ensure working directory is clean
   - Check synchronization with remote
   - Validate GitHub authentication
   - Run all quality checks (linting, formatting, type checking, tests, security)

2. **Version management**:
   - Update version in `pyproject.toml`
   - Update `uv.lock` file
   - Create version bump commit

3. **Safe publication**:
   - Push version bump commit with validation
   - Verify commit was successfully pushed to remote
   - Create and push release tag with validation
   - Automatic rollback on any failure

4. **GitHub Actions** will then automatically:
   - Run tests
   - Build the package
   - Publish to Test PyPI (if configured)
   - Publish to PyPI (if configured)
   - Create a GitHub release

**Manual Release Process**

If you prefer to handle the process manually:

1. Update version in `pyproject.toml`
2. Create and push a git tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

**Release Validation**

Before releasing, you can validate the release:

```bash
just release-check 0.1.1
```

**Emergency Rollback**

If a release fails or needs to be rolled back:

```bash
just rollback-release 0.1.1
```

⚠️ **Note**: Rollback cannot undo PyPI publications. If the package was already published to PyPI, you'll need to create a new version.

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
