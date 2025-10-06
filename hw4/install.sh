#!/bin/bash

# Gabriel Manso AI - Installation Script
# This script helps set up the voice interaction system

set -e  # Exit on any error

echo "🇧🇷 Gabriel Manso AI - Installation Script"
echo "=========================================="

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected (>= $required_version required)"
else
    echo "❌ Python $required_version or higher required. Found: $python_version"
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
echo "🔧 Checking configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your API keys:"
        echo "   - OPENAI_API_KEY"
        echo "   - SERPER_API_KEY"
    else
        echo "⚠️  No .env file found. Please create one with your API keys."
    fi
else
    echo "✅ .env file found"
fi

# Test basic imports
echo "🧪 Testing basic imports..."
python3 -c "
try:
    import crewai
    import openai
    import sounddevice
    import soundfile
    import whisper
    print('✅ Core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test Kokoro TTS (required)
echo "🎤 Testing Kokoro TTS..."
python3 -c "
try:
    from kokoro import KPipeline
    print('✅ Kokoro TTS available')
except ImportError:
    print('❌ Kokoro TTS not available (REQUIRED for voice interaction)')
    print('💡 Install with: pip install kokoro>=0.7.16 torch')
    exit(1)
"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python gabriel.py"
echo "3. Choose option 2 to run system tests"
echo ""
echo "For help, see README.md"
