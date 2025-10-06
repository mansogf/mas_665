# Standard library imports
import os
import platform
import subprocess
import tempfile
import uuid
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from contextlib import contextmanager

# Third-party imports
import asyncio
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# Optional imports with fallbacks
try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    import whisper
except ImportError:
    whisper = None


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Constants
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_RECORD_SECONDS = 6.0
DEFAULT_TTS_RATE = 175
DEFAULT_KOKORO_SAMPLE_RATE = 24000
VOICE_ARTIFACTS_DIR = Path(__file__).resolve().parent / "voice_artifacts"

# Voice mapping for TTS
VOICE_MAPPING = {
    "alloy": "af_heart", "echo": "af_heart", "fable": "af_heart",
    "onyx": "af_heart", "nova": "af_heart", "shimmer": "af_heart",
    "puck": "am_puck", "am_puck": "am_puck"
}

# Persona configuration
PERSONA = {
    "name": "Gabriel Manso",
    "role": "PhD student",
    "org": "MIT EECS",
    "location": "Cabridge, Massachusetts",
    "strengths": "rapid synthesis, hypothesis-driven validation, empathetic communication, systems thinking, up-to-date on latest releases",
    "values": "intellectual honesty, evidence before conviction, privacy & ethics, time efficiency, Brazilian warmth",
    "music_bands": "Pink Floyd, Bombay Bicycle Club, Stevie Ray Vaughan",
    "music_genres": "progressive rock, psychedelic rock, indie rock, blues rock, alternative rock, experimental rock",
    "recency_days": 15,
    "safety_flags": "medical, legal, financial"
}

# Configuration functions
def _configure_environment():
    """Set default environment variables."""
    if os.getenv("USE_KOKORO_TTS") is None:
        os.environ["USE_KOKORO_TTS"] = "true"
    if os.getenv("TTS_VOICE") is None:
        os.environ["TTS_VOICE"] = "am_puck"

def _configure_warnings():
    """Configure warning filters for clean output."""
    patterns = [
        "dropout option adds dropout after all but last recurrent layer.*",
        ".*torch.nn.utils.weight_norm.*is deprecated.*",
        ".*Defaulting repo_id to.*"
    ]
    for pattern in patterns:
        warnings.filterwarnings("ignore", message=pattern)

def _patch_asyncio():
    """Patch asyncio.get_event_loop() for Python 3.12 compatibility."""
    original_get_event_loop = asyncio.get_event_loop
    
    def patched_get_event_loop():
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    asyncio.get_event_loop = patched_get_event_loop

# Apply configuration
_configure_environment()
_configure_warnings()
_patch_asyncio()

# Utility functions
def _ensure_voice_dir() -> Path:
    """Ensure the voice artifacts directory exists."""
    try:
        VOICE_ARTIFACTS_DIR.mkdir(exist_ok=True)
        return VOICE_ARTIFACTS_DIR
    except Exception:
        return Path(tempfile.gettempdir())

def _temp_audio_path(suffix: str = ".wav") -> Path:
    """Create a unique audio file path."""
    return _ensure_voice_dir() / f"{uuid.uuid4().hex}{suffix}"

