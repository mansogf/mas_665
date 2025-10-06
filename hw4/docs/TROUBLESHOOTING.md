# Troubleshooting Guide

## Common Installation Issues

### 1. Python Version Issues

**Problem**: "Python 3.8+ required"
**Solution**: 
- Install Python 3.8-3.12 from [python.org](https://python.org)
- Avoid Python 3.13+ (Kokoro TTS incompatibility)

### 2. Audio Library Issues

**Problem**: "No module named 'sounddevice'"
**Solution**:
```bash
# macOS
brew install portaudio
pip install sounddevice soundfile

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio
pip install sounddevice soundfile

# Windows
pip install pipwin
pipwin install pyaudio
pip install sounddevice soundfile
```

### 3. Kokoro TTS Installation Issues

**Problem**: "Kokoro library not installed"
**Solution**:
```bash
# Install PyTorch first
pip install torch>=2.0.0

# Then install Kokoro
pip install kokoro>=0.7.16

# If still failing, try:
pip install --upgrade pip setuptools wheel
pip install kokoro>=0.7.16 torch numpy
```

### 4. Whisper Model Download Issues

**Problem**: "Model not found" or slow downloads
**Solution**:
```bash
# Pre-download models
python -c "import whisper; whisper.load_model('small')"

# Or use smaller model
export WHISPER_MODEL=tiny
```

## Runtime Issues

### 1. Audio Device Not Found

**Problem**: "No audio device found"
**Solution**:
```bash
# List available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Set specific device in .env
INPUT_DEVICE=1
OUTPUT_DEVICE=2
```

### 2. Poor Speech Recognition

**Problem**: "I could not understand anything"
**Solutions**:
- Speak clearly and close to microphone
- Check microphone permissions
- Try different Whisper models:
  ```bash
  export WHISPER_MODEL=base  # or medium, large
  ```
- Increase recording time:
  ```bash
  export VOICE_RECORD_SECONDS=8.0
  ```

### 3. API Key Issues

**Problem**: "No LLM providers available"
**Solutions**:
- Check OpenAI API key in `.env`
- Verify API key has credits
- Test API key:
  ```bash
  python -c "import openai; print(openai.api_key)"
  ```
- Use Ollama fallback:
  ```bash
  # Install Ollama
  curl -fsSL https://ollama.ai/install.sh | sh
  
  # Pull model
  ollama pull llama3:8b
  ```

### 4. Kokoro TTS Issues

**Problem**: "Kokoro TTS not available" or "Kokoro library not installed"
**Solutions**:
- **Critical**: Kokoro TTS is required for voice interaction
- Install Kokoro TTS:
  ```bash
  pip install kokoro>=0.7.16 torch
  ```
- No fallback TTS option available
- Ensure Python version is <3.13

### 5. Memory Issues

**Problem**: "Out of memory" or slow performance
**Solutions**:
- Use smaller Whisper model:
  ```bash
  export WHISPER_MODEL=tiny
  ```
- Close other applications
- Use CPU-only mode:
  ```bash
  export CUDA_VISIBLE_DEVICES=""
  ```

## Platform-Specific Issues

### macOS

**Problem**: Microphone permissions
**Solution**: 
- System Preferences → Security & Privacy → Microphone
- Allow Terminal/Python access

**Problem**: Kokoro TTS not working
**Solution**:
```bash
# Test Kokoro TTS
python gabriel.py  # Choose option 6
```

### Linux

**Problem**: Audio system not working
**Solution**:
```bash
# Install ALSA development libraries
sudo apt-get install libasound2-dev

# Test audio
aplay /usr/share/sounds/alsa/Front_Left.wav
```

### Windows

**Problem**: Kokoro TTS installation fails
**Solution**:
```bash
# Install Visual C++ Build Tools first
# Then:
pip install kokoro>=0.7.16 torch
```

**Problem**: Audio device access denied
**Solution**:
- Check Windows audio permissions
- Run as administrator if needed

## Performance Optimization

### 1. Faster Startup
```bash
# Use smaller models
export WHISPER_MODEL=tiny
```

### 2. Better Quality
```bash
# Use larger models
export WHISPER_MODEL=large
```

### 3. Memory Optimization
```bash
# Disable GPU if causing issues
export CUDA_VISIBLE_DEVICES=""

# Use CPU-only PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Getting Help

1. **Check logs**: Look for error messages in terminal output
2. **Test components**: Use individual test functions (options 5-7)
3. **Verify setup**: Run system tests (option 2)
4. **Check dependencies**: Ensure all packages are installed
5. **Review configuration**: Verify `.env` file settings

## Emergency Fallbacks

If nothing works:

1. **Text-only mode**: Use option 1 (Gabriel Chat)
2. **Ollama only**: Remove OpenAI API key
3. **Minimal setup**: Use `WHISPER_MODEL=tiny`
4. **Install Kokoro TTS**: Required for voice interaction

## Still Having Issues?

1. Check the main README.md
2. Review the technical write-up
3. Test with minimal configuration
4. Check system requirements
5. Verify all dependencies are installed
