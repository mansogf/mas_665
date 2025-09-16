# Gabriel Manso AI Assistant 🎸🎯

> Interactive AI Digital Twin powered by CrewAI and Ollama - Gabriel's conversational multi-agent assistant for research synthesis and music discovery.

## What Gabriel Manso AI Does

Gabriel Manso AI is an interactive conversational system that embodies Gabriel's authentic voice and expertise:

- **🤖 Interactive Research**: Natural conversational research synthesis on any topic with Gabriel's voice
- **🎵 Music Discovery**: Personalized music recommendations matching Gabriel's progressive/psychedelic rock taste
- **👤 Personal Introduction**: Generate authentic Gabriel introductions for classes and meetings
- **💬 Conversational Interface**: Natural dialogue system with Gabriel's Brazilian warmth and MIT expertise

## System Architecture

### 🤖 Multi-Agent Crew
- **Personal Identity Representative**: Speaks exactly like Gabriel - natural, conversational, human
- **Research Synthesis Specialist**: Researches topics with Gabriel's analytical approach and conversational tone
- **Music Intelligence Curator**: Recommends music with Gabriel's enthusiasm and expertise

### 🛠️ Tools & Capabilities
- **SerperDevTool**: Advanced web search for real-time information
- **Dual LLM Support**: OpenAI GPT-4o-mini (primary) + Ollama gemma3:27b (fallback)
- **Automatic Fallback**: Seamlessly switches to Ollama if OpenAI fails
- **Python 3.12 Compatibility**: Includes asyncio deprecation patches for smooth operation
- **Fresh Research**: Prioritizes sources from the last 15 days with current date awareness

## Quick Start

### Prerequisites

1. **Python 3.12** (recommended) or **Python 3.11** (compatible with CrewAI and asyncio patches)
2. **OpenAI API Key** (optional - for primary LLM)
3. **SERPER API Key** (required - for web search functionality)
4. **Ollama** installed and running (fallback LLM)
5. **gemma3:27b** model pulled (for Ollama fallback)

#### Install Ollama

**macOS/Linux:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the required model (this may take several minutes)
ollama pull gemma3:27b

# Start Ollama service (keep this running in a separate terminal)
ollama serve
```

**Windows:**
```bash
# Download and install from https://ollama.com/download
# Then run:
ollama pull gemma3:27b
ollama serve
```

**Verify Ollama is working:**
```bash
# Check if Ollama is running
ollama list

# Test with a simple query
ollama run gemma3:27b "Hello, this is a test"
```

### Installation

1. **Setup environment**:
   ```bash
   cd hw1
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API Keys** (required for full functionality):
   ```bash
   # Option 1: Set environment variables
   export OPENAI_API_KEY="your-openai-api-key-here"
   export SERPER_API_KEY="your-serper-api-key-here"
   
   # Option 2: Create .env file (recommended)
   echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env
   echo "SERPER_API_KEY=your-serper-api-key-here" >> .env
   ```
   
   **Get your API keys:**
   - **OpenAI API Key**: https://platform.openai.com/api-keys (optional - system will use Ollama if not provided)
   - **SERPER API Key**: https://serper.dev/ (required - for web search functionality)

### Usage

#### Interactive Session
```bash
# Start the interactive Gabriel AI assistant
python main.py

# Choose option 1 for interactive session
# Choose option 2 for system tests
```

#### Available Commands (Interactive Mode)
```
🎯 Como posso ajudar? (How can I help?)

1. 'intro' or '1' - Generate Gabriel's class introduction
2. 'research [topic]' or '2 [topic]' - Research synthesis on any topic
3. 'music' or '3' - Get personalized music recommendations
4. 'about' or '4' - Learn more about Gabriel's research and background
5. 'help' or '5' - Show help menu
6. 'quit' or '6' - Exit the system
```

#### Example Usage
```bash
# Start interactive session
python main.py

# Then use commands like:
🎯 Como posso ajudar? (How can I help?) intro
🎯 Como posso ajudar? (How can I help?) research AI in scientific computing
🎯 Como posso ajudar? (How can I help?) music
🎯 Como posso ajudar? (How can I help?) about
🎯 Como posso ajudar? (How can I help?) quit
```

## How It Works

### 🤖 The 3-Agent Architecture

1. **Personal Identity Representative** 
   - Speaks exactly like Gabriel would - natural, conversational, human
   - Embodies Gabriel's authentic voice and personality
   - Uses "I" not "he" to sound like Gabriel actually speaking
   - Avoids formal language and reports, maintains casual warmth

2. **Research Synthesis Specialist**
   - Researches any topic with Gabriel's analytical approach
   - Uses current date awareness (always 2025, never outdated years)
   - Focuses on recent information (last 15 days)
   - Talks about findings conversationally, like explaining to a friend
   - Uses tables and citations when helpful, but keeps tone natural

3. **Music Intelligence Curator**
   - Recommends music with Gabriel's enthusiasm and expertise
   - Searches for both classic discoveries and new releases
   - Focuses on progressive rock, psychedelic rock, indie rock, blues rock
   - Matches Gabriel's taste: Pink Floyd, Bombay Bicycle Club, Stevie Ray Vaughan
   - Avoids repetitive phrases and over-explanations

### 📋 The Interactive Workflow

1. **System Initialization**: Creates agents, tasks, and crew with Gabriel's persona
2. **Command Processing**: Parses user input and routes to appropriate agent
3. **Agent Execution**: Selected agent performs task with Gabriel's authentic voice
4. **Natural Response**: Returns conversational output that sounds like Gabriel speaking

### 🎵 Gabriel's Profile

