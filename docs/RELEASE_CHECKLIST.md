# Release Checklist

Use this checklist before publishing the project to GitHub or cutting a tagged
release.

## Source hygiene

- [ ] `python scripts/doctor.py` exits with `Result: ready`.
- [ ] `python scripts/maturity_audit.py` exits with no blockers.
- [ ] `python scripts/clean.py --runs --apply` has removed local generated artifacts when preparing a clean release commit.
- [ ] No large generated artifacts are staged.
- [ ] `.gitattributes` is present so cross-platform line endings stay predictable.
- [ ] `.agents/build/`, `.agents/dist/`, `.agents/*.exe`, `__pycache__/`, and
      `.pytest_cache/` remain ignored.
- [ ] Generated run folders under `.agents/reports/runs/` are not committed
      except `.gitkeep`.
- [ ] Example files contain no private task data, secrets, or real customer
      context.

## Verification

- [ ] `python scripts/verify.py` passes locally.
- [ ] GitHub Actions CI passes on all supported Python versions.
- [ ] `python .agents/magent.py run --task "..." --scope "..."` creates a run.
- [ ] `python .agents/magent.py step latest` refreshes summary state and shows a copyable packet.

## Documentation

- [ ] README explains what the project does in the first screen.
- [ ] `docs/GETTING_STARTED.md` works from a fresh checkout.
- [ ] `docs/USER_GUIDE.md` covers the normal workflow.
- [ ] `docs/ARCHITECTURE.md` matches the current runtime.
- [ ] `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md` are present.
- [ ] GitHub issue templates point users to the right information.

## GitHub setup

- [ ] Initialize the local repository if needed: `git init`.
- [ ] Create a source-only initial commit before publishing.
- [ ] Review ignored files with `git status --ignored`.
- [ ] Create the first commit from source files only.
- [ ] Create a GitHub repository and push after explicit owner approval.
- [ ] Add repository URL, badges, and project homepage links after the first push if desired.
- [ ] Add repository topics such as `codex`, `multi-agent`, `agent-workflow`,
      and `developer-tools`.

## Optional binary release

The source repository should not commit built executables. For a binary release:

- [ ] Build locally from `.agents/` with `build.bat` or `./build.sh`.
- [ ] Attach the artifact to a GitHub Release.
- [ ] Include checksums and the source commit SHA.
- [ ] Confirm the binary starts with `magent version`.
