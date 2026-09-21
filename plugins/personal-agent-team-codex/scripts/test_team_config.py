import json
import tempfile
from pathlib import Path
import tomllib

from team_config import apply, defaults, effective_team, validate


with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    original = 'model = "old"\n# keep\n[projects.example]\ntrust_level = "trusted"\n'
    (home / "config.toml").write_text(original)
    generated = "<!-- Generated file. Do not edit directly. -->\nExisting rules\n"
    (home / "AGENTS.md").write_text(generated)
    data = defaults("sol", "astra", "medium")
    validate(data)
    apply(home, data, dry=True)
    assert not (home / "personal-agent-team-codex-state.json").exists()
    apply(home, data)
    config = tomllib.loads((home / "config.toml").read_text())
    assert config["model"] == "sol"
    assert "agents" not in config
    assert config["projects"]["example"]["trust_level"] == "trusted"
    stored = json.loads((home / "personal-agent-team-codex/team.json").read_text())
    assert stored["schema_version"] == 2
    assert stored["workflow"]["active"] == "consultation_on_trigger"
    consultor_toml = tomllib.loads((home / "agents/consultor.toml").read_text())
    assert consultor_toml["model"] == "astra"
    assert "contrato de resposta efetivo" in consultor_toml["developer_instructions"]
    assert (home / "AGENTS.md").read_text() == generated
    assert "AGENTS.md" not in json.loads((home / "personal-agent-team-codex-state.json").read_text())
    apply(home, data)
    installed = (home / "config.toml").read_text()
    (home / "config.toml").write_text(installed + "# later\n")
    try:
        apply(home, {}, uninstall=True)
    except ValueError:
        pass
    else:
        raise AssertionError("later edit overwritten")
    (home / "config.toml").write_text(installed)
    apply(home, {}, uninstall=True)
    assert (home / "config.toml").read_text() == original
    assert (home / "AGENTS.md").read_text() == generated
    assert not (home / "agents/consultor.toml").exists()

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    home = root / "codex"
    home.mkdir()
    generated = root / "generated-agents.md"
    generated.write_text("<!-- Generated file. Do not edit directly. -->\nShared rules\n")
    (home / "AGENTS.md").symlink_to(generated)
    apply(home, defaults("sol", "astra", "medium"))
    assert (home / "AGENTS.md").is_symlink()
    assert generated.read_text() == "<!-- Generated file. Do not edit directly. -->\nShared rules\n"
    apply(home, {}, uninstall=True)
    assert (home / "AGENTS.md").is_symlink()
    assert generated.read_text() == "<!-- Generated file. Do not edit directly. -->\nShared rules\n"

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    before = "Existing rules\n"
    after = before + "\n<!-- executor-consultor -->\nOld policy\n<!-- /executor-consultor -->\n"
    (home / "AGENTS.md").write_text(after)
    (home / "personal-agent-team-codex-state.json").write_text(
        json.dumps({"AGENTS.md": {"before": before, "after": after}})
    )
    apply(home, defaults("sol", "astra", "medium"))
    assert (home / "AGENTS.md").read_text() == before
    assert "AGENTS.md" not in json.loads((home / "personal-agent-team-codex-state.json").read_text())

bad = defaults("sol", "astra", "medium")
bad["limits"]["max_calls_per_task"] = 0
try:
    validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("invalid limit accepted")

conflicting_permission = defaults("sol", "astra", "medium")
conflicting_permission["agents"]["consultor"]["read_only"] = False
try:
    validate(conflicting_permission)
except ValueError:
    pass
else:
    raise AssertionError("conflicting permission aliases accepted")

legacy_permission = defaults("sol", "astra", "medium")
for agent in legacy_permission["agents"].values():
    agent.pop("requested_read_only")
validate(legacy_permission)

legacy_schema = defaults("sol", "astra", "medium")
legacy_schema["schema_version"] = 1
legacy_schema.pop("workflow")
for agent in legacy_schema["agents"].values():
    agent.pop("triggers")
    agent.pop("exclusions")
    agent.pop("response_contract")
legacy_snapshot = json.dumps(legacy_schema, sort_keys=True)
normalized_legacy = validate(legacy_schema)
assert normalized_legacy["schema_version"] == 2
assert normalized_legacy["workflow"]["active"] == "consultation_on_trigger"
assert normalized_legacy["agents"]["consultor"]["triggers"] == []
assert json.dumps(legacy_schema, sort_keys=True) == legacy_snapshot

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    apply(home, legacy_schema)
    stored = json.loads((home / "personal-agent-team-codex/team.json").read_text())
    assert stored["schema_version"] == 2
    assert stored["agents"]["consultor"]["triggers"] == []
    apply(home, {}, uninstall=True)

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    new_permission = defaults("sol", "astra", "medium")
    for agent in new_permission["agents"].values():
        agent.pop("read_only")
    apply(home, new_permission)
    stored_agents = json.loads(
        (home / "personal-agent-team-codex/team.json").read_text()
    )["agents"]
    assert stored_agents["consultor"]["requested_read_only"] is True
    assert stored_agents["consultor"]["read_only"] is True
    apply(home, {}, uninstall=True)

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    data = defaults("sol", "astra", "medium")
    data["limits"] = {"max_concurrent": 4, "max_calls_per_task": 8}
    apply(home, data)
    config = tomllib.loads((home / "config.toml").read_text())
    assert config["agents"]["max_concurrent_threads_per_session"] == 4
    stored = json.loads((home / "personal-agent-team-codex/team.json").read_text())
    assert stored["limits"] == {"max_concurrent": 4, "max_calls_per_task": 8}
    apply(home, {}, uninstall=True)

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    existing = '[agents]\nmax_concurrent_threads_per_session = 7\n'
    (home / "config.toml").write_text(existing)
    apply(home, defaults("sol", "astra", "medium"))
    config = tomllib.loads((home / "config.toml").read_text())
    assert config["agents"]["max_concurrent_threads_per_session"] == 7
    apply(home, {}, uninstall=True)
    assert (home / "config.toml").read_text() == existing