@contextmanager
def _suppress_kokoro_warnings():
    """Context manager to suppress Kokoro TTS warnings."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="dropout option adds dropout after all but last recurrent layer.*")
        warnings.filterwarnings("ignore", message=".*torch.nn.utils.weight_norm.*is deprecated.*")
        warnings.filterwarnings("ignore", message=".*Defaulting repo_id to.*")
        yield

def _get_current_date():
    """Get current date formatted for prompts."""
    return datetime.now().strftime('%B %d, %Y')

def _build_conversational_prompt(name, role, org, location, strengths, values, bands, genres):
    """Build conversational prompt for agents."""
    return f"""You ARE {name}, a {role} at {org} in {location}. You speak exactly like he would - 
    naturally, conversationally, like a real person talking, not giving a formal presentation. 
    You know his strengths: {strengths}. His values: {values}. He loves music, especially {bands} 
    and {genres}. When you talk, sound like Gabriel actually speaking - use "I" not "he", 
    be casual and warm, avoid formal language. Never sound like a report or summary. 
    Just talk like a normal person would. Remember: you are a {role}, not faculty or a professor."""

# LLM creation
def create_llm(quiet: bool = False):
    """Create LLM with OpenAI as primary and Ollama as fallback."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if openai_api_key:
        try:
            if not quiet:
                print("🤖 Attempting to connect to OpenAI...")
            openai_llm = LLM(model="gpt-4o-mini", temperature=0.1, api_key=openai_api_key)
            openai_llm.call("Hello, this is a connection test.")
            if not quiet:
                print("✅ OpenAI connection successful!")
            return openai_llm
        except Exception as e:
            if not quiet:
                print(f"⚠️ OpenAI connection failed: {e}\n🔄 Falling back to Ollama...")
    else:
        if not quiet:
            print("⚠️ No OpenAI API key found, using Ollama directly...")
    
    try:
        if not quiet:
            print("🤖 Attempting to connect to Ollama (llama3:8b)...")
        ollama_llm = LLM(model="ollama/llama3:8b", base_url="http://localhost:11434", temperature=0.2, api_key="ollama")
        ollama_llm.call("Hello, this is a connection test.")
        if not quiet:
            print("✅ Ollama connection successful!")
        return ollama_llm
    except Exception as ollama_error:
        error_msg = "No LLM providers available. Please check your API keys and Ollama setup." if openai_api_key else "Ollama connection failed. Please ensure Ollama is running and the llama3:8b model is available."
        raise Exception(error_msg)

# Audio interface
class AudioInterface:
    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE, input_device: Optional[object] = None, output_device: Optional[object] = None):
        self.sample_rate = sample_rate
        self._record_capable = sd is not None and sf is not None
        self.input_device = input_device
        self.output_device = output_device

    def ensure_recording_available(self):
        if not self._record_capable:
            raise RuntimeError("Recording requires sounddevice and soundfile. Install them to use voice mode.")

    def record(self, duration_seconds: float) -> Path:
        self.ensure_recording_available()
        frames = int(duration_seconds * self.sample_rate)
        audio = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype="float32", device=self.input_device)
        sd.wait()
        
        target_dir = _ensure_voice_dir()
        fd, path_str = tempfile.mkstemp(suffix=".wav", dir=str(target_dir))
        os.close(fd)
        sf.write(path_str, audio, self.sample_rate)
        return Path(path_str)

    def play(self, audio_path: Path):
        if sd is None or sf is None:
            print(f"Audio playback unavailable. File saved at {audio_path}.")
            return
        data, sample_rate = sf.read(str(audio_path), dtype="float32")
        sd.play(data, sample_rate, device=self.output_device)
        sd.wait()

# Speech-to-text engine
class SpeechToTextEngine:
    def __init__(self, model_name: str = "small"):
        if whisper is None:
            raise RuntimeError("The whisper package is required for speech-to-text.")
        self.model_name = model_name
        self._model = whisper.load_model(model_name)

    def _use_fp16(self) -> bool:
        try:
            device = getattr(self._model, "device", None)
            return getattr(device, "type", "cpu") == "cuda"
        except Exception:
            return False

    def transcribe(self, audio_path: Path) -> str:
        result = self._model.transcribe(str(audio_path), fp16=self._use_fp16())
        return result.get("text", "").strip()

# Kokoro TTS engine
class KokoroTTS:
    """Kokoro TTS engine using local kokoro library."""
    
    def __init__(self, voice: str = "am_puck", speed: float = 1.0, lang_code: str = "a"):
        try:
            from kokoro import KPipeline
        except ImportError:
            raise RuntimeError("Kokoro library not installed. Run: pip install kokoro>=0.7.16 torch")
        
        self.voice = voice
        self.speed = speed
        self.lang_code = lang_code
        
        try:
            with _suppress_kokoro_warnings():
                self.pipeline = KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Kokoro pipeline: {e}")
    
    def synthesize(self, text: str, destination: Optional[Path] = None) -> Path:
        """Synthesize text to speech using local Kokoro TTS."""
        dest_path = Path(destination) if destination else _temp_audio_path(".wav")
        
        try:
            import numpy as np
            
            with _suppress_kokoro_warnings():
                generator = self.pipeline(text, voice=self.voice, speed=self.speed, split_pattern=r'\n+')
                audio_chunks = [audio for gs, ps, audio in generator]
                
                if not audio_chunks:
                    raise RuntimeError("Kokoro TTS did not generate any audio.")
                
                full_audio = np.concatenate(audio_chunks)
                sf.write(str(dest_path), full_audio, DEFAULT_KOKORO_SAMPLE_RATE)
        except Exception as e:
            raise RuntimeError(f"Kokoro TTS synthesis failed: {e}")
        
        if not dest_path.exists() or dest_path.stat().st_size == 0:
            raise RuntimeError("Kokoro TTS did not produce audio output.")
        
        return dest_path

