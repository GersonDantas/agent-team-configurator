import json
import os
from pathlib import Path
import subprocess
import tempfile

from session_context import render_context
from team_config import defaults


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "session_context.py"


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
    assert "Active workflow: consultation_on_trigger" in context
    assert "consultor.public_contract" in context
    assert "blocking=revise,insufficient_information" in context
    assert "behavioral policy" in context
    assert len(context) < 8000
    assert render_context(data, root / "other").count("# Personal agent team") == 1

    legacy = defaults("sol", "astra", "medium")
    legacy["schema_version"] = 1
    legacy.pop("workflow")
    for agent in legacy["agents"].values():
        agent.pop("triggers")
        agent.pop("exclusions")
        agent.pop("response_contract")
    legacy_context = render_context(legacy, project)
    assert "Active workflow: consultation_on_trigger" in legacy_context
    assert "consultor.public_contract" not in legacy_context

    long_instructions = defaults("sol", "astra", "medium")
    long_instructions["agents"]["executor"]["instructions"] = "x" * 8000
    try:
        render_context(long_instructions, project)
    except ValueError as error:
        assert "context budget" in str(error)
    else:
        raise AssertionError("oversized instructions were silently truncated")

    maximum_instructions = defaults("sol", "astra", "medium")
    maximum_instructions["agents"]["executor"]["instructions"] = "x" * 2000
    budgeted_context = render_context(maximum_instructions, project)
    assert len(budgeted_context) <= 7800
    assert budgeted_context.index("Active workflow") < budgeted_context.index("Agent instructions")

    legacy_long = defaults("sol", "astra", "medium")
    legacy_long["schema_version"] = 1
    legacy_long.pop("workflow")
    for agent in legacy_long["agents"].values():
        agent.pop("triggers")
        agent.pop("exclusions")
        agent.pop("response_contract")
    legacy_long["agents"]["executor"]["instructions"] = "x" * 2001
    legacy_long_context = render_context(legacy_long, project)
    assert "x" * 2001 in legacy_long_context
    assert len(legacy_long_context) <= 7800

    custom_contract = defaults("sol", "astra", "medium")
    contract = custom_contract["agents"]["consultor"]["response_contract"]
    contract["outcomes"] = ["approved", "rejected"]
    contract["blocking_outcomes"] = ["rejected"]
    custom_context = render_context(custom_contract, project)
    assert "outcomes=approved,rejected" in custom_context

    team_path.write_text("not-json")
    invalid = json.loads(run_hook(home, project))
    assert "team context was not loaded" in invalid["systemMessage"]

print("PASS: no-op, startup context, compact context, project override, invalid config")