invalid_trigger = defaults("sol", "astra", "medium")
invalid_trigger["agents"]["consultor"]["triggers"].append(
    dict(invalid_trigger["agents"]["consultor"]["triggers"][0])
)
try:
    validate(invalid_trigger)
except ValueError:
    pass
else:
    raise AssertionError("duplicate trigger accepted")

invalid_workflow = defaults("sol", "astra", "medium")
invalid_workflow["workflow"]["definitions"]["reviewed_plan"]["steps"][0]["after"] = ["missing"]
try:
    validate(invalid_workflow)
except ValueError:
    pass
else:
    raise AssertionError("invalid workflow dependency accepted")

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    project = root / "project"
    child = project / "child"
    child.mkdir(parents=True)
    data = defaults("sol", "astra", "medium")
    data["project_overrides"][str(project.resolve())] = {
        "workflow": {"active": "reviewed_plan"}
    }
    data["project_overrides"][str(child.resolve())] = {
        "agents": {"consultor": {"triggers": [], "read_only": False}}
    }
    assert effective_team(data, project)["workflow"]["active"] == "reviewed_plan"
    effective_child = effective_team(data, child)
    assert effective_child["workflow"]["active"] == "consultation_on_trigger"
    assert effective_child["agents"]["consultor"]["triggers"] == []
    assert effective_child["agents"]["consultor"]["requested_read_only"] is False

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    project_a = root / "a"
    project_b = root / "b"
    project_a.mkdir()
    project_b.mkdir()
    data = defaults("sol", "astra", "medium")
    data["project_overrides"][str(project_a.resolve())] = {
        "agents": {"consultor": {"default_level": "rotina", "max_level": "rotina"}}
    }
    data["project_overrides"][str(project_b.resolve())] = {
        "agents": {"consultor": {"default_level": "analise"}}
    }
    assert effective_team(data, project_a)["agents"]["consultor"]["default_level"] == "rotina"
    assert effective_team(data, project_b)["agents"]["consultor"]["default_level"] == "analise"

legacy_override_agent = defaults("sol", "astra", "medium")
legacy_override_agent["schema_version"] = 1
legacy_override_agent.pop("workflow")
for agent in legacy_override_agent["agents"].values():
    agent.pop("triggers")
    agent.pop("exclusions")
    agent.pop("response_contract")
project = str(Path("/tmp/personal-agent-team-v1-project").resolve())
legacy_override_agent["project_overrides"][project] = {
    "agents": {
        "auditor": {
            "description": "Audits one project.",
            "instructions": "Audit evidence.",
            "default_level": "analise",
            "max_level": "estrategico",
            "read_only": True,
            "can_delegate": False,
            "delegates_to": [],
        }
    }
}
effective_legacy = effective_team(legacy_override_agent, project)
assert effective_legacy["agents"]["auditor"]["triggers"] == []

impossible_workflow = defaults("sol", "astra", "medium")
impossible_workflow["workflow"]["active"] = "reviewed_plan"
impossible_workflow["agents"]["executor"]["can_delegate"] = False
impossible_workflow["agents"]["executor"]["delegates_to"] = []
try:
    validate(impossible_workflow)
except ValueError:
    pass
else:
    raise AssertionError("workflow without authorized delegation path accepted")

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    oversized = defaults("sol", "astra", "medium")
    oversized["agents"]["executor"]["instructions"] = "x" * 8000
    try:
        apply(home, oversized, dry=True)
    except ValueError as error:
        assert "context budget" in str(error)
    else:
        raise AssertionError("oversized policy accepted during plan")
    assert not (home / "personal-agent-team-codex-state.json").exists()

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    (home / "personal-agent-team-codex-state.json").write_text(
        json.dumps({"../outside": {"before": None, "after": "bad"}})
    )
    try:
        apply(home, defaults("sol", "astra", "medium"), dry=True)
    except ValueError:
        pass
    else:
        raise AssertionError("path traversal accepted")

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    (home / "executor-consultor-state.json").write_text("{}")
    try:
        apply(home, defaults("sol", "astra", "medium"), dry=True)
    except ValueError:
        pass
    else:
        raise AssertionError("legacy state accepted")

print("PASS: team plan, apply, idempotence, preservation, refusal, uninstall, generated and symlinked AGENTS, policy migration, invalid input, journal confinement, legacy block")
