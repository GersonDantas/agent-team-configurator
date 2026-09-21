"""Render the configured personal team as Codex SessionStart context."""

import json
import os
from pathlib import Path
import sys

from team_schema import LEVELS, effective_team, requested_read_only


MAX_CONTEXT_CHARS = 7800

def _codex_home():
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))


def render_context(data, cwd):
    team = effective_team(data, cwd)
    agent_instructions = []
    lines = [
        "# Personal agent team",
        "",
        "Use the personal team policy below for delegated work. Choose the lowest approved level sufficient for the task.",
        "Only agents explicitly marked as able to delegate may do so, and only to their configured destinations.",
        "More restrictive skill rules and approval, proof, publication, Git, and permission gates still prevail.",
        "Agent levels never expand filesystem, network, write, or external-action permissions.",
        "Configured agent permissions are requests, not proof of the effective child sandbox. Confirm runtime metadata before claiming technical isolation.",
        "Do not repeat a consultation without new evidence or a new decision.",
        "Multiple matching triggers produce one focused consultation. Exclusions may skip automatic convenience triggers, but never an explicit request, delegation prohibition, permission requirement, or stronger skill gate.",
        "A missing, interrupted, invalid, or insufficient response leaves the consultation pending; it never approves the next gated step.",
        "",
        "Levels:",
    ]
    for name in LEVELS:
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
            ]
        )
        agent_instructions.append((name, item["instructions"].strip()))

    active_workflow = team["workflow"]["active"]
    workflow = team["workflow"]["definitions"][active_workflow]
    lines.extend(["", f"Active workflow: {active_workflow}. {workflow['description']}"])
    for step in workflow["steps"]:
        dependencies = ",".join(step.get("after", [])) or "none"
        lines.append(
            f"- step={step['id']}; agent={step['agent']}; when={step['when']}; "
            f"after={dependencies}; requires_response={str(step.get('requires_response', False)).lower()}."
        )

    configured_agents = [
        (name, item)
        for name, item in team["agents"].items()
        if item.get("triggers") or item.get("response_contract") or item.get("exclusions")
    ]
    if configured_agents:
        lines.extend(["", "Configured triggers and response gates:"])
    for name, item in configured_agents:
        for trigger in item.get("triggers", []):
            lines.append(
                f"- {name}.{trigger['id']}: timing={trigger['timing']}; "
                f"required={str(trigger['required']).lower()}; {trigger['description']}"
            )
        if item.get("exclusions"):
            lines.append(f"- {name} exclusions: " + " | ".join(item["exclusions"]))
        contract = item.get("response_contract", {})
        if contract:
            lines.append(
                f"- {name} response contract v{contract['contract_version']}: fields="
                + ",".join(contract["required_fields"])
                + "; outcomes="
                + ",".join(contract["outcomes"])
                + "; blocking="
                + ",".join(contract["blocking_outcomes"])
                + ". The executor must assess the response and address blockers before advancing."
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
        "Delegation destinations, workflow transitions, trigger classification, response shape, and any call budget are behavioral policy unless a validated runtime guard reports enforcement."
    )
    lines.extend(["", "Agent instructions:"])
    for name, instructions in agent_instructions:
        lines.append(f"- {name}: {instructions}")
    context = "\n".join(lines)
    if len(context) > MAX_CONTEXT_CHARS:
        raise ValueError(
            "complete agent policy exceeds SessionStart context budget; shorten instructions or rules"
        )
    return context


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
