#!/usr/bin/env python3
"""
Validate Galileo trace export for workshop demo acts.

Run from lab root with venv active:
  python scripts/validate_galileo_traces.py

After traces export, confirm metric scores in Galileo UI on log stream metrics:
  - Prompt Injection (Act 3)
  - Context Adherence (Act 2)
  - Chunk Attribution Utilization (Act 2)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setup_env import setup_environment
from helpers.demo_scenarios import log_hallucination_from_config


def main() -> int:
    config = setup_environment()
    project = os.environ.get("GALILEO_PROJECT", "n/a")
    log_stream = os.environ.get("GALILEO_LOG_STREAM", "n/a")
    console = os.environ.get("GALILEO_CONSOLE_URL", "n/a")

    print("Galileo target:")
    print(f"  project:    {project}")
    print(f"  log_stream: {log_stream}")
    print(f"  console:    {console}")
    print()

    if not os.environ.get("GALILEO_API_KEY"):
        print("FAIL: GALILEO_API_KEY not set — configure secrets.toml first")
        return 1

    print("Act 2 — logging hallucination trace...")
    ok = log_hallucination_from_config(config)
    if not ok:
        print("FAIL: hallucination trace did not export")
        return 1
    print("OK: hallucination trace exported")
    print()
    print("Next steps (manual):")
    print(f"  1. Open {console}")
    print(f"  2. Project → {project} → Log stream → {log_stream}")
    print("  3. Confirm hallucination trace with retriever + LLM spans")
    print("  4. Check Context Adherence and Chunk Attribution scores (if metrics enabled)")
    print()
    print("Act 3 — send a prompt-injection chip in Streamlit, then check Prompt Injection score")
    print("Act 1 — send 'Look up ticket T-1001' and confirm agent trace spans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
