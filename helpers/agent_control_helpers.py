"""
Agent Control helpers — optional Phase 2 guardrails for the IT Helpdesk lab.

Enable with galileo.enable_agent_control: true in config.yaml and create
block-prompt-injection on the log stream in the Splunk Agent Observability (Galileo) UI.
"""
import os

import agent_control
from agent_control.settings import configure_settings
from galileo.log_streams import get_log_stream

from helpers.llm import SPAN_NAME

_initialized = False

IT_HELPDESK_AGENT_CONTROL_STEPS = [
    {"type": "llm", "name": SPAN_NAME},
    {"type": "tool", "name": "lookup_ticket"},
    {"type": "tool", "name": "search_kb"},
]

BLOCKED_MESSAGE = (
    "I'm sorry, this request was blocked by Agent Control. "
    "Please rephrase your question or try a different approach."
)


def init_agent_control(
    galileo_logger,
    project_name: str,
    log_stream: str,
    *,
    agent_description: str = "IT Helpdesk assistant lab agent",
    force: bool = False,
) -> bool:
    """Initialize Agent Control for the current Splunk Agent Observability (Galileo) logger/session."""
    global _initialized

    if galileo_logger is None:
        print("⚠️  Agent Control not initialized (no Splunk Agent Observability (Galileo) logger)")
        return False

    server_url = os.environ.get("AGENT_CONTROL_URL")
    agent_name = os.environ.get("AGENT_CONTROL_AGENT_NAME")
    api_key = os.environ.get("GALILEO_API_KEY")
    api_key_header = os.environ.get("AGENT_CONTROL_API_KEY_HEADER", "Galileo-API-Key")

    if not all([server_url, agent_name, api_key]):
        print(
            "⚠️  Agent Control not configured "
            "(set AGENT_CONTROL_URL, AGENT_CONTROL_AGENT_NAME, and GALILEO_API_KEY)"
        )
        return False

    session_key = (agent_name, project_name, log_stream, server_url)
    if not force and getattr(init_agent_control, "_last_session_key", None) == session_key:
        return True

    try:
        log_stream_data = get_log_stream(name=log_stream, project_name=project_name)
    except Exception as exc:
        print(f"⚠️  Agent Control: failed to resolve log stream '{log_stream}': {exc}")
        return False

    configure_settings(
        url=server_url,
        api_key=api_key,
        api_key_header=api_key_header,
    )

    agent_control.init(
        agent_name=agent_name,
        agent_description=agent_description,
        server_url=server_url,
        api_key=api_key,
        api_key_header=api_key_header,
        observability_enabled=True,
        observability_sink_name="registered",
        target_type="log_stream",
        target_id=log_stream_data.id,
        steps=IT_HELPDESK_AGENT_CONTROL_STEPS,
    )
    _initialized = True
    init_agent_control._last_session_key = session_key
    print(
        f"✅ Agent Control initialized for '{agent_name}' "
        f"(project={project_name}, log_stream={log_stream})"
    )
    return True