- **Identity**: Gabriel Manso, MIT EECS graduate student, Boston, MA
- **Music**: Pink Floyd, Bombay Bicycle Club, Stevie Ray Vaughan
- **Genres**: Progressive rock, psychedelic rock, indie rock, blues rock, alternative rock, experimental rock
- **Communication Style**: Warm, concise, informal, conversational, natural speech patterns
- **Values**: Intellectual honesty, evidence before conviction, privacy & ethics, time efficiency, Brazilian warmth
- **Strengths**: Rapid synthesis, hypothesis-driven validation, empathetic communication, systems thinking
- **Research Focus**: AI effectiveness in scientific computing, meta-analysis of 2,400+ pairwise comparisons

## 📄 Output Format

The system provides real-time conversational responses with:
- **Natural Speech**: Gabriel's authentic voice and conversational tone
- **Current Information**: Real-time research with 2025 date awareness
- **Structured Data**: Tables and citations when helpful, but maintains casual tone
- **Music Recommendations**: Enthusiastic but natural descriptions of discoveries
- **Interactive Experience**: Continuous dialogue with Gabriel's personality

No file outputs - everything happens in real-time through the interactive console.

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY` - For OpenAI GPT-4o-mini (optional, will fallback to Ollama if not provided)
- `SERPER_API_KEY` - For enhanced web search (required - must be set by user)

### System Features

- **Dual LLM Architecture**: OpenAI GPT-4o-mini (primary) with Ollama gemma3:27b (fallback)
- **Automatic Fallback**: Seamlessly switches between LLM providers based on availability
- **Python 3.12 Compatibility**: Includes asyncio deprecation patches for smooth operation
- **Real-time Search**: Uses current date for all search queries (always 2025)
- **Conversational AI**: Natural dialogue system with Gabriel's authentic voice
- **Safety Constraints**: Avoids medical, legal, and financial advice
- **Recency Focus**: Prioritizes information from the last 15 days

### Dependencies

- **CrewAI**: Multi-agent orchestration framework
- **CrewAI Tools**: SerperDevTool for web search
- **OpenAI**: GPT-4o-mini model (primary LLM)
- **Ollama**: Local LLM with gemma3:27b model (fallback LLM)
- **Python 3.12**: With asyncio compatibility patches

## 🔧 Troubleshooting

### Common Issues

**"Ollama connection failed"**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Verify model is available
ollama pull gemma3:27b
```

**"Module not found" or "Import errors"**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (should be 3.12)
python --version
```

**"Invalid response from LLM call" or "LLM connection failed"**
- **OpenAI Issues**: Check if OPENAI_API_KEY is valid and has credits
- **Ollama Issues**: Ensure Ollama is running: `ollama serve`
- **Model Issues**: Check if gemma3:27b model is pulled: `ollama list`
- **Connection Issues**: Verify localhost:11434 is accessible for Ollama
- **SERPER Issues**: Verify SERPER_API_KEY is set and valid
- **Dependencies**: Reinstall requirements: `pip install -r requirements.txt`

**"Asyncio deprecation warnings"**
- The system includes built-in patches for Python 3.12 compatibility
- Warnings are normal and handled automatically

**"No recent sources found" or "SERPER_API_KEY not found"**
- Check internet connection
- Verify SERPER_API_KEY is set correctly: `echo $SERPER_API_KEY`
- Get a free SERPER API key from https://serper.dev/
- Ensure web tools can access external APIs

**"System test failures"**
```bash
# Run system tests
python main.py
# Choose option 2 for testing
```

**"resolution-too-deep" error during pip install**
```bash
# Check Python version
python3 --version

# If using Python 3.13+, install Python 3.12 instead
# On macOS with Homebrew:
brew install python@3.12

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.12 python3.12-venv

# Create virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# Verify version and install dependencies
python --version  # Should show Python 3.12.x
pip install -r requirements.txt
```

**Alternative for Python 3.13 users:**
```bash
# Try with legacy resolver
pip install -r requirements.txt --use-deprecated=legacy-resolver

# Or install packages individually
pip install crewai==0.186.1
pip install crewai-tools==0.71.0
pip install python-dotenv requests beautifulsoup4 lxml openai litellm
```

## 📁 Project Structure

```
hw1/
├── main.py           # Core Gabriel Manso AI interactive system
├── requirements.txt  # Dependencies (CrewAI, tools, etc.)
├── README.md         # This comprehensive guide
└── venv/            # Python 3.12 virtual environment (created after setup)
```

## 🎯 Gabriel's Values & Philosophy

- **Intellectual Honesty**: Evidence before conviction, transparent analysis
- **Brazilian Warmth**: Friendly, empathetic communication with authentic voice
- **Time Efficiency**: Concise, actionable insights without unnecessary complexity
- **Privacy & Ethics**: Safe, responsible AI usage with ethical considerations
- **Systems Thinking**: Structured, comprehensive analysis with clear priorities
- **Up-to-date Knowledge**: Focus on latest releases and emerging trends
- **Natural Communication**: Conversational tone, not formal reports or summaries

## 🚀 Getting Started

1. **Setup**: Follow the Quick Start guide above
2. **Run**: `python main.py` and choose option 1 for interactive session
3. **Explore**: Use the 6 available commands to interact with Gabriel's AI
4. **Test**: Choose option 2 to run system tests and verify everything works
5. **Customize**: Modify the PERSONA dictionary in `main.py` to match your preferences

---

*"Like a perfectly arranged Pink Floyd concept album, every conversation flows naturally with both technical depth and human warmth." - Gabriel Manso AI* 🎸🎯