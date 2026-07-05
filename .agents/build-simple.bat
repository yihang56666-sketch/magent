@echo off
python -m pip install -q pyinstaller psutil pyyaml
python -m PyInstaller --clean --noconfirm magent.spec
if exist dist\magent.exe (
    move /y dist\magent.exe . >nul
    echo Build complete
) else (
    echo Build failed
)
pause
