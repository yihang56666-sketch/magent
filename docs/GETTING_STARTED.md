# Getting Started

This guide takes a new user from a fresh checkout to their first completed
manual multi-agent run.

## 1. Install

Use Python 3.10 or newer.

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

## 2. Check the checkout

```bash
python scripts/doctor.py
python scripts/maturity_audit.py
```

The doctor checks required files, importable dependencies, Python version, and
large generated artifacts that should stay out of source commits.

## 3. Run the test suite

```bash
python scripts/verify.py
```

This runs the identity validator, pytest suite, project doctor, and CLI smoke
test.

## 4. Pick a practical recipe

Before creating a run, ask whether a multi-agent workflow is worth the manual
overhead:

```bash
python .agents/magent.py advise --scope "src/auth tests/auth" --task "login returns 500 after password reset"
```

```bash
python .agents/magent.py recipes
```

Recipes are the recommended starting point because they define useful outcomes
for common jobs.

## 5. Create a run

```bash
python .agents/magent.py start bugfix --scope "src/auth tests/auth" --task "login returns 500 after password reset"
```

The command creates a local folder under `.agents/reports/runs/<run-id>/`.

## 6. Work through agents manually

```bash
python .agents/magent.py step latest
```

Copy the packet into the current Codex session, answer it as the bounded agent,
and save the final answer into the matching `*.output.md` file in the run
folder.

After each answer:

```bash
python .agents/magent.py step latest
```

## 7. Merge the results

When all agents are complete:

```bash
python .agents/scripts/merge-results.py .agents/reports/runs/<run-id>
```

The merged `synthesis.md` is advisory evidence for the main Codex session. The
main agent still owns final decisions, edits, verification claims, and user
communication.
