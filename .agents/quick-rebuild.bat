@echo off
chcp 65001 >nul
echo Quick rebuild...
python -m PyInstaller --clean --noconfirm magent.spec
if exist dist\magent.exe (
    move /y dist\magent.exe . >nul
    echo SUCCESS
    echo.
    echo Testing UI bundle...
    magent.exe ui --no-browser &
    timeout /t 2 /nobreak >nul
    curl -s http://localhost:8080/dashboard.html >nul 2>&1 && echo UI accessible! || echo UI not found
    taskkill /f /im magent.exe >nul 2>&1
) else (
    echo FAILED
)
