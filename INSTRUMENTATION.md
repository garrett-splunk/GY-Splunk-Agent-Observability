# Instrumentation Lab Guide

Practice wiring Galileo SDK observability into the IT Helpdesk assistant. Each exercise maps to `# INSTRUMENTATION:` blocks in the codebase.

**Workshop site (with copy buttons):** https://garrett-splunk.github.io/GY-Splunk-Agent-Observability/

Reference implementation: optional `galileo-golden-demo` clone

---

## Concepts 101 (Splunk O11y → Galileo)

| Splunk Observability Cloud | Galileo (this lab) |
|---------------------------|-------------------|
| AI trace / span in APM | Trace + LLM/tool/retriever spans in log stream |
| Service / environment | **Project** (`galileo.project`) |
| Deployment or data partition | **Log stream** (`galileo.log_stream`) |
| Platform-side evaluation | **Metrics** on log stream (Step 10) |
| AI trace insights | **Signals** / Log Stream Insights (Step 12) |
| Runtime guardrails | **Agent Control** (Step 13, optional) |
| OTEL GenAI instrumentation | **Galileo SDK** (`GalileoLogger`, `GalileoCallback`) |

**Official docs**

| Topic | Galileo | Splunk |
|-------|---------|--------|
| Overview | [Logging basics](https://docs.galileo.ai/sdk-api/logging/logging-basics) | [AI Agent Monitoring intro](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring) |
| Manual SDK | [GalileoLogger](https://docs.galileo.ai/sdk-api/logging/galileo-logger) | [Code-based OTEL GenAI](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring/code-based-instrumentation) |
| LangChain | [LangChain callback](https://docs.galileo.ai/sdk-api/third-party-integrations/langchain/langchain) | [Monitor AI traces](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/monitor-and-troubleshoot-ai-agents-and-applications/monitor-ai-traces-and-spans) |
| Quality | [Metrics reference](https://docs.galileo.ai/sdk-api/metrics/metrics) | [Set up AI Agent Monitoring](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring) |
| Configure metrics UI | [Log stream metrics](https://docs.galileo.ai/concepts/logging/configure-metrics/configure-metrics) | — |
| Signals / insights | [Simple Chatbot — Get insights](https://docs.galileo.ai/getting-started/sample-projects/simple-chatbot) | [Monitor AI traces](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/monitor-and-troubleshoot-ai-agents-and-applications/monitor-ai-traces-and-spans) |
| Agent Control | [Agent Control overview](https://docs.galileo.ai/concepts/agent-control/overview) | — |

---

## Lab root

**Lab root** is the directory where you cloned or copied this repository. Default folder name after clone: `GY-Splunk-Agent-Observability`.

```bash
git clone https://github.com/garrett-splunk/GY-Splunk-Agent-Observability.git
cd GY-Splunk-Agent-Observability
```

All commands below assume you are already in lab root unless noted otherwise.

---

## How to open lab files in Cursor

From lab root:

```bash
open -a Cursor FILENAME
```

Examples:

```bash
open -a Cursor app.py
open -a Cursor agent.py
open -a Cursor helpers/trace_lifecycle.py
open -a Cursor tools.py
```

In Cursor:

1. Press `Cmd+F` and search for `# INSTRUMENTATION`
2. Make the edits below
3. Save with `Cmd+S`
4. Restart Streamlit after each exercise block (`Ctrl+C`, then `streamlit run app.py`)

---

## Exercise 1 — Galileo project, log stream, and environment bootstrap

**Goal:** Create a Galileo project and log stream, point the lab at them in `config.yaml`, and confirm `setup_env.py` exports the right environment variables.

> **Concept:** A **project** is your app boundary; a **log stream** is where traces and metrics attach (like choosing which service/deployment slice in APM).  
> **Docs:** [Galileo log stream hierarchy](https://docs.galileo.ai/sdk-api/logging/logging-basics) · [Splunk AI Agent Monitoring setup](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring)

### Step 1a — Create a project and log stream in Galileo

1. Open your Galileo console (same URL as `galileo_console_url` in `.streamlit/secrets.toml`, e.g. `https://app.galileo.ai`).
2. **Create a project** (wording may vary by UI version):
   - Go to **Projects** → **New project** / **Create project**
   - Name it something memorable, e.g. `galileo-lab-it-helpdesk` or `your-name-it-helpdesk-lab`
   - Save / create the project
3. **Open the project**, then create or select a **log stream**:
   - Go to **Log streams** (or **Observability** → **Log streams**)
   - Create a new stream, e.g. `default` or `it-helpdesk-lab`
   - Note the **exact** project name and log stream name — they must match `config.yaml` character-for-character
4. If you have not already, copy your **API key** from **Settings** → **API keys** (or your org’s equivalent) into `.streamlit/secrets.toml` as `galileo_api_key`.

**Tip:** You can reuse the lab defaults (`galileo-lab-it-helpdesk` + `default`) if you create a project and stream with those exact names.

### Step 1b — Point the app at your project and log stream

**File:** `config.yaml`  
**Open:** `open -a Cursor config.yaml`

Edit the `galileo` block so `project` and `log_stream` match what you created in the console:

```yaml
galileo:
  project: "galileo-lab-it-helpdesk"   # your Galileo project name
  log_stream: "default"                # your log stream name
```

Save the file. No code changes are required in `setup_env.py` — it already reads these values (lines **50–52**, **72–73**).

**Data flow:**

| Source | Variable / usage |
|--------|------------------|
| `config.yaml` → `galileo.project` | `GALILEO_PROJECT` env var |
| `config.yaml` → `galileo.log_stream` | `GALILEO_LOG_STREAM` env var |
| Exercise 2 `GalileoLogger(...)` | Same names passed to the SDK |
| Streamlit sidebar | Displays project + log stream from config |

### Step 1c — Verify environment bootstrap

**File:** `setup_env.py` (optional inspect)  
**Open:** `open -a Cursor setup_env.py`

When `galileo_api_key` is set in `.streamlit/secrets.toml`, lines **65–78** add `GALILEO_API_KEY`, `GALILEO_PROJECT`, and `GALILEO_LOG_STREAM` automatically.

**Verify:**

```bash
source venv/bin/activate
python -c "from setup_env import setup_environment; setup_environment(); import os; print('project:', os.environ.get('GALILEO_PROJECT')); print('log_stream:', os.environ.get('GALILEO_LOG_STREAM'))"
```

Expected (if you kept lab defaults):

```
project: galileo-lab-it-helpdesk
log_stream: default
```

After `streamlit run app.py`, the sidebar should show the same project and log stream. Traces from Exercises 2–4 and demo scenarios land in that log stream in the Galileo console.

---

## Exercise 2 — Per-session logger

**File:** `app.py`  
**Open:** `open -a Cursor app.py`

> **Concept:** `GalileoLogger` sends LLM-native telemetry; `start_session` groups traces from one browser tab (session correlation).  
> **Docs:** [GalileoLogger](https://docs.galileo.ai/sdk-api/logging/galileo-logger) · Compare: [Splunk OTEL GenAI](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring/code-based-instrumentation)

### Step 2a — Uncomment import (~line 23)

Find `# INSTRUMENTATION (Exercise 2)`.

**Before:**

```python
# from galileo import GalileoLogger
```

**After:**

```python
from galileo import GalileoLogger
```

Leave the next commented `create_galileo_logger` line as-is.

### Step 2b — Replace `_create_galileo_logger` (~lines 40–52)

Remove the docstring (`""" ... """`) and delete `_ = config` / `return None`.

**Paste exactly:**

```python
def _create_galileo_logger(config: Dict[str, Any]):
    galileo_cfg = config.get("galileo", {})
    project = galileo_cfg.get("project", "galileo-lab-it-helpdesk")
    log_stream = galileo_cfg.get("log_stream", "default")
    if not os.environ.get("GALILEO_API_KEY"):
        return None
    return GalileoLogger(project=project, log_stream=log_stream)
```

### Step 2c — Replace `_start_galileo_session_if_needed` (~lines 55–69)

Remove the docstring and `_ = config`.

**Paste exactly:**

```python
def _start_galileo_session_if_needed(config: Dict[str, Any]) -> None:
    logger = st.session_state.get("galileo_logger")
    if logger and not st.session_state.galileo_session_started:
        ui = config.get("ui", {})
        title = ui.get("app_title", "IT Helpdesk Assistant Lab")
        logger.start_session(
            name=f"{title} Demo",
            external_id=st.session_state.session_id,
        )
        st.session_state.galileo_session_started = True
```

### Step 2d — Restart and verify

```bash
streamlit run app.py
```

Send a chat message → Galileo console shows a new session like `IT Helpdesk Assistant Lab Demo`.

**Reference:** `galileo-golden-demo/app.py` ~304–317 and ~1024–1076

---

## Exercise 3 — LangChain callback

**File:** `agent.py`  
**Open:** `open -a Cursor agent.py`

> **Concept:** `GalileoCallback` auto-instruments LangGraph LLM and tool steps into child spans — like auto-instrumentation for chains. Use `start_new_trace=False` to avoid duplicate root traces.  
> **Docs:** [LangChain / LangGraph integration](https://docs.galileo.ai/sdk-api/third-party-integrations/langchain/langchain)

### Step 3a — Uncomment import (~line 25)

**Before:**

```python
# from galileo.handlers.langchain import GalileoCallback
```

**After:**

```python
from galileo.handlers.langchain import GalileoCallback
```

### Step 3b — Replace `self.invoke_config` (~lines 60–72)

Find `# INSTRUMENTATION (Exercise 3)`.

**Delete this line:**

```python
        self.invoke_config = {"configurable": {"thread_id": self.session_id}}
```

**Uncomment the block above it so `__init__` contains:**

```python
        callbacks = [
            GalileoCallback(
                galileo_logger=galileo_logger,
                start_new_trace=False,
                flush_on_chain_end=False,
            )
        ]
        self.invoke_config = {
            "configurable": {"thread_id": self.session_id},
            "callbacks": callbacks,
        }
```

Keep `start_new_trace=False` and `flush_on_chain_end=False`.

**Reference:** `galileo-golden-demo/agent_frameworks/langgraph/agent.py` lines 219–230

---

## Exercise 4 — Trace boundary

**File:** `helpers/trace_lifecycle.py`  
**Open:** `open -a Cursor helpers/trace_lifecycle.py`

> **Concept:** One **trace** = one user query. `start_trace` opens the root; `conclude` + `flush` ship buffered spans to Galileo (explicit flush — not continuous like an OTEL collector).  
> **Docs:** [Logging basics — traces & spans](https://docs.galileo.ai/sdk-api/logging/logging-basics) · Splunk UI: [Monitor AI traces and spans](https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/monitor-and-troubleshoot-ai-agents-and-applications/monitor-ai-traces-and-spans)

### Step 4a — Replace `ensure_trace_started`

Remove the docstring and placeholder `_ = (galileo_logger, ...)`.

**Paste exactly:**

```python
def ensure_trace_started(
    galileo_logger,
    messages=None,
    *,
    trace_input: Optional[str] = None,
    trace_name: str = "Run Agent",
) -> None:
    if not galileo_logger or galileo_logger.current_parent() is not None:
        return
    if trace_input is None and messages is not None:
        trace_input = _extract_trace_input(messages)
    galileo_logger.start_trace(input=trace_input or "", name=trace_name)
```

### Step 4b — Replace `finalize_trace`

**Paste exactly:**

```python
def finalize_trace(galileo_logger, output: str) -> None:
    if not galileo_logger or galileo_logger.current_parent() is None:
        return
    galileo_logger.conclude(output=output)
    galileo_logger.flush()
```

`agent.py` already calls these (lines ~133–151) — no changes needed there.

Restart Streamlit. Each chat turn should produce one root trace named **Run Agent**.

**Reference:** `galileo-golden-demo/helpers/agent_control_helpers.py` lines 115–135

---

## Exercise 5 — Named LLM spans (verify only)

**File:** `helpers/llm.py`  
**Open:** `open -a Cursor helpers/llm.py`

Confirm lines ~34 and ~44 pass `name=name` to `ChatOpenAI` / `ChatOllama`. After Exercise 3, LLM spans should show **IT Helpdesk Assistant**.

**Reference:** `galileo-golden-demo/helpers/llm_utils.py`

---

## Exercise 6 — Optional manual tool spans

**File:** `tools.py`  
**Open:** `open -a Cursor tools.py`

In `_log_tool_span` (~line 31), remove the docstring and placeholder line.

**Paste exactly:**

```python
def _log_tool_span(name: str, tool_input: str, tool_output: str, duration_ns: int) -> None:
    if not _galileo_logger:
        return
    _galileo_logger.add_tool_span(
        input=tool_input,
        output=tool_output,
        name=name,
        duration_ns=duration_ns,
        status_code=200,
    )
```

**Reference:** `galileo-golden-demo/domains/healthcare/tools/logic.py` `_log_tool_span`

---

## Exercise 7 — Verification checklist

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

## After instrumentation — Galileo console (Steps 10–13)

Workshop site: [Step 10 Configure metrics](https://garrett-splunk.github.io/GY-Splunk-Agent-Observability/#step-metrics) (screenshots: Configure Metrics → Apply → Compute)

| Step | What to do |
|------|------------|
| **10** | Enable Prompt Injection, Context Adherence, Chunk Attribution on log stream; **Compute** backfill on Acts 1–3 |
| **11** | Verify metric scores on hallucination and injection traces |
| **12** | Run **Log Stream Insights** / **Signals**; review suggested fixes |
| **13** (optional) | Enable Agent Control in `config.yaml`; create `block-prompt-injection` control; replay Act 3 |

---

## Future path: Splunk OTEL GenAI

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
