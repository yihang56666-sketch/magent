@echo off
chcp 65001 >nul
echo Rebuilding with auto-launch UI...
python -m PyInstaller --clean --noconfirm magent.spec
if exist dist\magent.exe (
    move /y dist\magent.exe . >nul
    echo.
    echo SUCCESS: magent.exe ready!
    echo.
    echo Usage:
    echo   Double-click magent.exe = Auto launch Dashboard
    echo   magent.exe run --task "..." --scope "..." = Execute task
    echo.
) else (
    echo FAILED
)
pause
