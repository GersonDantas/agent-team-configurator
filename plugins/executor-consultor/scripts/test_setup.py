import tempfile
from pathlib import Path
import tomllib
from setup import apply

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    config = 'model = "old"\n# preserved\n[projects.example]\ntrust_level = "trusted"\n'
    (home / "config.toml").write_text(config)
    (home / "AGENTS.md").write_text("Existing rules")
    apply(home, "sol", "astra", "medium", dry=True)
    assert not (home / "executor-consultor-state.json").exists()
    apply(home, "sol", "astra", "medium")
    assert tomllib.loads((home / "config.toml").read_text())["projects"]["example"]["trust_level"] == "trusted"
    apply(home, "other", "astra", "high")
    assert tomllib.loads((home / "config.toml").read_text())["model"] == "other"
    assert (home / "AGENTS.md").read_text().count("## Consultation policy") == 1
    installed = (home / "AGENTS.md").read_text()
    (home / "AGENTS.md").write_text(installed + "\nLater user change")
    try:
        apply(home, "", "", "", uninstall=True)
    except ValueError:
        pass
    else:
        raise AssertionError("Later edits overwritten")
    (home / "AGENTS.md").write_text(installed)
    apply(home, "", "", "", uninstall=True)
    assert (home / "config.toml").read_text() == config
    assert (home / "AGENTS.md").read_text() == "Existing rules"
    assert not (home / "agents/consultor.toml").exists()
    (home / "AGENTS.md").write_text("<!-- Generated file -->")
    try:
        apply(home, "sol", "astra", "medium")
    except ValueError:
        pass
    else:
        raise AssertionError("Generated file overwritten")
print("PASS: preview, install, update, preservation, conflict, uninstall, generated file")
