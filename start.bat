@echo off
echo 🚀 Starting LeadBot Pro...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
pip install -r requirements.txt

REM Start the server
python -m app.main

pause