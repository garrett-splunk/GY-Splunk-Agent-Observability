# Demo Script (~5 minutes)

Use this script when presenting Galileo agent observability with the IT Helpdesk lab app.

**Before you start:**

1. `streamlit run app.py` running at http://localhost:8501
2. Galileo console open → project and log stream from `config.yaml`
3. Complete INSTRUMENTATION exercises 1–4 for live agent traces (hallucination button works independently)
4. **Step 10:** Enable log stream metrics (Prompt Injection, Context Adherence, Chunk Attribution Utilization)
5. Optional: second monitor with Galileo trace detail view

---

## Configure metrics (before demos)

In Galileo → **Projects** → your project → **Log streams** → your stream → **Metrics**:

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

---

## Act 1 — Normal operation (happy path)

**Story:** “First, a typical employee asks about a support ticket.”

1. In the sidebar under **Act 1 — Happy path**, click **Look up ticket T-1001**
2. Agent calls `lookup_ticket` and returns VPN issue details
3. Switch to Galileo → open the new trace

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
2. Click **Log Hallucination to Galileo**
3. Open the new trace in Galileo

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

## Phase 2 — Live guardrail blocking (optional)

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
4. Restart Streamlit — sidebar shows **Agent Control enabled (Phase 2)**
5. In Galileo UI → Project → Log Stream → **Controls**, create **`block-prompt-injection`**:
   - Stage: PRE
   - Action: Deny
   - Step types: llm
   - Evaluator: Prompt Injection (SML), threshold ≥ 0.80, path: input

6. Replay Act 3 — guardrail blocks with visible evaluation span

**Reference:** `galileo-golden-demo/README.md` section on `block-prompt-injection` (~lines 470–484)

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
