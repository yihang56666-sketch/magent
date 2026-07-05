@echo off
chcp 65001 >nul
echo Building Codex-only Multi-Agent Framework...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
python -m pip install -q pyinstaller psutil pyyaml
echo Done.

echo [2/4] Cleaning...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist magent.exe del /q magent.exe
echo Done.

echo [3/4] Building executable...
python -m PyInstaller --clean --noconfirm magent.spec
if errorlevel 1 (
    echo BUILD FAILED
    pause
    exit /b 1
)
echo Done.

echo [4/4] Finalizing...
if exist dist\magent.exe (
    move dist\magent.exe . >nul
    echo SUCCESS: magent.exe created
) else (
    echo ERROR: exe not found
    pause
    exit /b 1
)

echo.
echo Testing...
magent.exe version
echo.
echo BUILD COMPLETE!
echo Run: magent.exe ui
echo Then: magent.exe run --task "..." --scope "..."
pause
