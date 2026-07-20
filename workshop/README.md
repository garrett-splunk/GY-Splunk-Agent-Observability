# Splunk Agent Observability (Galileo) Assistant Lab — Workshop Site

Interactive step-by-step guide for the IT Helpdesk instrumentation lab. Same Splunk workshop theme as the Oracle DB and Kubernetes OTel labs.

**Live site:** https://garrett-splunk.github.io/GY-Splunk-Agent-Observability/

## Lab root

Use the folder where you cloned or copied this repository. After `git clone`, the default name is **`GY-Splunk-Agent-Observability`**.

```bash
git clone https://github.com/garrett-splunk/GY-Splunk-Agent-Observability.git
cd GY-Splunk-Agent-Observability
```

## Open locally

```bash
cd workshop
python3 -m http.server 8095
# browse http://localhost:8095
```

Or: `open index.html` (from the `workshop/` folder)

Run the **app** separately (from lab root, different port):

```bash
source venv/bin/activate
streamlit run app.py
# browse http://localhost:8501
```

## Files

| File | Purpose |
|------|---------|
| `index.html` | Participant walkthrough (sidebar + copy buttons) |
| `WORKSHOP_GUIDE.md` | Facilitator cheat sheet |
| `styles.css` | Splunk workshop theme |
| `app.js` | Theme toggle, progress bar, sidebar nav |

## Facilitators

See [`WORKSHOP_GUIDE.md`](WORKSHOP_GUIDE.md) for timing, talking points, and troubleshooting.

Participant docs in the repo root: [`../README.md`](../README.md), [`../INSTRUMENTATION.md`](../INSTRUMENTATION.md), [`../DEMO.md`](../DEMO.md).
