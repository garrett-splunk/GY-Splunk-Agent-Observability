#!/usr/bin/env python3
"""
Ensure block-prompt-injection is attached to the lab log stream (Phase 2 / Step 13).

Usage (from lab root, venv active):
  python scripts/setup_phase2_control.py              # verify only
  python scripts/setup_phase2_control.py --enable     # enable binding for enforce demo
  python scripts/setup_phase2_control.py --disable    # disable binding for observe-only demo

Requires GALILEO_API_KEY and galileo project/log_stream in config.yaml.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from galileo.log_streams import get_log_stream
from setup_env import setup_environment

CONTROL_NAME = "block-prompt-injection"
SOURCE_CONTROL_ID = 12  # global template in multitenant org


async def _find_attached_control(client, log_stream_id: str) -> dict | None:
    response = await client.http_client.get(
        "/api/v1/controls",
        params={
            "name": "block-prompt-injection",
            "include_attachments": True,
            "attachment_target_type": "log_stream",
            "attachment_target_id": log_stream_id,
            "limit": 20,
        },
    )
    response.raise_for_status()
    controls = response.json().get("controls", [])
    return controls[0] if controls else None


async def _attach_control(log_stream_id: str) -> dict:
    import agent_control

    return await agent_control.clone_and_bind_control(
        SOURCE_CONTROL_ID,
        target_type="log_stream",
        target_id=log_stream_id,
        enabled=False,
    )


async def _set_binding_enabled(client, control_id: int, log_stream_id: str, enabled: bool) -> None:
    from agent_control.control_bindings import update_control_binding_by_key

    await update_control_binding_by_key(
        client,
        target_type="log_stream",
        target_id=log_stream_id,
        control_id=control_id,
        enabled=enabled,
    )


async def run(enable: bool | None) -> int:
    from agent_control.client import AgentControlClient

    config = setup_environment()
    if not os.environ.get("GALILEO_API_KEY"):
        print("FAIL: GALILEO_API_KEY not set — configure secrets.toml first")
        return 1
    project = config["galileo"]["project"]
    log_stream = config["galileo"]["log_stream"]
    ls = get_log_stream(name=log_stream, project_name=project)
    log_stream_id = ls.id

    print("Phase 2 control target:")
    print(f"  project:     {project}")
    print(f"  log_stream:  {log_stream}")
    print(f"  stream id:   {log_stream_id}")
    print()

    async with AgentControlClient(
        base_url=os.environ["AGENT_CONTROL_URL"],
        api_key=os.environ["GALILEO_API_KEY"],
        api_key_header=os.environ.get("AGENT_CONTROL_API_KEY_HEADER", "Galileo-API-Key"),
    ) as client:
        attached = await _find_attached_control(client, log_stream_id)
        if attached is None:
            print(f"No {CONTROL_NAME} clone on this log stream — cloning from control {SOURCE_CONTROL_ID}...")
            created = await _attach_control(log_stream_id)
            print(f"OK: created clone control_id={created.get('id')} binding_id={created.get('binding_id')}")
            attached = await _find_attached_control(client, log_stream_id)
        else:
            print(f"OK: found attached control id={attached['id']} name={attached['name']}")

        if attached is None:
            print("FAIL: could not attach control")
            return 1

        binding = attached["attachments"]["targets"][0]
        binding_enabled = binding.get("enabled", False)
        print(f"Binding enabled: {binding_enabled}")

        if enable is not None and binding_enabled != enable:
            await _set_binding_enabled(client, attached["id"], log_stream_id, enable)
            print(f"OK: binding set to enabled={enable}")
        elif enable is None:
            print("Tip: use --enable before Act 3 enforce replay; --disable for observe-only")

    print()
    print("Next: set galileo.enable_agent_control: true in config.yaml and restart Streamlit")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enable", action="store_true", help="Enable control binding on log stream")
    group.add_argument("--disable", action="store_true", help="Disable control binding (observe-only)")
    args = parser.parse_args()

    enable_flag: bool | None
    if args.enable:
        enable_flag = True
    elif args.disable:
        enable_flag = False
    else:
        enable_flag = None

    return asyncio.run(run(enable_flag))


if __name__ == "__main__":
    raise SystemExit(main())
