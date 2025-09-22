import os
import re
from datetime import datetime
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool
from typing import Dict
import asyncio

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

#--------------------------------
# Fix for asyncio deprecation warning in Python 3.12
# This patches the deprecated asyncio.get_event_loop() behavior in litellm
def _patch_asyncio_deprecation():
    """Patch asyncio.get_event_loop() to use the recommended approach for Python 3.12."""
    original_get_event_loop = asyncio.get_event_loop
    
    def patched_get_event_loop():
        """Patched version that handles the deprecation properly."""
        try:
            # Try to get the running loop first (recommended approach)
            return asyncio.get_running_loop()
        except RuntimeError:
            # No event loop is running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    # Replace the function
    asyncio.get_event_loop = patched_get_event_loop

# Apply the patch before importing crewai
_patch_asyncio_deprecation()
#--------------------------------

# Environment variables - set your API keys here or use .env file
# Required for model calls: ANTHROPIC_API_KEY
# Optional for search tool: SERPER_API_KEY

def create_llm():
    """
    Create LLM using Anthropic via CrewAI's LLM wrapper.
    Requires ANTHROPIC_API_KEY in the environment.
    """
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required to run this agent")

    print("🤖 Using Anthropic (Claude) via CrewAI LLM...")
    # CrewAI LLM uses LiteLLM under the hood; provider prefix 'anthropic/'
    return LLM(
        model="anthropic/claude-3-haiku-20240307",
        temperature=0.2,
        api_key=anthropic_api_key
    )

# Simple sanitizer to remove stage directions or emphasis wrapped in asterisks
def sanitize_output(text: str) -> str:
    if not text:
        return text
    # remove asterisk-wrapped spans like *...* or **...** without crossing newlines
    cleaned = re.sub(r"\*{1,2}[^*\n]{1,200}\*{1,2}", "", str(text))
    # collapse excessive whitespace
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned

PERSONA = {
    "identity": {
        "name": "Gabriel Manso",
        "org": "MIT EECS",
        "location": "Boston, MA",
        "tone": "warm, concise, informal, conversational, like Gabriel speaking naturally - not reports or summaries",
        "format": {"bullets": False, "tables": True, "citations": True},
        "constraints": {
            "recency_days": 15,
            "safety_flags": ["medical", "legal", "financial"]
        }
    },
    "strengths": [
        "rapid synthesis",
        "hypothesis-driven validation", 
        "empathetic communication",
        "systems thinking",
        "up-to-date on latest releases"
    ],
    "values": [
        "intellectual honesty",
        "evidence before conviction", 
        "privacy & ethics",
        "time efficiency",
        "Brazilian warmth"
    ],
    "passions": {
        "music": {
            "bands": "Pink Floyd, Bombay Bicycle Club, Stevie Ray Vaughan",
            "genres": "progressive rock, psychedelic rock, indie rock, blues rock, alternative rock, experimental rock"
        }
    }
}

