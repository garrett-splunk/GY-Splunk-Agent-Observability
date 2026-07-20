"""
Trace lifecycle helpers — start and finish Galileo traces around agent runs.

INSTRUMENTATION (Exercise 4):
  Implement ensure_trace_started() and finalize_trace() using GalileoLogger APIs.
  Reference: ~/Desktop/galileo-golden-demo/helpers/agent_control_helpers.py lines 115–135
"""


def _extract_trace_input(messages: Any) -> str:
    if isinstance(messages, str):
        return messages
    if isinstance(messages, list):
        parts = []
        for msg in messages:
            if hasattr(msg, "content"):
                parts.append(str(getattr(msg, "content", "")))
            elif isinstance(msg, dict):
                parts.append(str(msg.get("content", "")))
        return "\n".join(part for part in parts if part)
    return str(messages)


def ensure_trace_started(
    galileo_logger,
    messages=None,
    *,
    trace_input: Optional[str] = None,
    trace_name: str = "Run Agent",
) -> None:
    """Start a Galileo trace when none is active (required before LLM/tool spans)."""
    if not galileo_logger or galileo_logger.current_parent() is not None:
        return
    if trace_input is None and messages is not None:
        trace_input = _extract_trace_input(messages)
    galileo_logger.start_trace(input=trace_input or "", name=trace_name)


def finalize_trace(galileo_logger, output: str) -> None:
    """Conclude and flush the active trace after a query completes."""
    if not galileo_logger or galileo_logger.current_parent() is None:
        return
    galileo_logger.conclude(output=output)
    galileo_logger.flush()
