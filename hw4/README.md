# Gabriel Manso AI - Voice Interaction System

A sophisticated AI assistant that combines speech-to-text, natural language processing, and text-to-speech technologies to create natural voice conversations. Built with CrewAI framework and featuring multiple specialized agents representing different aspects of Gabriel's persona.

## 🎯 Features

- **Voice Interaction**: Full voice-to-voice conversation using Whisper STT and Kokoro TTS
- **Multi-Agent System**: Specialized agents for different conversation types
- **Research Capabilities**: Real-time web search and information synthesis
- **Music Recommendations**: Curated music suggestions based on preferences
- **Cross-Platform Support**: Works on macOS, Linux, and Windows
- **Fallback Systems**: Graceful degradation when components are unavailable

## 🚀 Quick Start

### Prerequisites

- **Python 3.8-3.12** (Kokoro TTS requires Python <3.13)
- **Microphone and speakers** for voice interaction
- **Internet connection** for AI models and web search
- **OpenAI API key** (recommended) or **Ollama** (fallback)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mas_665/hw4
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # Create from template if available
   ```
   
   Or create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   WHISPER_MODEL=small
   USE_KOKORO_TTS=true
   TTS_VOICE=am_puck
   TTS_RATE=175
   VOICE_RECORD_SECONDS=6.0
   ```

## 🔧 Configuration

### Required API Keys

1. **OpenAI API Key** (Primary LLM)
   - Get from: https://platform.openai.com/api-keys
   - Required for GPT-4o-mini access

2. **Serper API Key** (Web Search)
   - Get from: https://serper.dev/
   - Required for research capabilities

### Optional Configuration

- **Ollama** (Fallback LLM)
  - Install: https://ollama.ai/
  - Pull model: `ollama pull llama3:8b`

### Audio Configuration

The system automatically detects your audio devices. For manual configuration:

```bash
# List available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Set device IDs in your `.env`:
```env
INPUT_DEVICE=1
OUTPUT_DEVICE=2
```

## 🎮 Usage

### Interactive Menu

Run the main script to access the interactive menu:

```bash
python gabriel.py
```

Choose from:
1. **Gabriel Chat** - Text-based conversation
2. **System Tests** - Verify installation
3. **Single Response** - One-time query
4. **Voice Chat** - Full voice interaction (Kokoro TTS)
5. **STT Check** - Test speech recognition
6. **Kokoro TTS Check** - Test high-quality TTS

### Voice Commands

During voice chat, you can:
- **Press Enter**: Record voice message (6 seconds default)
- **Type "text"**: Switch to text input
- **Type "quit"**: Exit voice chat

### Special Commands

- `intro` - Gabriel's introduction
- `quit` - Exit the system

## 🏗️ Architecture

### Core Components

```
VoiceInteractionSession
├── AudioInterface (recording/playback)
├── SpeechToTextEngine (Whisper)
├── TextToSpeechEngine (Kokoro/System)
└── GabrielCrewAI (AI agents)
    ├── Personal Assistant Agent
    ├── Research Synthesizer Agent
    └── Music Curator Agent
```

### Technology Stack

- **STT**: OpenAI Whisper (configurable model sizes)
- **TTS**: Kokoro TTS (high-quality neural voice synthesis)
- **LLM**: OpenAI GPT-4o-mini (primary) + Ollama (fallback)
- **Framework**: CrewAI for multi-agent orchestration
- **Audio**: sounddevice, soundfile for real-time processing

## 🔍 Troubleshooting

### Common Issues

1. **"Recording requires sounddevice and soundfile"**
   ```bash
   pip install sounddevice soundfile
   ```

2. **"Kokoro library not installed"**
   ```bash
   pip install kokoro>=0.7.16 torch
   ```
   **Note**: Kokoro TTS is required for voice interaction. There is no fallback TTS option.

3. **"No LLM providers available"**
   - Check your OpenAI API key
   - Or install Ollama: `ollama pull llama3:8b`

4. **Audio device not found**
   ```bash
   # Test audio devices
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

5. **Poor speech recognition**
   - Speak clearly and close to microphone
   - Check microphone permissions
   - Try different Whisper models (tiny, base, small, medium, large)

### Performance Optimization

- **Faster STT**: Use `WHISPER_MODEL=tiny` for speed
- **Better STT**: Use `WHISPER_MODEL=large` for accuracy
- **Memory usage**: Smaller models use less RAM
- **GPU acceleration**: Automatically detected for Whisper

### Platform-Specific Notes

#### macOS
- May require microphone permissions in System Preferences
- Kokoro TTS provides high-quality voice synthesis

#### Linux
- Install audio development libraries:
  ```bash
  sudo apt-get install portaudio19-dev python3-pyaudio
  ```

#### Windows
- May require Visual C++ Build Tools for some dependencies
- Kokoro TTS works natively on Windows

## 📁 Project Structure

```
hw4/
├── gabriel.py              # Main application
├── requirements.txt        # Dependencies
├── README.md              # This file
├── voice_interaction_writeup.md  # Technical documentation
├── voice_artifacts/       # Temporary audio files
│   ├── *.wav             # Generated audio files
└── docs/                 # Additional documentation
```

## 🧪 Testing

### System Health Check

```bash
python gabriel.py
# Choose option 2: System tests
```

### Individual Component Tests

```bash
# Test speech recognition
python gabriel.py  # Option 5

# Test Kokoro TTS
python gabriel.py  # Option 6
```

## 🔒 Privacy & Security

- **Local Processing**: Whisper and Kokoro TTS run locally
- **API Keys**: Store securely in `.env` file (not committed)
- **Audio Files**: Temporary files auto-deleted after use
- **No Data Storage**: Conversations are not saved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of MIT EECS coursework. Please respect academic integrity guidelines.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the technical write-up
3. Test individual components
4. Check system requirements

## 🎵 About Gabriel

Gabriel Manso is an MIT EECS graduate student with interests in:
- Rapid synthesis and hypothesis-driven validation
- Systems thinking and empathetic communication
- Music: Pink Floyd, Bombay Bicycle Club, Stevie Ray Vaughan
- Progressive rock, psychedelic rock, indie rock, blues rock

The AI system captures his conversational style, Brazilian warmth, and intellectual curiosity.

---

**Note**: This system requires significant computational resources. For best performance, use a machine with at least 8GB RAM and a modern CPU. GPU acceleration is automatically utilized when available.
