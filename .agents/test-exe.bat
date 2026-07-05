@echo off
chcp 65001 >nul
echo Testing magent.exe...
echo.

echo [1] Check file exists:
if exist magent.exe (
    echo    OK: magent.exe found
    dir magent.exe | find "magent.exe"
) else (
    echo    ERROR: magent.exe not found
    pause
    exit /b 1
)

echo.
echo [2] Test version command:
magent.exe version 2>&1
if errorlevel 1 (
    echo    ERROR: Failed to run
) else (
    echo    OK: Version works
)

echo.
echo [3] Test help command:
magent.exe --help 2>&1

echo.
echo [4] Test config command:
magent.exe config get 2>&1

echo.
pause