# Text-to-speech engine (Kokoro TTS only)
class TextToSpeechEngine:
    def __init__(self, voice: Optional[str] = None, rate: Optional[int] = None):
        speed = max(0.25, min(4.0, rate / DEFAULT_TTS_RATE)) if rate else 1.0
        kokoro_voice = VOICE_MAPPING.get(voice.lower(), "am_puck") if voice else "am_puck"
        self.kokoro = KokoroTTS(voice=kokoro_voice, speed=speed)

    def synthesize(self, text: str, destination: Optional[Path] = None) -> Path:
        return self.kokoro.synthesize(text, destination)

# Gabriel CrewAI system
class GabrielCrewAI:
    def __init__(self, llm_quiet: bool = False, verbose: bool = True):
        self.verbose = verbose
        self.llm = create_llm(quiet=llm_quiet)
        self.search_tool = SerperDevTool()
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        self.crew = self._create_crew()
    
    def _create_agents(self) -> Dict[str, Agent]:
        p = PERSONA
        current_date = _get_current_date()
        base_prompt = _build_conversational_prompt(p["name"], p["role"], p["org"], p["location"], p["strengths"], p["values"], p["music_bands"], p["music_genres"])
        
        personal_assistant = Agent(
            role="Personal Identity Representative",
            goal=f"Talk exactly like {p['name']} would - natural, conversational, human",
            backstory=f"""{base_prompt} You are Gabriel Manso, a PhD student at MIT EECS, not a professor or faculty member. 
            You're still learning and growing in your field, and you approach conversations with the curiosity and 
            enthusiasm of a graduate student.""",
            verbose=self.verbose,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3
        )
        
        research_synthesizer = Agent(
            role="Research Synthesis Specialist",
            goal=f"Research topics the way {p['name']} would - naturally and conversationally",
            backstory=f"""You ARE {p['name']}, a PhD student at MIT EECS, doing research. You have his strengths: {p['strengths']} and values: {p['values']}. 
            As a graduate student, you approach research with curiosity and the perspective of someone who is still learning. 
            When you research something, talk about it like Gabriel would - naturally, conversationally, 
            like you're explaining it to a friend. TODAY IS {current_date} - ALWAYS use this date 
            in your search queries. For search queries, use formats like: "topic news October 2025" or "topic latest updates since last week". 
            Focus on recent stuff (last {p['recency_days']} days from TODAY). Don't write formal reports or summaries - 
            just talk about what you found like a normal person would. Use tables if helpful, cite sources, 
            but keep it conversational. Avoid {p['safety_flags']} advice.
            
            IMPORTANT: Be natural and conversational. Don't repeat the same phrases. Don't over-explain. 
            Just talk about what you found naturally, like you're sharing interesting discoveries with a friend. 
            Remember: you are a PhD student, not a professor or faculty member.""",
            verbose=self.verbose,
            allow_delegation=False,
            tools=[self.search_tool],
            llm=self.llm,
            max_iter=3
        )
        
        music_curator = Agent(
            role="Music Intelligence Curator",
            goal=f"Recommend music like {p['name']} would - naturally and enthusiastically",
            backstory=f"""You ARE {p['name']}, a PhD student at MIT EECS, talking about music. You love {p['music_bands']} and {p['music_genres']}. 
            As a graduate student, you have the time and passion to explore music deeply. When you recommend music, 
            talk about it like Gabriel would - excitedly, naturally, like you're sharing cool stuff with a friend. 
            TODAY IS {current_date} - ALWAYS use this date in your search queries. For music searches, use formats like: 
            "psychedelic indie rock releases 2025" or "progressive rock new albums October 2025" or "indie rock latest 2025". 
            
            IMPORTANT: When recommending music, be natural and conversational. Don't use repetitive phrases. 
            Don't over-explain obvious things. Just talk naturally about what you found, 
            why it's cool, and what makes it special. Be enthusiastic but not repetitive. Keep it flowing 
            like a real conversation. Remember: you are a PhD student, not a professor or faculty member.""",
            verbose=self.verbose,
            allow_delegation=False,
            tools=[self.search_tool],
            llm=self.llm,
            max_iter=3
        )
        
        return {
            "personal_assistant": personal_assistant,
            "research_synthesizer": research_synthesizer, 
            "music_curator": music_curator
        }
    
    def _create_tasks(self) -> Dict[str, Task]:
        p = PERSONA
        current_date = _get_current_date()
        
        introduction_task = Task(
            description=f"""Introduce yourself as {p['name']} would - naturally and conversationally. 
            Talk about being a PhD student at {p['org']}, your research, living in {p['location']}, your values 
            ({p['values']}), your strengths ({p['strengths']}), and your love for music ({p['music_bands']}, {p['music_genres']}). 
            Make it clear you are a graduate student, not faculty. Sound like Gabriel actually talking, not giving a formal presentation.""",
            expected_output=f"""A natural, conversational introduction where Gabriel talks about himself 
            like he would to new people. Cover: (1) What you do as a PhD student at {p['org']} and your research, 
            (2) Where you're from and live ({p['location']}), (3) What matters to you ({p['values']}) and 
            what you're good at ({p['strengths']}), (4) Your music passion ({p['music_bands']}, {p['music_genres']}). 
            Make sure to emphasize that you are a PhD student, not a professor. Sound like a real person talking, not a formal bio.""",
            agent=self.agents["personal_assistant"]
        )
        
        research_task = Task(
            description=f"""Research a topic the way {p['name']} would - naturally and conversationally. 
            As a PhD student, you approach research with curiosity and the perspective of someone who is still learning. 
            Use your strengths: {p['strengths']} and values: {p['values']}. TODAY IS {current_date} - 
            ALWAYS use 2025 in your search queries. Use search formats like: 
            "topic news October 2025" or "topic latest updates since last week". 
            Focus on recent stuff (last {p['recency_days']} days from TODAY). Find key trends, check facts, 
            but talk about what you found like Gabriel would - naturally, like explaining to a friend. 
            Don't write formal reports. Just talk about what you discovered. Avoid {p['safety_flags']} advice.""",
            expected_output=f"""Talk about your research findings like Gabriel would - naturally and conversationally. 
            Use TODAY'S DATE ({current_date}). Cover: (1) What you found (talk about it 
            like you're explaining to someone), (2) Key stuff you discovered in a table if helpful, 
            (3) What you think about it, (4) What it means. Use tables for data if helpful, cite sources, but 
            keep it conversational. Sound like Gabriel, a PhD student, talking about research, not writing a formal report.""",
            agent=self.agents["research_synthesizer"]
        )
        
        music_recommendation_task = Task(
            description=f"""Recommend music like {p['name']} would - naturally and enthusiastically. 
            As a PhD student, you have the time and passion to explore music deeply. You love {p['music_bands']} and {p['music_genres']}. 
            TODAY IS {current_date} - ALWAYS use 2025 in your search queries. Use search formats like: 
            "psychedelic indie rock releases since last week" or "progressive rock new albums October 2025". 
            Find both classic stuff he might have missed and new releases that match his taste. Focus on what's actually good and interesting.
            
            IMPORTANT: Be natural and conversational. Don't repeat the same phrases. Don't over-explain. 
            Just talk about the music naturally, like you're excited to share it with a friend.""",
            expected_output=f"""Talk about music recommendations like Gabriel would - excitedly and naturally. 
            Just have a natural conversation about cool music you found. Don't use repetitive phrases, 
            don't over-explain obvious things. Just talk about what you discovered, 
            why it's cool, and what makes it special. Keep it flowing like a real conversation. 
            Sound like Gabriel, a PhD student, talking about music he's excited about.""",
            agent=self.agents["music_curator"]
        )
        
        return {
            "introduction": introduction_task,
            "research": research_task,
            "music_recommendation": music_recommendation_task
        }
    
    def _create_crew(self) -> Crew:
        return Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            process=Process.sequential,
            verbose=self.verbose
        )
    
    def introduce_gabriel(self) -> str:
        print("🎤 Generating Gabriel's introduction...")
        intro_crew = Crew(
            agents=[self.agents["personal_assistant"]],
            tasks=[self.tasks["introduction"]], 
            process=Process.sequential,
            verbose=self.verbose
        )
        return intro_crew.kickoff()
    
    def research_topic(self, topic: str) -> str:
        print(f"🔍 Researching: {topic}")
        current_date = _get_current_date()
        
        research_task = Task(
            description=f"""Research '{topic}' like Gabriel would - naturally and conversationally. 
            As a PhD student, you approach research with curiosity and the perspective of someone who is still learning. 
            TODAY IS {current_date} - ALWAYS use 2025 in your search queries. 
            Use search queries like '{topic} news October 2025' or '{topic} latest updates since last week'. 
            Look for recent info (last 15 days from TODAY). 
            Find current data, identify trends, check facts, but talk about what you found like 
            Gabriel would - naturally, like explaining to a friend. Don't write formal reports. 
            Just talk about what you discovered. Avoid medical, legal, or financial advice.""",
            expected_output=f"""Talk about your research on '{topic}' like Gabriel would - naturally and conversationally. 
            Use TODAY'S DATE ({current_date}). Cover: (1) What you found (talk about it like you're 
            explaining to someone), (2) Key stuff you discovered in a table if helpful, (3) What you 
            think about it, (4) What it means. Use tables for data if helpful, cite sources, but 
            keep it conversational. Sound like Gabriel, a PhD student, talking about the topic.""",
            agent=self.agents["research_synthesizer"]
        )
        
        research_crew = Crew(
            agents=[self.agents["research_synthesizer"]],
            tasks=[research_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        return research_crew.kickoff()
    
    def get_music_recommendations(self) -> str:
        print("🎵 Generating music recommendations...")
        music_crew = Crew(
            agents=[self.agents["music_curator"]],
            tasks=[self.tasks["music_recommendation"]],
            process=Process.sequential,
            verbose=self.verbose
        )
        return music_crew.kickoff()

def create_gabriel_response_agent(llm=None, llm_quiet: bool = False, verbose: bool = True):
    """Create a specialized agent for general Gabriel responses."""
    p = PERSONA
    base_prompt = _build_conversational_prompt(p["name"], p["role"], p["org"], p["location"], p["strengths"], p["values"], p["music_bands"], p["music_genres"])
    
    return Agent(
        role="Gabriel Manso",
        goal=f"Respond to any question or topic exactly like {p['name']} would - naturally, conversationally, and authentically",
        backstory=f"""{base_prompt} You are Gabriel Manso, a PhD student at MIT EECS, not a professor or faculty member. 
        You can discuss ANY topic, but always maintain Gabriel's personality, warmth, and conversational style. 
        Be helpful, insightful, and authentic in your responses. Approach topics with the curiosity and perspective 
        of a graduate student who is still learning and growing.""",
        verbose=verbose,
        allow_delegation=False,
        llm=llm or create_llm(quiet=llm_quiet),
        max_iter=3
    )

def process_user_input(user_input: str, gabriel_ai: GabrielCrewAI) -> str:
    """Process user input and return Gabriel's response."""
    user_input_lower = user_input.strip().lower()
    
    if user_input_lower in ['intro', 'introduction']:
        return gabriel_ai.introduce_gabriel()
    elif user_input_lower in ['music', 'music recommendations']:
        return gabriel_ai.get_music_recommendations()
    elif user_input_lower.startswith('research '):
        topic = user_input[9:].strip()
        if topic:
            return gabriel_ai.research_topic(topic)
        return "Hey! I'd love to research something for you. What topic are you curious about?"
    else:
        gabriel_response_agent = create_gabriel_response_agent(llm=gabriel_ai.llm, llm_quiet=True, verbose=gabriel_ai.verbose)
        
        response_task = Task(
            description=f"""Respond to this user input exactly like Gabriel would: "{user_input}"
            
            Be natural, conversational, and authentic. Use Gabriel's personality, warmth, and style. 
            If it's a question, answer it like Gabriel would. If it's a statement, respond naturally. 
            If you don't know something, say so honestly. Always maintain Gabriel's Brazilian warmth 
            and conversational tone. Don't be overly formal or academic - just be Gabriel talking 
            to someone.""",
            expected_output="A natural, conversational response that sounds exactly like Gabriel would talk",
            agent=gabriel_response_agent
        )
        
        response_crew = Crew(
            agents=[gabriel_response_agent],
            tasks=[response_task],
            process=Process.sequential,
            verbose=gabriel_ai.verbose
        )
        return response_crew.kickoff()

# Voice interaction session
class VoiceInteractionSession:
    def __init__(self, gabriel_ai: GabrielCrewAI, stt_model: str = "small", record_seconds: float = DEFAULT_RECORD_SECONDS,
                 tts_voice: Optional[str] = None, tts_rate: Optional[int] = None, input_device: Optional[str] = None,
                 output_device: Optional[str] = None):
        self.gabriel_ai = gabriel_ai
        self.record_seconds = record_seconds
        self.audio = AudioInterface(input_device=input_device, output_device=output_device)
        self.stt = SpeechToTextEngine(model_name=stt_model)
        self.tts = TextToSpeechEngine(voice=tts_voice, rate=tts_rate)

    def run(self):
        print("\n🎙️ Voice chat ready. Press Enter to record or type commands.")
        print("- Enter: record a message")
        print("- text: type instead of speaking")
        print("- quit: exit voice chat")

        while True:
            action = input("Command (Enter/text/quit): ").strip()
            action_lower = action.lower()

            if action_lower in {"quit", "q"}:
                print("\nGabriel: Valeu! Voice session closed.")
                break

            if action_lower == "text":
                user_text = input("Type your message: ").strip()
                if not user_text:
                    print("No text provided.")
                    continue
            elif action:
                user_text = action
                print(f"You typed: {user_text}")
            else:
                try:
                    audio_path = self.audio.record(self.record_seconds)
                    print(f"Captured audio -> {audio_path}")
                    user_text = self.stt.transcribe(audio_path)
                    audio_path.unlink(missing_ok=True)
                except Exception as err:
                    print(f"Recording/transcription failed: {err}")
                    continue

                if not user_text:
                    print("I could not understand anything. Try again.")
                    continue

                print(f"You said: {user_text}")
                correction = input("Edit transcript (press Enter to keep it as-is): ").strip()
                if correction:
                    user_text = correction

            try:
                response = process_user_input(user_text, self.gabriel_ai)
                if not isinstance(response, str):
                    response = str(response)
            except Exception as err:
                print(f"Response failed: {err}")
                continue

            print(f"Gabriel: {response}")

            try:
                output_path = self.tts.synthesize(response)
                self.audio.play(output_path)
                size_bytes = output_path.stat().st_size if output_path.exists() else "unknown"
                print(f"🔊 Saved reply audio at {output_path} ({size_bytes} bytes)")
            except Exception as err:
                print(f"Text-to-speech failed: {err}")

# Main functions
def run_gabriel_chat():
    """Run Gabriel in GPT-style chat mode."""
    print("🇧🇷 Gabriel Manso AI - Chat Mode")
    print("=" * 50)
    print("Olá! I'm Gabriel. Ask me anything or just chat!")
    print("Special commands: 'intro', 'music', 'research [topic]'")
    print("Type 'quit' to exit.")
    print("=" * 50)
    
    try:
        gabriel_ai = GabrielCrewAI(llm_quiet=True, verbose=False)
        print("✅ Gabriel AI initialized! Ready to chat.\n")
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nGabriel: Até logo! Thanks for chatting with me! 👋")
                break
            
            if not user_input:
                continue
                
            print("\nGabriel: ", end="")
            response = process_user_input(user_input, gabriel_ai)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGabriel: Interrupted! Até logo! 👋")
            break
        except Exception as e:
            print(f"\nGabriel: Oops, something went wrong: {e}")
            print("Let's try again!")

def run_gabriel_voice_chat():
    """Run Gabriel with voice-enabled interaction."""
    print("🎧 Gabriel Voice Chat")
    print("=" * 50)

    try:
        gabriel_ai = GabrielCrewAI()
        stt_choice = os.getenv("WHISPER_MODEL", "small")
        
        try:
            record_seconds = float(os.getenv("VOICE_RECORD_SECONDS", str(DEFAULT_RECORD_SECONDS)))
        except ValueError:
            record_seconds = DEFAULT_RECORD_SECONDS
            
        tts_voice = os.getenv("TTS_VOICE")
        
        try:
            tts_rate = int(os.getenv("TTS_RATE")) if os.getenv("TTS_RATE") else None
        except ValueError:
            tts_rate = None
        
        print("🎤 Using Kokoro TTS for high-quality voice synthesis")

        session = VoiceInteractionSession(
            gabriel_ai,
            stt_model=stt_choice,
            record_seconds=record_seconds,
            tts_voice=tts_voice,
            tts_rate=tts_rate,
        )
    except Exception as e:
        print(f"❌ Error initializing voice chat: {e}")
        return

    session.run()

def run_single_response(user_input: str):
    """Run Gabriel for a single response."""
    try:
        gabriel_ai = GabrielCrewAI()
        return process_user_input(user_input, gabriel_ai)
    except Exception as e:
        return f"Sorry, I encountered an error: {e}"

def run_speech_to_text_check(record_seconds: float = 4.0):
    """Quick microphone + Whisper sanity check."""
    print("🧪 Speech-to-Text Quick Check")
    print("=" * 50)

    if whisper is None:
        print("Whisper is not installed. Install the 'openai-whisper' package to run this test.")
        return

    audio = AudioInterface()

    try:
        stt = SpeechToTextEngine()
    except Exception as exc:
        print(f"Could not load Whisper model: {exc}")
        return

    try:
        input(f"Press Enter to record for {record_seconds} seconds...")
        audio_path = audio.record(record_seconds)
        print(f"Recorded audio at {audio_path}")
    except Exception as exc:
        print(f"Recording failed: {exc}")
        return

    try:
        transcript = stt.transcribe(audio_path)
    except Exception as exc:
        print(f"Transcription failed: {exc}")
        transcript = ""
    finally:
        try:
            audio_path.unlink(missing_ok=True)
        except Exception:
            pass

    if transcript:
        print(f"Heard: {transcript}")
    else:
        print("No speech detected. Try speaking louder or closer to the mic.")

def run_kokoro_tts_check():
    """Quick Kokoro TTS sanity check."""
    print("🧪 Kokoro TTS Quick Check")
    print("=" * 50)
    
    try:
        tts = TextToSpeechEngine(voice="am_puck")
        print("✅ Kokoro TTS initialized successfully with Puck voice!")
    except Exception as exc:
        print(f"❌ Could not initialize Kokoro TTS: {exc}")
        print("💡 Make sure you have installed kokoro: pip install kokoro>=0.7.16 torch")
        return

    sample_text = "Oi! It's Gabriel. This is a Kokoro TTS test. The voice should sound much more natural and expressive than the default system voices."

    try:
        print("🎤 Generating speech with Kokoro TTS...")
        output_path = tts.synthesize(sample_text)
        print(f"✅ Saved speech to {output_path}")
    except Exception as exc:
        print(f"❌ Generating audio failed: {exc}")
        return

    audio = AudioInterface()
    try:
        print("🔊 Playing audio...")
        audio.play(output_path)
    except Exception as exc:
        print(f"⚠️ Playback failed: {exc}")
        print("You can open the file manually to listen.")

    print(f"📁 File kept at {output_path}. Delete it when you no longer need it.")


def test_system():
    """Test Gabriel AI system."""
    print("🧪 Testing Gabriel AI System...")
    
    try:
        gabriel_ai = GabrielCrewAI()
        print("✅ System initialization: PASSED")
        
        assert len(gabriel_ai.agents) == 3
        print("✅ Agent creation: PASSED")
        
        assert len(gabriel_ai.tasks) == 3
        print("✅ Task creation: PASSED")
        
        assert gabriel_ai.crew is not None
        print("✅ Crew creation: PASSED")
        
        print("\n🎉 All tests passed! Gabriel AI system is ready to use.")
        print("Run the main function to start the interactive session.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🚀 Gabriel Manso CrewAI System")
    
    kokoro_available = False
    try:
        from kokoro import KPipeline
        kokoro_available = True
    except ImportError:
        pass
    
    print("Choose an option:")
    print("1. Run Gabriel Chat")
    print("2. Run system tests")
    print("3. Single response mode")
    print("4. Voice chat mode (Kokoro TTS with Puck voice)" + (" ✅" if kokoro_available else " ❌"))
    print("5. Quick speech-to-text check")
    print("6. Quick Kokoro TTS check" + (" ✅" if kokoro_available else " ❌"))
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice == "2":
        test_system()
    elif choice == "3":
        user_input = input("Enter your message for Gabriel: ").strip()
        if user_input:
            response = run_single_response(user_input)
            print(f"\nGabriel: {response}")
        else:
            print("No input provided.")
    elif choice == "4":
        run_gabriel_voice_chat()
    elif choice == "5":
        run_speech_to_text_check()
    elif choice == "6":
        run_kokoro_tts_check()
    else:
        run_gabriel_chat()
