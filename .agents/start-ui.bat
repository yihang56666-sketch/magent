@echo off
chcp 65001 >nul
echo Starting Dashboard...
echo.
echo Opening browser at http://localhost:8080/dashboard.html
echo Press Ctrl+C to stop
echo.
magent.exe ui
