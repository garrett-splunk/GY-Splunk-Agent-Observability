# Instrumentation Lab Guide

Practice wiring Galileo SDK observability into the IT Helpdesk assistant. Each exercise maps to commented `# INSTRUMENTATION:` blocks in the codebase.

Reference implementation: [`~/Desktop/galileo-golden-demo`](../galileo-golden-demo)

---

## Exercise 1 — Environment bootstrap

**File:** [`setup_env.py`](setup_env.py)

**Goal:** Load Galileo credentials from `.streamlit/secrets.toml` into environment variables.

**What to verify:** When `galileo_api_key` is set in secrets, these env vars should be present at runtime:

- `GALILEO_API_KEY`
- `GALILEO_API_URL` (derived from console URL if omitted)
- `GALILEO_CONSOLE_URL`
- `GALILEO_PROJECT` (from `config.yaml`)
- `GALILEO_LOG_STREAM` (from `config.yaml`)

**Reference:** `galileo-golden-demo/setup_env.py` lines 56–140

**Check:**

```bash
source venv/bin/activate
python -c "from setup_env import setup_environment; setup_environment(); import os; print(os.environ.get('GALILEO_PROJECT'))"
```

Expected: `galileo-lab-it-helpdesk`

---

## Exercise 2 — Per-session logger

**File:** [`app.py`](app.py)

**Goal:** One `GalileoLogger` per browser tab; `start_session` on first user message.

**Steps:**

1. Uncomment `from galileo import GalileoLogger` import
2. Implement `_create_galileo_logger()` body (see comment block)
3. Implement `_start_galileo_session_if_needed()` body (see comment block)

**Reference:** `galileo-golden-demo/app.py` ~1024–1076 (logger creation), ~304–317 (session start)

**Check:** Send a chat message → Galileo console shows a new session named like `IT Helpdesk Assistant Lab Demo`.

---

## Exercise 3 — LangChain callback

**File:** [`agent.py`](agent.py)

**Goal:** Auto-capture LLM and tool spans via `GalileoCallback`.

**Steps:**

1. Uncomment `from galileo.handlers.langchain import GalileoCallback`
2. Replace `self.invoke_config` with the commented version that includes `callbacks`

**Important flags:**

- `start_new_trace=False` — trace started manually in Exercise 4
- `flush_on_chain_end=False` — flush in `finalize_trace`

**Reference:** `galileo-golden-demo/agent_frameworks/langgraph/agent.py` lines 219–230

---

## Exercise 4 — Trace boundary

**Files:** [`agent.py`](agent.py), [`helpers/trace_lifecycle.py`](helpers/trace_lifecycle.py)

**Goal:** Wrap each user query in a root trace.

**Steps:**

1. Uncomment bodies of `ensure_trace_started()` and `finalize_trace()` in `trace_lifecycle.py`
2. Confirm calls in `agent.py` `_process_query_async` (already present)

**Reference:** `galileo-golden-demo/helpers/agent_control_helpers.py` lines 115–135

**Check:** Each chat turn produces one root trace named `Run Agent` with nested LLM/tool spans.

---

## Exercise 5 — Named LLM spans

**File:** [`helpers/llm.py`](helpers/llm.py)

**Goal:** Readable LLM span names in Galileo.

**Note:** `name="IT Helpdesk Assistant"` is already passed to `ChatOllama` / `ChatOpenAI`. Verify spans show this label after Exercise 3.

**Reference:** `galileo-golden-demo/helpers/llm_utils.py`

---

## Exercise 6 — Optional manual tool spans

**File:** [`tools.py`](tools.py)

**Goal:** Explicit tool span metadata via `add_tool_span`.

**Steps:** Uncomment `_log_tool_span()` body.

**When to use:** Extra fields or timing not captured by `GalileoCallback`. May duplicate auto spans — use for demo visibility only.

**Reference:** `galileo-golden-demo/domains/healthcare/tools/logic.py` `_log_tool_span`

---

## Exercise 7 — Verification checklist

Run through this after completing exercises 1–4 (5–6 optional):

- [ ] Sidebar shows **Galileo API key loaded**
- [ ] Send: `Look up ticket T-1001` → agent uses `lookup_ticket`
- [ ] Galileo project `galileo-lab-it-helpdesk`, log stream `default`
- [ ] Trace contains: root → LLM → tool → LLM
- [ ] Click **Log Hallucination to Galileo** → separate trace with retriever + LLM mismatch
- [ ] Send a prompt-injection chip payload → input visible in trace input

### Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| No traces at all | `GALILEO_API_KEY` missing or Exercise 1 incomplete |
| Duplicate root traces | `GalileoCallback(start_new_trace=True)` — must be `False` |
| LLM spans but no tool spans | Callback not attached (Exercise 3) |
| Hallucination button fails | API key not set; check secrets.toml |
| Agent errors on hosted | `openai_api_key` invalid; switch to Local (Ollama) |

---

## Future path: Splunk OTEL GenAI

This lab uses the **Galileo Python SDK** (same family as Splunk Agent Observability). For OpenTelemetry GenAI code-based instrumentation, see Splunk docs:

https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring/code-based-instrumentation

Package: `splunk-otel-util-genai` with `Workflow`, `AgentInvocation`, `LLMInvocation` types.

---

## Compare with golden demo

| Lab exercise | Golden demo file |
|--------------|------------------|
| 1–2 | `setup_env.py`, `app.py` |
| 3–4 | `agent_frameworks/langgraph/agent.py` |
| 5 | `helpers/llm_utils.py` |
| 6 | `domains/healthcare/tools/logic.py` |
| Hallucination demo | `helpers/hallucination_helpers.py` |
