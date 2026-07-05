# Build Manual

This optional executable packages the Codex-only manual orchestration workflow.
It does not bundle or configure any external model API client.

The source repository should not commit generated executables. Build locally and
attach binaries to GitHub Releases when needed.

## Windows CMD

```cmd
cd path\to\magent\.agents

pip install pyinstaller psutil pyyaml
rmdir /s /q build dist
del /q magent.exe
pyinstaller --clean --noconfirm magent.spec
move dist\magent.exe .
magent.exe version
```

## PowerShell

```powershell
Set-Location path\to\magent\.agents

pip install pyinstaller psutil pyyaml
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item magent.exe -ErrorAction SilentlyContinue
pyinstaller --clean --noconfirm magent.spec
Move-Item dist\magent.exe . -Force
.\magent.exe version
```

## Linux / macOS

```bash
cd .agents
python -m pip install -r ../requirements.txt
python -m pip install pyinstaller
pyinstaller --clean --noconfirm magent.spec
mv dist/magent .
./magent version
```

## Expected Result

```text
Multi-Agent Orchestration Framework
Version: 1.2.0
Mode: Codex-only manual execution
```

## After Build

```cmd
magent.exe ui
magent.exe run --task "analyze code quality" --scope ".agents/scripts"
magent.exe step latest
```

Generated run folders remain local artifacts and should not be committed.
