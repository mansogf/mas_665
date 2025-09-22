## HW2 — Gabriel Agent Runbook

This guide shows how to install dependencies and run the `gabriel.py` agent (served via NANDA).

### 1) Create and activate a virtual environment (recommended)

```bash
cd hw2/adapter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

### 2) Install the adapter package and requirements

```bash
# Install the nanda_adapter package in editable mode
pip install -e .

# Install example/tooling dependencies
pip install -r requirements.txt
```

### 3) Set required environment variables

```bash
# Required for model calls (Claude via CrewAI/LiteLLM)
export ANTHROPIC_API_KEY="<your_api_key>"

# Required by NANDA to expose the server endpoint
export DOMAIN_NAME="agent.gmanso.com"  # or your domain

# Optional: enables the Serper search tool used by research/music agents
export SERPER_API_KEY="<optional_serper_key>"
```

### 4) Run Gabriel via NANDA bridge

```bash
# From hw2/adapter (venv active)
python -m nanda_adapter.examples.gabriel
```

If the environment variables are missing, the script will exit with a helpful message.

### 5) Quick self-test (without starting the server)

```bash
python -c "from nanda_adapter.examples.gabriel import test_system; test_system()"
```

### 6) Notes

- `gabriel.py` already patches Python 3.12 asyncio deprecation warnings for LiteLLM usage.
- You must install `nanda_adapter` (step 2, `pip install -e .`) so `from nanda_adapter import NANDA` succeeds.
- Stop the server with Ctrl+C.


