# Galileo Assistant Lab — Workshop Site

Interactive step-by-step guide for the IT Helpdesk instrumentation lab. Same Splunk workshop theme as the Oracle DB and Kubernetes OTel labs.

**Live site:** https://garrett-splunk.github.io/GY-Splunk-Agent-Observability/

## Open locally

```bash
cd ~/Desktop/galileo-assistant-lab/workshop
open index.html
```

Or serve over HTTP (recommended for copy-to-clipboard in some browsers):

```bash
cd ~/Desktop/galileo-assistant-lab/workshop
python3 -m http.server 8095
# browse http://localhost:8095
```

Run the **app** separately (different port):

```bash
cd ~/Desktop/galileo-assistant-lab
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
