"""Portable installer: Python 3.11+, standard library only."""
import argparse
import json
import os
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def apply(home, executor, consultant, effort, uninstall=False, dry=False):
    state = home / "executor-consultor-state.json"
    saved = json.loads(state.read_text()) if state.exists() else {}
    for name, entry in saved.items():
        target = home / name
        if not target.exists() or target.read_text() != entry["after"]:
            raise ValueError(f"Alteracao posterior em {target}; concilie manualmente. Backup: {state}")
    if uninstall:
        if dry:
            print("Restauraria:", list(saved))
            return
        for name, entry in saved.items():
            target = home / name
            if entry["before"] is None:
                target.unlink()
            else:
                target.write_text(entry["before"])
        if state.exists():
            state.unlink()
        print("Configuracao restaurada.")
        return
    config = home / "config.toml"
    original = config.read_text() if config.exists() else ""
    tomllib.loads(original)
    split = re.search(r"(?m)^\s*\[", original)
    head, tail = (original[:split.start()], original[split.start():]) if split else (original, "")
    for key, value in (("model", executor), ("model_reasoning_effort", effort)):
        pattern = rf"(?m)^{key}\s*=.*$"
        line = f"{key} = {json.dumps(value)}"
        head = re.sub(pattern, lambda _: line, head) if re.search(pattern, head) else line + "\n" + head
    agent = (ROOT / "templates/consultor.toml").read_text()
    agent = agent.replace("MODEL_VALUE", json.dumps(consultant)).replace("EFFORT_VALUE", json.dumps(effort))
    instructions = home / "AGENTS.md"
    before_policy = instructions.read_text() if instructions.exists() else ""
    if "Generated file" in before_policy and "AGENTS.md" not in saved:
        raise ValueError("AGENTS.md gerado: integre a politica na fonte e no gerador existentes.")
    if (home / "agents/consultor.toml").exists() and "agents/consultor.toml" not in saved:
        raise ValueError("Consultor existente: use a skill para conciliar sem sobrescrever.")
    base = saved.get("AGENTS.md", {}).get("before", before_policy) or ""
    updates = {"config.toml": head + tail, "agents/consultor.toml": agent,
               "AGENTS.md": base + "\n\n" + (ROOT / "templates/policy.md").read_text()}
    for name in ("config.toml", "agents/consultor.toml"):
        tomllib.loads(updates[name])
    if dry:
        print(json.dumps({"executor": executor, "consultor": consultant, "esforco": effort, "arquivos": list(updates)}))
        return
    home.mkdir(parents=True, exist_ok=True)
    journal = {}
    for name, after in updates.items():
        target = home / name
        before = saved[name]["before"] if name in saved else (target.read_text() if target.exists() else None)
        journal[name] = {"before": before, "after": after}
    fd = os.open(state, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(journal, stream, indent=2)
    for name, after in updates.items():
        target = home / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(after)
    print(f"Configurado. Backup privado: {state}. Abra uma nova conversa.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    parser.add_argument("--executor", default="gpt-5.6-sol")
    parser.add_argument("--consultor", default="gpt-6-astra")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        apply(args.home, args.executor, args.consultor, args.effort, args.uninstall, args.dry_run)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")
