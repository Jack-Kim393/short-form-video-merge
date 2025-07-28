@echo off
chcp 65001 > nul
echo --- Shortform Video Editor Setup & Launch ---

ECHO.
echo [Step 1/5] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed.
    echo Please install Python 3 from python.org and ensure it's added to your PATH.
    pause
    exit /b
)
python --version

ECHO.
echo [Step 2/5] Setting up a clean virtual environment...
if exist .venv (
    echo Removing old virtual environment.
    rmdir /s /q .venv
)
python -m venv .venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment.
    pause
    exit /b
)
echo Virtual environment created successfully.

ECHO.
echo [Step 3/5] Installing required libraries...
.venv\Scripts\python.exe -m pip install --upgrade pip > nul
.venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install libraries from requirements.txt.
    echo Please check your internet connection and the console output above for errors.
    pause
    exit /b
)
echo Libraries installed.

ECHO.
echo [Step 4/5] Verifying library installation...
echo --- Installed Packages List ---
.venv\Scripts\pip.exe freeze
echo -----------------------------

ECHO.
echo Attempting to import 'moviepy.editor' directly...
.venv\Scripts\python.exe -c "import moviepy.editor"
if %errorlevel% neq 0 (
    ECHO.
    echo Error: Verification FAILED. The 'moviepy' library could not be imported.
    echo The installation appears to be broken. Please review the installation logs above.
    pause
    exit /b
)
echo Verification successful! 'moviepy' is installed correctly.

ECHO.
echo [Step 5/5] Starting the application...
echo Your web browser will open with the application shortly.
.venv\Scripts\streamlit.exe run app.py

ECHO.
echo Application has been closed. Exiting script.
pause
