@echo off
REM Development Environment Setup Script for SMTPHub
REM This script sets up virtual environment, git, and other development dependencies

setlocal enabledelayedexpansion

echo.
echo ========================================
echo SMTPHub Development Environment Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.x from https://www.python.org/downloads/
    exit /b 1
)
echo [OK] Python found: 
python --version

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Git is not installed or not in PATH
    echo You can install it from https://git-scm.com/download/win
    echo Continuing without git initialization...
) else (
    echo [OK] Git found:
    git --version
)

echo.
echo [1/5] Creating Python virtual environment...
if exist .venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)
echo [OK] Virtual environment activated

echo.
echo [3/5] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip components, continuing...
)

echo.
echo [4/5] Installing project dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARNING] Some dependencies may have failed to install
    ) else (
        echo [OK] Dependencies installed successfully
    )
) else (
    echo [WARNING] requirements.txt not found, skipping dependency installation
)

echo.
echo [5/5] Initializing Git repository...
if exist .git (
    echo Git repository already exists, skipping...
) else (
    git init
    if errorlevel 1 (
        echo [WARNING] Git not installed, skipping git initialization
    ) else (
        echo [OK] Git repository initialized
    fi
)

REM Create .gitignore if it doesn't exist
if not exist .gitignore (
    echo Creating .gitignore...
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo .venv/
        echo ENV/
        echo env/
        echo build/
        echo develop-eggs/
        echo dist/
        echo downloads/
        echo eggs/
        echo .eggs/
        echo lib/
        echo lib64/
        echo parts/
        echo sdist/
        echo var/
        echo wheels/
        echo *.egg-info/
        echo .installed.cfg
        echo *.egg
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo *~
        echo .DS_Store
        echo.
        echo # Environment
        echo .env
        echo .env.local
        echo.
        echo # Docker
        echo docker-compose.override.yml
    ) > .gitignore
    echo [OK] .gitignore created
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Virtual environment is ready. To activate it:
echo    .venv\Scripts\activate.bat
echo.
echo 2. To deactivate the virtual environment:
echo    deactivate
echo.
echo 3. If git was initialized, configure your user info:
echo    git config user.name "Your Name"
echo    git config user.email "your.email@example.com"
echo.
echo 4. Add files to git:
echo    git add .
echo    git commit -m "Initial commit"
echo.
echo Happy coding!
echo.

endlocal
