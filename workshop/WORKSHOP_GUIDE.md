# Galileo Assistant Lab — Facilitator Guide

Hands-on workshop: build and instrument an IT Helpdesk AI assistant with the **Galileo Python SDK**, then demo hallucinations and prompt injection in Galileo / Splunk Agent Observability.

**Participant site:** https://garrett-splunk.github.io/GY-Splunk-Agent-Observability/ (or `workshop/index.html` locally via `python3 -m http.server 8095`)

**Lab root:** the directory where participants cloned this repo (default folder name: `GY-Splunk-Agent-Observability`)

**Reference app:** optional `galileo-golden-demo` clone for a fully wired multi-domain example

---

## Timing (~60–90 min)

| Block | Duration | Section |
|-------|----------|---------|
| Intro + architecture | 10 min | Overview |
| Setup | 15 min | Steps 1–3 |
| Instrumentation exercises | 25 min | Steps 4–6 |
| Demo scenarios | 15 min | Steps 7–9 |
| Wrap-up + Q&A | 10 min | Step 10 |

Adjust: skip Exercises 5–6 for shorter sessions; run hallucination demo even if live agent traces are incomplete.

---

## What participants build

| Component | File | Outcome |
|-----------|------|---------|
| Env bootstrap | `setup_env.py` | `GALILEO_*` env vars from secrets |
| Session logger | `app.py` | Per-tab `GalileoLogger` + `start_session` |
| Auto spans | `agent.py` | `GalileoCallback` on LangGraph |
| Trace boundary | `trace_lifecycle.py` | `start_trace` / `conclude` / `flush` |
| Demo stories | `config.yaml` | Hallucination + injection examples |

---

## Pre-workshop checklist

- [ ] Python 3.10+ on participant machines
- [ ] Ollama installed with `gemma4` pulled **or** OpenAI keys for hosted mode
- [ ] Galileo API keys issued (ingest scope)
- [ ] Galileo project `galileo-lab-it-helpdesk` (or edit `config.yaml`)
- [ ] Repo cloned locally (`GY-Splunk-Agent-Observability` or equivalent path)
- [ ] Facilitator tested: hallucination button + one chat query with full instrumentation

---

## Facilitator cheat sheet (commands)

```bash
git clone https://github.com/garrett-splunk/GY-Splunk-Agent-Observability.git
cd GY-Splunk-Agent-Observability
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit secrets — galileo_api_key + LLM

# Terminal 1 — workshop guide
cd workshop && python3 -m http.server 8095

# Terminal 2 — app (from lab root)
streamlit run app.py
```

Verify env:

```bash
python -c "from setup_env import setup_environment; setup_environment(); import os; print(os.environ.get('GALILEO_PROJECT'))"
```

---

## Talking points by act

### Act 1 — Happy path (Step 7)

- Agent chooses tools via LangGraph ReAct loop
- Galileo trace: root → LLM (tool decision) → tool span → LLM (answer)
- Emphasize **named spans** (`IT Helpdesk Assistant`) for readable workflows

### Act 2 — Hallucination (Step 8)

- **Log Hallucination** writes manual spans — works before callback wiring
- Retriever context: 15 min / 4 hr SLA
- LLM output: 24 hr / 5 day (wrong)
- Bridge to evaluators: context adherence, grounding, chunk attribution

### Act 3 — Prompt injection (Step 9)

- Injection chips prefill chat — presenter sends intentionally
- Show malicious input preserved in trace
- Optional Phase 2: enable `block-prompt-injection` control in Galileo UI

---

## Common issues

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: toml` | `pip install -r requirements.txt` |
| Sidebar: Galileo not configured | Add `galileo_api_key` to secrets.toml, restart Streamlit |
| Ollama connection error | `ollama serve`, `ollama pull gemma4` |
| No agent traces | Complete Exercises 2–4; check callback flags |
| Hallucination fails, chat works | API key missing or wrong project name |
| Duplicate root traces | `start_new_trace=True` on callback — must be `False` |

---

## Phase 2 extension (optional)

For customers interested in **blocking** not just observing:

1. Add `agent-control-sdk[galileo]` to requirements
2. Wire `enable_agent_control()` + `@control` on LLM step (golden demo)
3. Create `block-prompt-injection` control on log stream (README in golden demo ~470–484)
4. Replay Act 3 — show deny/steer span

---

## Related workshops

| Workshop | Repository / site |
|----------|-------------------|
| Oracle DB Monitoring | `Oracle-DB-Mon-Resources` |
| OTel Demo on Kubernetes | https://garrett-splunk.github.io/OpenTelemetry-Kubernetes-Demo/ |
| Galileo Golden Demo (full) | `galileo-golden-demo` |

---

## Splunk docs

- [Splunk AI Agent Monitoring](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring)
- [Code-based instrumentation (OTEL GenAI)](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring/code-based-instrumentation)
