@echo off
echo Starting BookBot 06...
cd /d "%~dp0"
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment. Make sure 'venv' exists in %cd%
    pause
    exit /b 1
)
streamlit run app.py
pause
