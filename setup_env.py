"""
Environment setup — load secrets and set environment variables.

INSTRUMENTATION (Exercise 1):
  Wire Splunk Agent Observability (Galileo) env vars from .streamlit/secrets.toml so the SDK can export traces.
  Reference: ~/Desktop/galileo-golden-demo/setup_env.py lines 56–140
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import toml
import yaml


def _derive_galileo_api_url(console_url: str, explicit_url: str = "") -> str:
    if explicit_url:
        return explicit_url.rstrip("/")
    console_url = (console_url or "").rstrip("/")
    if not console_url:
        return ""
    if "console." in console_url:
        return console_url.replace("console.", "api.", 1)
    return ""


def _derive_agent_control_url(console_url: str, explicit_url: str = "") -> str:
    if explicit_url:
        return explicit_url.rstrip("/")
    console_url = (console_url or "").rstrip("/")
    if not console_url:
        return ""
    return f"{console_url}/api/agent-control"


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    path = config_path or Path(__file__).parent / "config.yaml"
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def setup_environment(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load secrets and config; set process env vars for LLM + Splunk Agent Observability (Galileo)."""
    config = config or load_config()
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"

    if not secrets_path.exists():
        print("⚠️  .streamlit/secrets.toml not found. Copy from secrets.toml.example")

    secrets: Dict[str, Any] = {}
    if secrets_path.exists():
        secrets = toml.load(secrets_path)

    console_url = secrets.get("galileo_console_url", "https://app.galileo.ai")
    galileo_api_url = _derive_galileo_api_url(
        console_url, secrets.get("galileo_api_url", "")
    )

    galileo_cfg = config.get("galileo", {})
    project_name = galileo_cfg.get("project", "galileo-lab-it-helpdesk")
    log_stream = galileo_cfg.get("log_stream", "default")

    env_vars = {
        "OLLAMA_BASE_URL": secrets.get("ollama_base_url", "http://localhost:11434"),
        "OLLAMA_DEFAULT_CHAT_MODEL": secrets.get(
            "ollama_default_chat_model", "gemma4"
        ),
        "OPENAI_API_KEY": secrets.get("openai_api_key", ""),
        "OPENAI_DEFAULT_CHAT_MODEL": secrets.get(
            "openai_default_chat_model", "gpt-4o"
        ),
    }

    galileo_api_key = secrets.get("galileo_api_key", "")
    if galileo_api_key and galileo_api_key not in ("...", ""):
        agent_control_url = _derive_agent_control_url(
            console_url, secrets.get("agent_control_url", "")
        )
        env_vars.update(
            {
                "GALILEO_API_KEY": galileo_api_key,
                "GALILEO_API_URL": galileo_api_url,
                "GALILEO_CONSOLE_URL": console_url,
                "GALILEO_PROJECT": project_name,
                "GALILEO_LOG_STREAM": log_stream,
                "AGENT_CONTROL_URL": agent_control_url,
                "AGENT_CONTROL_API_KEY": galileo_api_key,
                "AGENT_CONTROL_AGENT_NAME": secrets.get(
                    "agent_control_agent_name", "it-helpdesk-assistant"
                ),
                "AGENT_CONTROL_API_KEY_HEADER": secrets.get(
                    "agent_control_api_key_header", "Galileo-API-Key"
                ),
            }
        )
    else:
        # INSTRUMENTATION (Exercise 1): ensure these are set once galileo_api_key is configured
        print("⚠️  GALILEO_API_KEY not set — traces will not export until Exercise 1 is complete")

    for key, value in env_vars.items():
        if value:
            os.environ[key] = str(value)

    return config


if __name__ == "__main__":
    setup_environment()
