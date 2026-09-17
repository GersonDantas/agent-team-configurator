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


def render_context(data, cwd):
    team = effective_team(data, cwd)
    lines = [
        "# Personal agent team",
        "",
        "Use the personal team policy below for delegated work. Choose the lowest approved level sufficient for the task.",
        "Only agents explicitly marked as able to delegate may do so, and only to their configured destinations.",
        "More restrictive skill rules and approval, proof, publication, Git, and permission gates still prevail.",
        "Agent levels never expand filesystem, network, write, or external-action permissions.",
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
        mode = "read-only" if item["read_only"] else "workspace-write"
        lines.extend(
            [
                (
                    f"- {name}: {item['description']} Default={item['default_level']}; "
                    f"maximum={item['max_level']}; permission={mode}; "
                    f"can_delegate={str(item['can_delegate']).lower()}; delegates_to={destinations}."
                ),
                f"  Instructions: {item['instructions'].strip()}",
            ]
        )

    limits = team["limits"]
    lines.extend(
        [
            "",
            (
                "Limits: "
                f"max_concurrent={limits['max_concurrent']}; "
                f"max_calls_per_task={limits['max_calls_per_task']}."
            ),
            "Concurrency is native only when supported by the active host. Total calls and delegation destinations are behavioral policy unless a validated runtime guard reports enforcement.",
        ]
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
