"""
IT Helpdesk tools — in-memory ticket lookup and KB search.

INSTRUMENTATION (Exercise 6 — optional):
  After each tool executes, call galileo_logger.add_tool_span(...) for explicit
  span metadata beyond Splunk Agent Observability (Galileo) auto-instrumentation (GalileoCallback).
  Reference: ~/Desktop/galileo-golden-demo/domains/healthcare/tools/logic.py _log_tool_span
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

TICKETS_PATH = Path(__file__).parent / "data" / "tickets.json"
KB_PATH = Path(__file__).parent / "data" / "kb.json"

_galileo_logger: Optional[Any] = None


def set_galileo_logger(logger) -> None:
    """Called from app.py once a per-session GalileoLogger exists."""
    global _galileo_logger
    _galileo_logger = logger


def _load_json(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _log_tool_span(name: str, tool_input: str, tool_output: str, duration_ns: int) -> None:
    """
    INSTRUMENTATION (Exercise 6 — optional): uncomment to emit manual tool spans.

    if not _galileo_logger:
        return
    _galileo_logger.add_tool_span(
        input=tool_input,
        output=tool_output,
        name=name,
        duration_ns=duration_ns,
        status_code=200,
    )
    """
    _ = (name, tool_input, tool_output, duration_ns, _galileo_logger)


def lookup_ticket(ticket_id: str) -> str:
    """Look up a support ticket by ID (e.g. T-1001). Returns ticket details as JSON."""
    start = time.perf_counter_ns()
    tickets = _load_json(TICKETS_PATH)
    normalized = ticket_id.strip().upper()
    match = next((t for t in tickets if t["ticket_id"].upper() == normalized), None)
    if not match:
        result = json.dumps({"error": f"Ticket {ticket_id} not found."})
    else:
        public = {
            "ticket_id": match["ticket_id"],
            "title": match["title"],
            "status": match["status"],
            "priority": match["priority"],
            "assignee": match["assignee"],
            "summary": match["summary"],
        }
        result = json.dumps(public, indent=2)

    duration_ns = time.perf_counter_ns() - start
    _log_tool_span("lookup_ticket", ticket_id, result, duration_ns)
    return result


def search_kb(query: str) -> str:
    """Search the IT knowledge base for articles matching the query."""
    start = time.perf_counter_ns()
    articles = _load_json(KB_PATH)
    query_lower = query.lower()
    tokens = [t for t in query_lower.replace("?", " ").split() if len(t) > 2]

    scored: List[tuple[int, Dict[str, Any]]] = []
    for article in articles:
        haystack = " ".join(
            [article.get("title", ""), article.get("content", ""), " ".join(article.get("keywords", []))]
        ).lower()
        score = sum(1 for token in tokens if token in haystack)
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        result = json.dumps({"results": [], "message": "No matching KB articles found."})
    else:
        top = [
            {"id": a["id"], "title": a["title"], "content": a["content"]}
            for _, a in scored[:2]
        ]
        result = json.dumps({"results": top}, indent=2)

    duration_ns = time.perf_counter_ns() - start
    _log_tool_span("search_kb", query, result, duration_ns)
    return result


TOOLS = [lookup_ticket, search_kb]
