@echo off
echo ============================================
echo   KZA Doelen AI Dashboard starten...
echo ============================================
echo.

:: Controleer of Python beschikbaar is
python --version >nul 2>&1
if errorlevel 1 (
    echo FOUT: Python is niet gevonden. Installeer Python via https://python.org
    pause
    exit /b 1
)

:: Installeer benodigde pakketten als ze ontbreken
echo Benodigde pakketten installeren (eenmalig)...
pip install streamlit pandas plotly --quiet

echo.
echo Dashboard openen in browser...
echo Sluit dit venster om het dashboard te stoppen.
echo.

:: Start Streamlit
streamlit run "%~dp0kza_dashboard.py" --server.headless false --browser.gatherUsageStats false

pause
