"""Render the configured personal team as Codex SessionStart context."""

import json
import os
from pathlib import Path
import sys

def _codex_home():
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))


def effective_team(data, cwd):
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    for section in ("levels", "agents", "limits"):
        if not isinstance(data.get(section), dict):
            raise ValueError(f"{section} must be an object")
    if not isinstance(data.get("project_overrides", {}), dict):
        raise ValueError("project_overrides must be an object")

    team = json.loads(json.dumps(data))
    path = str(Path(cwd).resolve())
    matches = [
        (root, value)
        for root, value in data.get("project_overrides", {}).items()
        if isinstance(root, str)
        and isinstance(value, dict)
        and (path == root or path.startswith(root.rstrip("/") + "/"))
    ]
    if matches:
        _, override = max(matches, key=lambda pair: len(pair[0]))
        for section in ("levels", "agents", "limits"):
            for key, value in override.get(section, {}).items():
                if isinstance(value, dict) and isinstance(team[section].get(key), dict):
                    team[section][key].update(value)
                else:
                    team[section][key] = value
    return team


def requested_read_only(item):
    has_requested = "requested_read_only" in item
    has_legacy = "read_only" in item
    if not has_requested and not has_legacy:
        raise ValueError("agent permission intent is missing")
    if has_requested and not isinstance(item["requested_read_only"], bool):
        raise ValueError("requested_read_only must be boolean")
    if has_legacy and not isinstance(item["read_only"], bool):
        raise ValueError("read_only must be boolean")
    if has_requested and has_legacy and item["requested_read_only"] != item["read_only"]:
        raise ValueError("requested_read_only conflicts with legacy read_only")
    return item["requested_read_only"] if has_requested else item["read_only"]


def render_context(data, cwd):
    team = effective_team(data, cwd)
    lines = [
        "# Personal agent team",
        "",
        "Use the personal team policy below for delegated work. Choose the lowest approved level sufficient for the task.",
        "Only agents explicitly marked as able to delegate may do so, and only to their configured destinations.",
        "More restrictive skill rules and approval, proof, publication, Git, and permission gates still prevail.",
        "Agent levels never expand filesystem, network, write, or external-action permissions.",
        "Configured agent permissions are requests, not proof of the effective child sandbox. Confirm runtime metadata before claiming technical isolation.",
        "Do not repeat a consultation without new evidence or a new decision.",
        "",
        "Levels:",
    ]
    for name in ("rotina", "analise", "critico", "estrategico"):
        item = team["levels"][name]
        fallbacks = ", ".join(item.get("fallbacks", [])) or "none"
        lines.append(
            f"- {name}: model={item['model']}; effort={item['effort']}; fallbacks={fallbacks}."
        )

    lines.extend(["", "Agents:"])
    for name, item in team["agents"].items():
        destinations = ", ".join(item.get("delegates_to", [])) or "none"
        mode = "read-only" if requested_read_only(item) else "workspace-write"
        lines.extend(
            [
                (
                    f"- {name}: {item['description']} Default={item['default_level']}; "
                    f"maximum={item['max_level']}; requested_permission={mode}; "
                    "runtime_permission=unverified; "
                    f"can_delegate={str(item['can_delegate']).lower()}; delegates_to={destinations}."
                ),
                f"  Instructions: {item['instructions'].strip()}",
            ]
        )

    limits = team["limits"]
    configured_limits = []
    if "max_concurrent" in limits:
        configured_limits.append(
            f"requested_max_concurrent={limits['max_concurrent']} (native config when supported)"
        )
    if "max_calls_per_task" in limits:
        configured_limits.append(
            f"advisory_max_calls_per_task={limits['max_calls_per_task']} (not runtime-enforced)"
        )
    lines.extend(["", "Limits: " + ("; ".join(configured_limits) if configured_limits else "use host defaults; no advisory call budget configured") + "."])
    lines.append(
        "Delegation destinations and any call budget are behavioral policy unless a validated runtime guard reports enforcement."
    )
    return "\n".join(lines)


def main():
    try:
        event = json.load(sys.stdin)
        if event.get("hook_event_name") != "SessionStart":
            return 0
        path = _codex_home() / "personal-agent-team-codex" / "team.json"
        if not path.exists():
            return 0
        data = json.loads(path.read_text())
        context = render_context(data, event.get("cwd") or os.getcwd())
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": context,
                    }
                },
                ensure_ascii=False,
            )
        )
        return 0
    except (AttributeError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {
                    "systemMessage": (
                        "Personal Agent Team configuration is invalid; team context was not loaded: "
                        f"{error}"
                    )
                },
                ensure_ascii=False,
            )
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
