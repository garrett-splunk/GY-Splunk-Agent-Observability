# Demo Script (~5 minutes)

Use this script when presenting Splunk Agent Observability (Galileo) agent observability with the IT Helpdesk lab app.

**Before you start:**

1. `streamlit run app.py` running at http://localhost:8501
2. Splunk Agent Observability (Galileo) console open → project and log stream from `config.yaml`
3. Complete INSTRUMENTATION exercises 1–4 for live agent traces (hallucination button works independently)
4. **Step 10:** Enable log stream metrics (Configure Metrics → toggle → Compute backfill)
5. Optional: second monitor with Splunk Agent Observability (Galileo) trace detail view

---

## Configure metrics (Step 10 — before verify and Signals)

In Splunk Agent Observability (Galileo) → **Projects** → your project → **Log streams** → your stream:

| Substep | Action |
|---------|--------|
| **10a** | Click **Configure Metrics** (top right). Requires at least one session — run Acts 1–3 first. |
| **10b** | Toggle on the metrics below → **Save and close** |
| **10c** | Click **Compute** to score traces already logged from lab prompts |

Workshop screenshots: `workshop/screenshots/configure-metrics.png`, `apply.png`, `compute.png`

| Metric | Act | Notes |
|--------|-----|-------|
| **Prompt Injection** (SML) | 3 | Scores malicious user input on LLM `input` path |
| **Context Adherence** | 2 | Flags LLM output that contradicts retriever context |
| **Chunk Attribution Utilization** | 2 | Shows poor use of retrieved chunks |

Validate export from terminal:

```bash
python scripts/validate_galileo_traces.py
```

Skip **Ground Truth Adherence** unless you run batch experiments with a CSV dataset.

Official: [Configure log stream metrics](https://docs.galileo.ai/concepts/logging/configure-metrics/configure-metrics)

## Act 1 — Normal operation (happy path)

**Story:** “First, a typical employee asks about a support ticket.”

1. In the sidebar under **Act 1 — Happy path**, click **Look up ticket T-1001**
2. Agent calls `lookup_ticket` and returns VPN issue details
3. Switch to Splunk Agent Observability (Galileo) → open the new trace

**Point out:**

- Root trace `Run Agent`
- LLM span deciding to use a tool
- Tool span for `lookup_ticket`
- Final LLM synthesis

**Optional second query:** “How do I reset my VPN password?” → `search_kb` tool + KB article content

---

## Act 2 — Hallucination

**Story:** “Models can sound confident while contradicting retrieved context.”

1. Sidebar → **Act 2 — Hallucination**
2. Click **Log Hallucination to Splunk Agent Observability (Galileo)**
3. Open the new trace in Splunk Agent Observability (Galileo)

**Point out:**

- **Retriever span** — context says P1 SLA: 15 min response, 4 hr resolution
- **LLM span** — output claims 24 hr response, 5 day resolution
- Grounding / **Context Adherence** and **Chunk Attribution** metrics flag this mismatch (if enabled on log stream)

**Talking point:** Edit `demo_hallucinations` in [`config.yaml`](config.yaml) to tailor stories for your audience (healthcare, finance, etc.) without code changes.

**Compare:** Golden demo uses the same pattern in `helpers/hallucination_helpers.py`.

---

## Act 3 — Prompt injection

**Story:** “Attackers try to override system instructions or exfiltrate secrets.”

1. Sidebar → **Act 3 — Prompt injection**
2. Click **Ignore instructions** (or another chip)
3. Review the prefilled payload in chat — **send intentionally**
4. Show the trace input capturing the malicious prompt

**Point out:**

- Full injection text preserved in trace input
- Agent should refuse or stay within policy (depends on model)
- **Prompt Injection** metric should score high on the malicious input (if enabled on log stream)

**Demo tip:** Chips prefill but do not auto-send — you control the moment.

---

## Use Signals (Step 12 — after metrics Compute)

**Story:** “Splunk Agent Observability (Galileo) analyzes scored traces and suggests how to fix recurring failures.”

1. Open log stream with Act 2 and Act 3 metric scores visible (Step 10c Compute finished)
2. Click **Log Stream Insights** or **Signals**
3. Review insights panel: summaries, root-cause analysis, remediation suggestions
4. Click an insight example → jump to affected traces/spans

**Point out:**

- Act 2 hallucination patterns → prompt/grounding improvements
- Act 3 injection patterns → input validation or Agent Control (Step 13)
- Act 1 healthy traces as baseline contrast

**Reference:** [Simple Chatbot — Get insights](https://docs.galileo.ai/getting-started/sample-projects/simple-chatbot)

---

## Step 13 — Agent Control guardrails (optional)

When you want **denial**, not just observability:

1. Install dependencies (includes Agent Control SDK):
   ```bash
   pip install -r requirements.txt
   ```
2. In [`config.yaml`](config.yaml), set:
   ```yaml
   galileo:
     enable_agent_control: true
   ```
3. Optional in `.streamlit/secrets.toml`:
   ```toml
   agent_control_agent_name = "it-helpdesk-assistant"
   ```
4. Restart Streamlit — sidebar shows **Agent Control enabled**
5. In Splunk Agent Observability (Galileo) UI → Project → Log Stream → **Controls**:
   - Create **`block-prompt-injection`** (PRE, Deny, llm step, Prompt Injection SML ≥ 0.80, path: `input`)
   - **Attach** to log stream; use enable/disable toggle for demo pacing
6. **Observe:** Act 3 with control disabled — Prompt Injection metric fails on input
7. **Enforce:** Enable control → replay Act 3 — guardrail blocks with visible evaluation span

**Reference:** `galileo-golden-demo/README.md` section on `block-prompt-injection` (~lines 470–484) · [Agent Control overview](https://docs.galileo.ai/concepts/agent-control/overview)

---

## Customizing scenarios

Edit [`config.yaml`](config.yaml):

```yaml
demo_hallucinations:
  - question: "Your question"
    context:
      - "Ground truth the model should follow"
    hallucinated_answer: "Wrong but plausible answer"

demo_prompt_injections:
  - label: "Short label for button"
    prompt: "Full injection text to prefill"
```

Restart Streamlit after config changes.

---

## Fallback if LLM is unavailable

- **Hallucination button** still works (synthetic trace, no live LLM)
- Show golden demo (`galileo-golden-demo` clone) for full multi-domain story
- Walk through INSTRUMENTATION.md comment blocks as a “build observability” narrative