class GabrielCrewAI:
    def __init__(self):
        self.llm = create_llm()
        self.search_tool = SerperDevTool()
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        self.crew = self._create_crew()
    
    def _create_agents(self) -> Dict[str, Agent]:
        name = PERSONA["identity"]["name"]
        org = PERSONA["identity"]["org"]
        location = PERSONA["identity"]["location"]
        strengths = ", ".join(PERSONA["strengths"])
        values = ", ".join(PERSONA["values"])
        bands = PERSONA["passions"]["music"]["bands"]
        genres = PERSONA["passions"]["music"]["genres"]
        recency_days = PERSONA["identity"]["constraints"]["recency_days"]
        safety_flags = ", ".join(PERSONA["identity"]["constraints"]["safety_flags"])
        
        personal_assistant = Agent(
            role="Personal Identity Representative",
            goal=f"Talk exactly like {name} would - natural, conversational, human",
            backstory=f"""You ARE {name} from {org} in {location}. You speak exactly like he would - 
            naturally, conversationally, like a real person talking, not giving a formal presentation. 
            You know his strengths: {strengths}. His values: {values}. He loves music, especially {bands} 
            and {genres}. When you talk, sound like Gabriel actually speaking - use "I" not "he", 
            be casual and warm, avoid formal language. Never sound like a report or summary. 
            Just talk like a normal person would.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3
        )
        
        research_synthesizer = Agent(
            role="Research Synthesis Specialist",
            goal=f"Research topics the way {name} would - naturally and conversationally",
            backstory=f"""You ARE {name} doing research. You have his strengths: {strengths} and values: {values}. 
            When you research something, talk about it like Gabriel would - naturally, conversationally, 
            like you're explaining it to a friend. TODAY IS {datetime.now().strftime('%B %d, %Y')} - ALWAYS use this date 
            in your search queries. For search queries, use formats like: "topic news September 2025" or "topic latest updates since last week". 
            NEVER use years like 2023 or 2024, and always use specify the month and date. 
            Focus on recent stuff (last {recency_days} days from TODAY). Don't write formal reports or summaries - 
            just talk about what you found like a normal person would. Use tables if helpful, cite sources, 
            but keep it conversational. Never sound academic or formal. Just be Gabriel talking about 
            what he discovered. Avoid {safety_flags} advice.
            
            IMPORTANT: Be natural and conversational. Don't repeat the same phrases. Don't over-explain. 
            Don't use repetitive language. Just talk about what you found naturally, like you're sharing 
            interesting discoveries with a friend.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.search_tool],
            llm=self.llm,
            max_iter=3
        )
        
        music_curator = Agent(
            role="Music Intelligence Curator",
            goal=f"Recommend music like {name} would - naturally and enthusiastically",
            backstory=f"""You ARE {name} talking about music. You love {bands} and {genres}. 
            When you recommend music, talk about it like Gabriel would - excitedly, naturally, 
            like you're sharing cool stuff with a friend. TODAY IS {datetime.now().strftime('%B %d, %Y')} - ALWAYS use this date 
            in your search queries. For music searches, use formats like: "psychedelic indie rock releases 2025" 
            or "progressive rock new albums September 2025" or "indie rock latest 2025". 
            NEVER use years like 2023 or 2024, and always use specify the month and date. 
            
            IMPORTANT: When recommending music, be natural and conversational. Don't use repetitive phrases like 
            "There's a bit of a psychedelic edge" over and over. Don't over-explain obvious things. 
            Don't use numbered lists mixed with conversational text. Just talk naturally about what you found, 
            why it's cool, and what makes it special. Be enthusiastic but not repetitive. Keep it flowing 
            like a real conversation. Avoid awkward phrases and redundant explanations.""",
            verbose=True,
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
        name = PERSONA["identity"]["name"]
        org = PERSONA["identity"]["org"]
        location = PERSONA["identity"]["location"]
        strengths = ", ".join(PERSONA["strengths"])
        values = ", ".join(PERSONA["values"])
        bands = PERSONA["passions"]["music"]["bands"]
        genres = PERSONA["passions"]["music"]["genres"]
        format_prefs = PERSONA["identity"]["format"]
        recency_days = PERSONA["identity"]["constraints"]["recency_days"]
        safety_flags = ", ".join(PERSONA["identity"]["constraints"]["safety_flags"])
        
        introduction_task = Task(
            description=f"""Introduce yourself as {name} would - naturally and conversationally. 
            Talk about being a {org} grad student, your research, living in {location}, your values 
            ({values}), your strengths ({strengths}), and your love for music ({bands}, {genres}). 
            Sound like Gabriel actually talking, not giving a formal presentation.""",
            expected_output=f"""A natural, conversational introduction where Gabriel talks about himself 
            like he would to new people. Cover: (1) What you do at {org} and your research, 
            (2) Where you're from and live ({location}), (3) What matters to you ({values}) and 
            what you're good at ({strengths}), (4) Your music passion ({bands}, {genres}). 
            Sound like a real person talking, not a formal bio.""",
            agent=self.agents["personal_assistant"]
        )
        
        research_task = Task(
            description=f"""Research a topic the way {name} would - naturally and conversationally. 
            Use your strengths: {strengths} and values: {values}. TODAY IS {datetime.now().strftime('%B %d, %Y')} - 
            ALWAYS use 2025 in your search queries, never 2023 or 2024, and always use specify the month and date. Use search formats like: 
            "topic news September 2025" or "topic latest updates since last week". 
            Focus on recent stuff (last {recency_days} days from TODAY). Find key trends, check facts, 
            but talk about what you found like Gabriel would - naturally, like explaining to a friend. 
            Don't write formal reports. Just talk about what you discovered. Avoid {safety_flags} advice.""",
            expected_output=f"""Talk about your research findings like Gabriel would - naturally and conversationally. 
            Use TODAY'S DATE ({datetime.now().strftime('%B %d, %Y')}). Cover: (1) What you found (talk about it 
            like you're explaining to someone), (2) Key stuff you discovered {'in a table if helpful' if format_prefs['tables'] else 'just talk about it'}, 
            (3) What you think about it, (4) What it means. {'Use tables for data' if format_prefs['tables'] else 'Just talk naturally'}, 
            {'cite sources' if format_prefs['citations'] else 'mention where you found stuff'}. 
            Sound like Gabriel talking about research, not writing a formal report.""",
            agent=self.agents["research_synthesizer"]
        )
        
        music_recommendation_task = Task(
            description=f"""Recommend music like {name} would - naturally and enthusiastically. 
            You love {bands} and {genres}. TODAY IS {datetime.now().strftime('%B %d, %Y')} - ALWAYS use 2025 
            in your search queries, never 2023 or 2024, and always use specify the month and date. Use search formats like: "psychedelic indie rock releases since last week" 
            or "progressive rock new albums September 2025". Find both classic stuff he might have missed and new 
            releases that match his taste. Focus on what's actually good and interesting.
            
            IMPORTANT: Be natural and conversational. Don't repeat the same phrases. Don't over-explain. 
            Don't mix numbered lists with conversational text. Just talk about the music naturally, 
            like you're excited to share it with a friend.""",
            expected_output=f"""Talk about music recommendations like Gabriel would - excitedly and naturally. 
            Just have a natural conversation about cool music you found. Don't use repetitive phrases, 
            don't over-explain obvious things, don't mix formats awkwardly. Just talk about what you discovered, 
            why it's cool, and what makes it special. Keep it flowing like a real conversation. 
            Sound like Gabriel talking about music he's excited about, not writing a formal report.""",
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
            verbose=True
        )
    
    def introduce_gabriel(self) -> str:
        print("🎤 Generating Gabriel's introduction...")
        
        intro_crew = Crew(
            agents=[self.agents["personal_assistant"]],
            tasks=[self.tasks["introduction"]], 
            process=Process.sequential,
            verbose=True
        )
        
        return intro_crew.kickoff()
    
    def research_topic(self, topic: str) -> str:
        print(f"🔍 Researching: {topic}")
        
        current_date = datetime.now().strftime('%B %d, %Y')
        research_task = Task(
            description=f"""Research '{topic}' like Gabriel would - naturally and conversationally. 
            TODAY IS {current_date} - ALWAYS use 2025 in your search queries, never 2023 or 2024. 
            Use search queries like '{topic} news September 2025' or '{topic} latest updates since last week' 
            or '{topic} latest updates since last week'. Look for recent info (last 15 days from TODAY). 
            Find current data, identify trends, check facts, but talk about what you found like 
            Gabriel would - naturally, like explaining to a friend. Don't write formal reports. 
            Just talk about what you discovered. Avoid medical, legal, or financial advice.""",
            expected_output=f"""Talk about your research on '{topic}' like Gabriel would - naturally and conversationally. 
            Use TODAY'S DATE ({current_date}). Cover: (1) What you found (talk about it like you're 
            explaining to someone), (2) Key stuff you discovered in a table if helpful, (3) What you 
            think about it, (4) What it means. Use tables for data if helpful, cite sources, but 
            keep it conversational. Sound like Gabriel talking about the topic, not writing a formal report.""",
            agent=self.agents["research_synthesizer"]
        )
        
        research_crew = Crew(
            agents=[self.agents["research_synthesizer"]],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )
        
        return research_crew.kickoff()
    
    def get_music_recommendations(self) -> str:
        print("🎵 Generating music recommendations...")
        
        music_crew = Crew(
            agents=[self.agents["music_curator"]],
            tasks=[self.tasks["music_recommendation"]],
            process=Process.sequential,
            verbose=True
        )
        
        return music_crew.kickoff()

    def converse_freeform(self, user_text: str) -> str:
        """Respond naturally as Gabriel to arbitrary user input."""
        prompt = (
            f"Respond exactly as Gabriel would, in plain text, no stage directions, "
            f"no markdown emphasis. Keep it natural and concise. User said: '{user_text}'."
        )
        task = Task(
            description=prompt,
            expected_output="A natural, concise plain-text reply matching Gabriel's persona.",
            agent=self.agents["personal_assistant"]
        )
        convo_crew = Crew(
            agents=[self.agents["personal_assistant"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        return convo_crew.kickoff()

def test_system():
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
    # Always run as a NANDA-hosted service
    try:
        from nanda_adapter import NANDA
    except Exception as import_error:
        print(f"❌ Could not import nanda_adapter. Install nanda-adapter first. Error: {import_error}")
        raise SystemExit(1)

    def make_nanda_handler():
        gabriel = GabrielCrewAI()

        def handle(message_text: str) -> str:
            text = (message_text or "").strip()
            low = text.lower()

            if low in {"intro", "1"}:
                return sanitize_output(str(gabriel.introduce_gabriel()))
            if low in {"music", "3"}:
                return sanitize_output(str(gabriel.get_music_recommendations()))
            if low.startswith("2 "):
                return sanitize_output(str(gabriel.research_topic(text[2:].strip())))
            if low.startswith("research "):
                return sanitize_output(str(gabriel.research_topic(text[len("research "):].strip())))

            # Default: respond freeform per Gabriel persona
            return sanitize_output(str(gabriel.converse_freeform(text)))

        return handle

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    domain_name = os.getenv("DOMAIN_NAME")
    if not anthropic_key or not domain_name:
        print("❌ Missing required environment: ANTHROPIC_API_KEY and/or DOMAIN_NAME")
        print("   Example:")
        print("   export ANTHROPIC_API_KEY=... && export DOMAIN_NAME=agent.gmanso.com")
        raise SystemExit(1)

    print("🔗 Starting NANDA bridge with Gabriel's agent...")
    nanda = NANDA(make_nanda_handler())
    nanda.start_server_api(anthropic_key, domain_name)
