@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Rebuilding exe...
python -m PyInstaller --clean --noconfirm magent.spec
if exist dist\magent.exe (
    move /y dist\magent.exe . >nul
    echo SUCCESS: magent.exe updated
    magent.exe version
) else (
    echo ERROR: Build failed
)
pause
