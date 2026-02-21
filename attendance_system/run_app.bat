@echo off
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
)

REM Install dependencies
call venv\Scripts\pip install -r requirements.txt

REM Run the app
call venv\Scripts\python app.py
