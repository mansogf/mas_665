@echo off
REM Gabriel Manso AI - Installation Script for Windows
REM This script helps set up the voice interaction system

echo 🇧🇷 Gabriel Manso AI - Installation Script
echo ==========================================

REM Check Python version
echo 🐍 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python %python_version% detected

REM Create virtual environment
echo 📦 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check for .env file
echo 🔧 Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 Creating .env file from template...
        copy .env.example .env
        echo ⚠️  Please edit .env file with your API keys:
        echo    - OPENAI_API_KEY
        echo    - SERPER_API_KEY
    ) else (
        echo ⚠️  No .env file found. Please create one with your API keys.
    )
) else (
    echo ✅ .env file found
)

REM Test basic imports
echo 🧪 Testing basic imports...
python -c "try: import crewai, openai, sounddevice, soundfile, whisper; print('✅ Core dependencies imported successfully'); except ImportError as e: print(f'❌ Import error: {e}'); exit(1)"

REM Test Kokoro TTS (required)
echo 🎤 Testing Kokoro TTS...
python -c "try: from kokoro import KPipeline; print('✅ Kokoro TTS available'); except ImportError: print('❌ Kokoro TTS not available (REQUIRED for voice interaction)'); print('💡 Install with: pip install kokoro>=0.7.16 torch'); exit(1)"

echo.
echo 🎉 Installation complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: python gabriel.py
echo 3. Choose option 2 to run system tests
echo.
echo For help, see README.md
pause
