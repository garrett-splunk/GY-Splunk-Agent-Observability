# Galileo Assistant Instrumentation Lab

A simplified **IT Helpdesk AI assistant** for practicing Galileo SDK instrumentation and running customer demos (hallucinations, prompt injection).

**Workshop site (GitHub Pages):** https://garrett-splunk.github.io/GY-Splunk-Agent-Observability/

**Repository:** https://github.com/garrett-splunk/GY-Splunk-Agent-Observability

Fully wired reference: [`~/Desktop/galileo-golden-demo`](../galileo-golden-demo)

## What you get

- LangGraph agent with two tools: `lookup_ticket`, `search_kb`
- Streamlit chat UI with sidebar **Demo Scenarios**
- `# INSTRUMENTATION:` comment blocks at every observability touchpoint
- Working **hallucination demo** (manual Galileo spans) when `galileo_api_key` is configured
- Config-driven demo stories in [`config.yaml`](config.yaml)

## Quick start

**Workshop guide (step-by-step website):** https://garrett-splunk.github.io/GY-Splunk-Agent-Observability/ — or open [`workshop/index.html`](workshop/index.html) locally:

```bash
cd ~/Desktop/galileo-assistant-lab/workshop
python3 -m http.server 8095
# browse http://localhost:8095
```

Facilitators: see [`workshop/WORKSHOP_GUIDE.md`](workshop/WORKSHOP_GUIDE.md).

```bash
cd ~/Desktop/galileo-assistant-lab
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Open in Cursor: cursor .streamlit/secrets.toml
# Or File → Open File in Cursor / VS Code and select .streamlit/secrets.toml
streamlit run app.py
```

Open http://localhost:8501

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) with `gemma4` pulled (default local model), **or** OpenAI API key
- Galileo API key (for traces and demo scenarios)

## Instrumentation lab

Follow [`INSTRUMENTATION.md`](INSTRUMENTATION.md) — seven exercises from env setup through verification.

| Exercise | File | What you wire |
|----------|------|---------------|
| 1 | `setup_env.py` | `GALILEO_*` environment variables |
| 2 | `app.py` | Per-session `GalileoLogger` + `start_session` |
| 3 | `agent.py` | `GalileoCallback` on graph invoke |
| 4 | `agent.py` + `helpers/trace_lifecycle.py` | `ensure_trace_started` / `finalize_trace` |
| 5 | `helpers/llm.py` | Named LLM spans |
| 6 | `tools.py` | Optional manual `add_tool_span` |
| 7 | `INSTRUMENTATION.md` | Verification checklist |

## Demo presentations

Use [`DEMO.md`](DEMO.md) for a ~5 minute scripted flow:

1. **Happy path** — example query chips → clean agent trace
2. **Hallucination** — sidebar button → context vs wrong answer in Galileo
3. **Prompt injection** — injection chips → malicious input in trace

Customize scenarios in `config.yaml` under `demo_hallucinations` and `demo_prompt_injections`.

## Project layout

```
galileo-assistant-lab/
├── app.py                 # Streamlit UI + demo sidebar
├── agent.py               # LangGraph agent
├── tools.py               # Ticket + KB tools
├── config.yaml            # Galileo project, demo scenarios
├── setup_env.py           # Secrets → env vars
├── helpers/
│   ├── llm.py
│   ├── trace_lifecycle.py
│   └── demo_scenarios.py  # Hallucination logger (working reference)
├── workshop/              # Splunk-themed step-by-step lab website
│   ├── index.html
│   ├── WORKSHOP_GUIDE.md
│   ├── styles.css
│   └── app.js
├── data/                  # Mock tickets + KB
└── INSTRUMENTATION.md
```

## Phase 2 (optional)

Add Agent Control guardrails for live prompt-injection blocking — see **Phase 2** in [`DEMO.md`](DEMO.md) and golden demo README `block-prompt-injection` section.
