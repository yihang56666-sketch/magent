@echo off
echo Checking if UI files are bundled in exe...
echo.

echo Running: magent.exe ui --no-browser
echo.
echo If you see "Starting dashboard on port 8080", UI files are bundled!
echo Then manually open: http://localhost:8080/dashboard.html
echo.
timeout /t 2 /nobreak >nul

start /b magent.exe ui --no-browser

timeout /t 3 /nobreak >nul

echo.
echo Opening browser...
start http://localhost:8080/dashboard.html

echo.
echo Press any key to stop server...
pause >nul
taskkill /f /im magent.exe >nul 2>&1
