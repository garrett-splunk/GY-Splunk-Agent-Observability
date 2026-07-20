"""
IT Helpdesk Assistant Lab — Streamlit UI with demo scenario sidebar.

INSTRUMENTATION (Exercise 2):
  Create a per-session GalileoLogger and call start_session on first user message.
  Reference: ~/Desktop/galileo-golden-demo/app.py ~304–317 and ~1024–1076
"""
import os
import uuid
from typing import Any, Dict, List, Optional

import streamlit as st

from agent import ITHelpdeskAgent
from helpers.demo_scenarios import (
    get_hallucination_chat_turn,
    get_prompt_injection_examples,
    log_hallucination_from_config,
)
from setup_env import load_config, setup_environment

# INSTRUMENTATION (Exercise 2): uncomment when wiring per-session logger
from galileo import GalileoLogger


def _init_session_state(config: Dict[str, Any]) -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:10]
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "galileo_session_started" not in st.session_state:
        st.session_state.galileo_session_started = False
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = ""
    if "galileo_logger" not in st.session_state:
        st.session_state.galileo_logger = _create_galileo_logger(config)


def _create_galileo_logger(config: Dict[str, Any]):
    galileo_cfg = config.get("galileo", {})
    project = galileo_cfg.get("project", "galileo-lab-it-helpdesk")
    log_stream = galileo_cfg.get("log_stream", "default")
    if not os.environ.get("GALILEO_API_KEY"):
        return None
    return GalileoLogger(project=project, log_stream=log_stream)


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


def _render_demo_sidebar(config: Dict[str, Any]) -> None:
    ui = config.get("ui", {})
    st.subheader("Demo Scenarios")

    st.markdown("**Act 1 — Happy path**")
    for query in ui.get("example_queries", []):
        if st.button(query, key=f"example_{query[:24]}"):
            st.session_state.pending_prompt = query

    if config.get("demo_hallucinations"):
        st.divider()
        st.markdown("**Act 2 — Hallucination**")
        st.caption("Logs a synthetic trace with correct context but wrong LLM answer.")
        if st.button("Log Hallucination to Galileo", key="log_hallucination"):
            with st.spinner("Logging hallucination to Galileo..."):
                existing = (
                    st.session_state.get("galileo_logger")
                    if st.session_state.get("galileo_session_started")
                    else None
                )
                model = config.get("model", {}).get("default_model", "gemma4")
                success = log_hallucination_from_config(
                    config,
                    existing_logger=existing,
                    model=model,
                )
                if success:
                    turn = get_hallucination_chat_turn(config)
                    if turn:
                        st.session_state.messages.append(
                            {"role": "user", "content": turn["question"]}
                        )
                        st.session_state.messages.append(
                            {"role": "assistant", "content": turn["answer"]}
                        )
                    st.success("Hallucination logged — open Galileo console to compare context vs output.")
                    st.rerun()
                else:
                    st.error("Failed to log hallucination. Check secrets and INSTRUMENTATION.md.")

    injections = get_prompt_injection_examples(config)
    if injections:
        st.divider()
        st.markdown("**Act 3 — Prompt injection**")
        st.caption("Prefills chat input; review then send intentionally.")
        for item in injections:
            label = item.get("label", "Injection")
            if st.button(label, key=f"inject_{label}"):
                st.session_state.pending_prompt = item.get("prompt", "")


def _render_chat(config: Dict[str, Any], provider: str, model: Optional[str]) -> None:
    ui = config.get("ui", {})
    icon = ui.get("icon", "🎫")
    title = ui.get("app_title", "IT Helpdesk Assistant Lab")
    st.title(f"{icon} {title}")
    st.caption("Instrumentation lab — complete exercises in INSTRUMENTATION.md")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask about tickets or IT policies...")
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = ""

    if prompt:
        _start_galileo_session_if_needed(config)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        agent = ITHelpdeskAgent(
            config,
            session_id=st.session_state.session_id,
            galileo_logger=st.session_state.get("galileo_logger"),
            llm_provider=provider,
            model_override=model or None,
        )
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = agent.process_query(st.session_state.messages)
                except Exception as exc:
                    response = f"Error: {exc}"
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


def main() -> None:
    st.set_page_config(page_title="Galileo Assistant Lab", layout="wide")
    config = setup_environment()
    _init_session_state(config)

    with st.sidebar:
        st.header("Settings")
        provider = st.radio(
            "Model provider",
            options=["local", "hosted"],
            format_func=lambda x: "Local (Ollama)" if x == "local" else "Hosted (OpenAI)",
            horizontal=True,
        )
        model_cfg = config.get("model", {})
        if provider == "hosted":
            default_model = model_cfg.get("hosted_default_model", "gpt-4o")
        else:
            default_model = model_cfg.get("default_model", "gemma4")
        model = st.text_input("Model name", value=default_model)

        galileo_cfg = config.get("galileo", {})
        st.divider()
        st.markdown("**Galileo target**")
        st.text(f"Project: {galileo_cfg.get('project', 'n/a')}")
        st.text(f"Log stream: {galileo_cfg.get('log_stream', 'n/a')}")
        if os.environ.get("GALILEO_API_KEY"):
            st.success("Galileo API key loaded")
        else:
            st.warning("Galileo not configured — see Exercise 1")

        st.divider()
        _render_demo_sidebar(config)

    _render_chat(config, provider, model.strip() or None)


if __name__ == "__main__":
    main()
