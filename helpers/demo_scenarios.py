"""
Demo scenario helpers — hallucination traces and prompt-injection utilities.

This module is a **working reference** for manual Galileo spans (retriever + LLM).
Use it alongside the INSTRUMENTATION exercises for callback-based agent tracing.

Reference: ~/Desktop/galileo-golden-demo/helpers/hallucination_helpers.py
"""
import os
import uuid
from typing import Any, Dict, List, Optional


def _galileo_configured() -> bool:
    key = os.environ.get("GALILEO_API_KEY", "")
    return bool(key and key not in ("...", ""))


def create_galileo_logger(project_name: str, log_stream: str):
    """Create a GalileoLogger when GALILEO_API_KEY is configured."""
    if not _galileo_configured():
        return None
    from galileo import GalileoLogger

    return GalileoLogger(project=project_name, log_stream=log_stream)


def log_hallucination(
    project_name: str,
    log_stream: str,
    question: str,
    context_docs: List[str],
    hallucinated_answer: str,
    *,
    model: str = "gemma4",
    session_name: str = "Hallucination Demo",
    existing_logger=None,
) -> bool:
    """
    Log an intentional hallucination trace for demos.

    Span lifecycle (manual API — compare to GalileoCallback in agent.py):
      start_trace → add_retriever_span → add_llm_span → conclude → flush
    """
    if not _galileo_configured():
        print("⚠️  Set galileo_api_key in .streamlit/secrets.toml to log hallucinations")
        return False

    try:
        if existing_logger:
            galileo_logger = existing_logger
        else:
            galileo_logger = create_galileo_logger(project_name, log_stream)
            if galileo_logger is None:
                return False
            session_id = str(uuid.uuid4())[:10]
            galileo_logger.start_session(name=session_name, external_id=session_id)

        galileo_logger.start_trace(input=question, name="Hallucination Demo")

        # INSTRUMENTATION note: retriever span shows grounding context evaluators compare against
        galileo_logger.add_retriever_span(
            input=question,
            output=context_docs,
            name="KB Retrieval",
            duration_ns=int(1.3e8),
            status_code=200,
        )

        context_text = "\n\n".join(context_docs)
        llm_input = (
            f"Given the context below, answer the question.\n\n"
            f"{context_text}\n\nQuestion: {question}"
        )

        # INSTRUMENTATION note: LLM span carries the intentionally wrong answer for demo
        galileo_logger.add_llm_span(
            input=llm_input,
            output=hallucinated_answer,
            model=model,
            name="LLM Response",
            metadata={"demo_type": "hallucination", "temperature": "0.1"},
            temperature=0.1,
            status_code=200,
        )

        galileo_logger.conclude(output=hallucinated_answer)
        galileo_logger.flush()
        return True
    except Exception as exc:
        print(f"Failed to log hallucination: {exc}")
        return False


def log_hallucination_from_config(
    config: Dict[str, Any],
    *,
    hallucination_index: int = 0,
    existing_logger=None,
    model: str = "gemma4",
) -> bool:
    """Read demo_hallucinations from config.yaml and log the selected example."""
    galileo_cfg = config.get("galileo", {})
    project_name = galileo_cfg.get("project", "galileo-lab-it-helpdesk")
    log_stream = galileo_cfg.get("log_stream", "default")

    examples = config.get("demo_hallucinations", [])
    if not examples:
        print("No demo_hallucinations defined in config.yaml")
        return False

    idx = min(hallucination_index, len(examples) - 1)
    example = examples[idx]
    question = example.get("question", "")
    hallucinated_answer = example.get("hallucinated_answer", "")
    context_docs = example.get("context", [])
    if not question or not hallucinated_answer:
        return False

    return log_hallucination(
        project_name=project_name,
        log_stream=log_stream,
        question=question,
        context_docs=context_docs,
        hallucinated_answer=hallucinated_answer,
        model=model,
        session_name="IT Helpdesk Hallucination Demo",
        existing_logger=existing_logger,
    )


def get_prompt_injection_examples(config: Dict[str, Any]) -> List[Dict[str, str]]:
    return list(config.get("demo_prompt_injections", []))


def get_hallucination_chat_turn(config: Dict[str, Any], index: int = 0) -> Optional[Dict[str, str]]:
    examples = config.get("demo_hallucinations", [])
    if not examples or index >= len(examples):
        return None
    ex = examples[index]
    question = ex.get("question", "")
    answer = ex.get("hallucinated_answer", "")
    if not question or not answer:
        return None
    return {"question": question, "answer": answer}
