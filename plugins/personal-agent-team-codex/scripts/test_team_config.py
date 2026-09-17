import json
import tempfile
from pathlib import Path
import tomllib

from team_config import apply, defaults, validate


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
    assert json.loads((home / "personal-agent-team-codex/team.json").read_text())["schema_version"] == 1
    assert tomllib.loads((home / "agents/consultor.toml").read_text())["model"] == "astra"
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
