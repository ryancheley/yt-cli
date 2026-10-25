# Release Checklist

Step-by-step for cutting a new release. The `just release` recipe enforces most
of the pre-flight checks and aborts if any fail, but do the prep first so the
run doesn't bail partway through.

## 1. Pick the version

SemVer, pre-1.0 rules (`0.MINOR.PATCH`):

- **PATCH** (`0.26.0 → 0.26.1`) — bug fixes only, no behavior removed.
- **MINOR** (`0.26.0 → 0.27.0`) — new features **or anything backward-incompatible**
  (e.g. dropping a Python version / raising `requires-python`).

Check what's unreleased before deciding:

```bash
just release-status        # shows whether there are unreleased changes
git log --oneline v<LAST>..HEAD
```

## 2. Prep the CHANGELOG (via a PR — never edit main directly)

The release recipe requires a header matching the version exactly:
`## [X.Y.Z] - YYYY-MM-DD`.

```bash
git checkout -b changelog-X.Y.Z
# edit CHANGELOG.md: set the unreleased section's header to
#   ## [X.Y.Z] - <today>
pre-commit run --all-files
git commit -m "📝 docs: ..."       # emoji-first
git push -u origin changelog-X.Y.Z
gh pr create --title "..." --body "..."
```

Wait for **all** checks to pass (never bypass), then:

```bash
gh pr checks <PR#> --watch
gh pr merge <PR#> --squash --delete-branch
git checkout main && git pull origin main
```

## 3. Cut the release

Pre-flight you can run first (optional):

```bash
just release-check X.Y.Z     # validates version format + increment, no tag exists
```

Then, from a clean `main` up to date with origin:

```bash
just release X.Y.Z
```

This runs quality checks (`just check`), bumps the version in `pyproject.toml`,
updates `uv.lock`, commits, pushes the commit to `main`, then creates and pushes
the `vX.Y.Z` tag (with automatic rollback if the push fails).

> Note: the version-bump commit pushes directly to `main` and bypasses branch
> protection — this is by design and is the only sanctioned direct-to-main push.

## 4. Verify

Pushing the tag triggers `release.yml`, which tests, builds, publishes to Test
PyPI + PyPI (trusted publishers, no tokens), and creates the GitHub release.

```bash
gh run watch $(gh run list --workflow=release.yml --limit 1 --json databaseId -q '.[0].databaseId') --exit-status
gh release view vX.Y.Z
git pull origin main        # pull the version-bump commit locally
```

Confirm the package shows up at `https://pypi.org/project/youtrack-cli/X.Y.Z/`.

## If something breaks

```bash
just rollback-release X.Y.Z
```

⚠️ Rollback **cannot** undo a PyPI publish. If the package already shipped,
bump to a new version and release again.
