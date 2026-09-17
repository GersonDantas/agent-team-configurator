import json
import os
from pathlib import Path
import subprocess
import tempfile

from session_context import render_context


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "session_context.py"


def defaults(executor, consultant, effort):
    return {
        "schema_version": 1,
        "levels": {
            "rotina": {"model": executor, "effort": effort, "fallbacks": []},
            "analise": {"model": executor, "effort": effort, "fallbacks": []},
            "critico": {"model": consultant, "effort": effort, "fallbacks": []},
            "estrategico": {"model": consultant, "effort": effort, "fallbacks": []},
        },
        "agents": {
            "executor": {
                "description": "Coordinates work.",
                "instructions": "Execute the task.",
                "default_level": "analise",
                "max_level": "estrategico",
                "requested_read_only": False,
                "read_only": False,
                "can_delegate": True,
                "delegates_to": ["consultor"],
            },
            "consultor": {
                "description": "Reviews important decisions.",
                "instructions": "Review evidence without editing.",
                "default_level": "estrategico",
                "max_level": "estrategico",
                "requested_read_only": True,
                "read_only": True,
                "can_delegate": False,
                "delegates_to": [],
            },
        },
        "limits": {},
        "project_overrides": {},
    }


def run_hook(home, cwd, source="startup"):
    environment = dict(os.environ, CODEX_HOME=str(home))
    result = subprocess.run(
        [os.environ.get("PYTHON", "python3"), str(SCRIPT)],
        input=json.dumps(
            {
                "hook_event_name": "SessionStart",
                "source": source,
                "cwd": str(cwd),
                "session_id": "test",
            }
        ),
        text=True,
        capture_output=True,
        env=environment,
        check=True,
    )
    return result.stdout.strip()


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    home = root / "codex"
    project = root / "project"
    project.mkdir()
    assert run_hook(home, project) == ""

    data = defaults("sol", "astra", "medium")
    data["project_overrides"][str(project.resolve())] = {"limits": {"max_calls_per_task": 2}}
    team_path = home / "personal-agent-team-codex" / "team.json"
    team_path.parent.mkdir(parents=True)
    team_path.write_text(json.dumps(data))

    output = json.loads(run_hook(home, project, "compact"))
    context = output["hookSpecificOutput"]["additionalContext"]
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "consultor" in context
    assert "model=astra" in context
    assert "requested_permission=read-only" in context
    assert "runtime_permission=unverified" in context
    assert "advisory_max_calls_per_task=2" in context
    assert render_context(data, root / "other").count("# Personal agent team") == 1

    team_path.write_text("not-json")
    invalid = json.loads(run_hook(home, project))
    assert "team context was not loaded" in invalid["systemMessage"]

print("PASS: no-op, startup context, compact context, project override, invalid config")
