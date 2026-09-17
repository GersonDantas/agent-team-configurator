import json
import tempfile
from pathlib import Path
import tomllib

from team_config import apply, defaults, resolve, validate


with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    original = 'model = "old"\n# keep\n[projects.example]\ntrust_level = "trusted"\n'
    (home / "config.toml").write_text(original)
    (home / "AGENTS.md").write_text("Existing rules\n")
    data = defaults("sol", "astra", "medium")
    validate(data)
    apply(home, data, dry=True)
    assert not (home / "executor-consultor-state.json").exists()
    apply(home, data)
    config = tomllib.loads((home / "config.toml").read_text())
    assert config["model"] == "sol"
    assert config["agents"]["max_concurrent_threads_per_session"] == 3
    assert config["projects"]["example"]["trust_level"] == "trusted"
    assert json.loads((home / "executor-consultor/team.json").read_text())["schema_version"] == 1
    assert tomllib.loads((home / "agents/consultor.toml").read_text())["model"] == "astra"
    assert (home / "AGENTS.md").read_text().count("<!-- executor-consultor -->") == 1
    apply(home, data)
    installed = (home / "AGENTS.md").read_text()
    (home / "AGENTS.md").write_text(installed + "later")
    try:
        apply(home, {}, uninstall=True)
    except ValueError:
        pass
    else:
        raise AssertionError("later edit overwritten")
    (home / "AGENTS.md").write_text(installed)
    apply(home, {}, uninstall=True)
    assert (home / "config.toml").read_text() == original
    assert (home / "AGENTS.md").read_text() == "Existing rules\n"
    assert not (home / "agents/consultor.toml").exists()

bad = defaults("sol", "astra", "medium")
bad["limits"]["max_calls_per_task"] = 0
try:
    validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("invalid limit accepted")

print("PASS: team plan, apply, idempotence, preservation, refusal, uninstall, invalid input")
