"""Configure a personal Codex agent team from an approved JSON specification."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
STATE_NAME = "executor-consultor-state.json"
LEVELS = ("rotina", "analise", "critico", "estrategico")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


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
                "description": "Coordena o trabalho e integra os resultados.",
                "instructions": "Execute a tarefa, delegando apenas quando houver beneficio claro.",
                "default_level": "analise",
                "max_level": "estrategico",
                "read_only": False,
                "can_delegate": True,
                "delegates_to": ["consultor"],
            },
            "consultor": {
                "description": "Consulta planos importantes, bloqueios e marcos.",
                "instructions": (
                    "Analise evidencias e restricoes. Distinga fatos de hipoteses e devolva "
                    "recomendacoes acionaveis. Nao edite arquivos, publique ou delegue."
                ),
                "default_level": "estrategico",
                "max_level": "estrategico",
                "read_only": True,
                "can_delegate": False,
                "delegates_to": [],
            },
        },
        "limits": {"max_concurrent": 3, "max_calls_per_task": 6},
        "project_overrides": {},
    }


def validate(data):
    if data.get("schema_version") != 1:
        raise ValueError("schema_version deve ser 1")
    levels = data.get("levels")
    if not isinstance(levels, dict) or set(levels) != set(LEVELS):
        raise ValueError("levels deve conter rotina, analise, critico e estrategico")
    for level, item in levels.items():
        if not isinstance(item, dict) or not isinstance(item.get("model"), str) or not item["model"]:
            raise ValueError(f"modelo invalido em {level}")
        if item.get("effort") not in EFFORTS:
            raise ValueError(f"esforco invalido em {level}")
        fallbacks = item.get("fallbacks", [])
        if not isinstance(fallbacks, list) or any(not isinstance(x, str) or not x for x in fallbacks):
            raise ValueError(f"fallbacks invalidos em {level}")
    agents = data.get("agents")
    if not isinstance(agents, dict) or "executor" not in agents or "consultor" not in agents:
        raise ValueError("agents deve conter executor e consultor")
    for name, item in agents.items():
        if not NAME.fullmatch(name) or not isinstance(item, dict):
            raise ValueError(f"agente invalido: {name}")
        for field in ("description", "instructions"):
            if not isinstance(item.get(field), str) or not item[field].strip() or '"""' in item[field]:
                raise ValueError(f"{field} invalido em {name}")
        if item.get("default_level") not in LEVELS or item.get("max_level") not in LEVELS:
            raise ValueError(f"nivel invalido em {name}")
        if LEVELS.index(item["default_level"]) > LEVELS.index(item["max_level"]):
            raise ValueError(f"nivel padrao excede maximo em {name}")
        if not isinstance(item.get("read_only"), bool) or not isinstance(item.get("can_delegate"), bool):
            raise ValueError(f"permissoes invalidas em {name}")
        targets = item.get("delegates_to", [])
        if not isinstance(targets, list) or any(x not in agents or x == name for x in targets):
            raise ValueError(f"destinos invalidos em {name}")
        if not item["can_delegate"] and targets:
            raise ValueError(f"{name} nao pode delegar, mas possui destinos")
    limits = data.get("limits")
    if not isinstance(limits, dict):
        raise ValueError("limits ausente")
    for key in ("max_concurrent", "max_calls_per_task"):
        if not isinstance(limits.get(key), int) or limits[key] < 1:
            raise ValueError(f"{key} deve ser inteiro positivo")
    overrides = data.get("project_overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("project_overrides deve ser objeto")
    for path, override in overrides.items():
        if not Path(path).is_absolute() or not isinstance(override, dict):
            raise ValueError(f"excecao de projeto invalida: {path}")
        unknown = set(override) - {"limits", "agents", "levels"}
        if unknown:
            raise ValueError(f"campos desconhecidos em {path}: {sorted(unknown)}")
    return data


def _set_top(text, key, value):
    match = re.search(r"(?m)^\s*\[", text)
    head, tail = (text[: match.start()], text[match.start() :]) if match else (text, "")
    pattern = rf"(?m)^{re.escape(key)}\s*=.*$"
    line = f"{key} = {json.dumps(value)}"
    head = re.sub(pattern, line, head) if re.search(pattern, head) else line + "\n" + head
    return head + tail


def _set_agents_limit(text, value):
    header = re.search(r"(?m)^\[agents\]\s*$", text)
    line = f"max_concurrent_threads_per_session = {value}"
    if not header:
        suffix = "" if not text or text.endswith("\n") else "\n"
        return text + suffix + f"\n[agents]\n{line}\n"
    start = header.end()
    next_header = re.search(r"(?m)^\[", text[start:])
    end = start + next_header.start() if next_header else len(text)
    body = text[start:end]
    pattern = r"(?m)^max_concurrent_threads_per_session\s*=.*$"
    body = re.sub(pattern, line, body) if re.search(pattern, body) else "\n" + line + body
    return text[:start] + body + text[end:]


def _without_policy(text):
    return re.sub(
        r"\n*<!-- executor-consultor -->.*?<!-- /executor-consultor -->\n*",
        "\n",
        text,
        flags=re.DOTALL,
    ).rstrip()


def _agent_toml(name, item, levels):
    level = levels[item["default_level"]]
    sandbox = "read-only" if item["read_only"] else "workspace-write"
    instructions = item["instructions"].strip()
    if item["can_delegate"]:
        instructions += "\nDelegue somente aos destinos pessoais aprovados e dentro dos limites aplicaveis."
    else:
        instructions += "\nNao delegue a outros agentes."
    return (
        f"name = {json.dumps(name)}\n"
        f"description = {json.dumps(item['description'])}\n"
        f"model = {json.dumps(level['model'])}\n"
        f"model_reasoning_effort = {json.dumps(level['effort'])}\n"
        f"sandbox_mode = {json.dumps(sandbox)}\n"
        f'developer_instructions = """\n{instructions}\n"""\n'
    )


def build_updates(home, data, saved):
    config = home / "config.toml"
    current_config = config.read_text() if config.exists() else ""
    if current_config.strip():
        tomllib.loads(current_config)
    executor_level = data["levels"][data["agents"]["executor"]["default_level"]]
    config_text = _set_top(current_config, "model", executor_level["model"])
    config_text = _set_top(config_text, "model_reasoning_effort", executor_level["effort"])
    config_text = _set_agents_limit(config_text, data["limits"]["max_concurrent"])
    tomllib.loads(config_text)

    instructions = home / "AGENTS.md"
    current_policy = instructions.read_text() if instructions.exists() else ""
    if "Generated file" in current_policy and "AGENTS.md" not in saved:
        raise ValueError("AGENTS.md gerado: integre a politica na fonte e no gerador existentes")
    policy = (ROOT / "templates/team-policy.md").read_text().rstrip()
    policy_text = _without_policy(current_policy)
    policy_text = (policy_text + "\n\n" + policy + "\n").lstrip("\n")

    updates = {
        "config.toml": config_text,
        "AGENTS.md": policy_text,
        "executor-consultor/team.json": json.dumps(data, indent=2, ensure_ascii=False) + "\n",
    }
    for name, item in data["agents"].items():
        if name == "executor":
            continue
        relative = f"agents/{name}.toml"
        target = home / relative
        if target.exists() and relative not in saved:
            raise ValueError(f"agente existente fora do plugin: {target}")
        updates[relative] = _agent_toml(name, item, data["levels"])
        tomllib.loads(updates[relative])
    return updates


def apply(home, data, dry=False, uninstall=False):
    state = home / STATE_NAME
    saved = json.loads(state.read_text()) if state.exists() else {}
    for name, entry in saved.items():
        target = home / name
        if not target.exists() or target.read_text() != entry["after"]:
            raise ValueError(f"alteracao posterior em {target}; concilie pelo backup {state}")
    if uninstall:
        if dry:
            print(json.dumps({"restore": list(saved)}, ensure_ascii=False))
            return
        for name, entry in saved.items():
            target = home / name
            if entry["before"] is None:
                target.unlink(missing_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(entry["before"])
        state.unlink(missing_ok=True)
        print("Configuracao restaurada.")
        return
    validate(data)
    updates = build_updates(home, data, saved)
    preview = {
        "executor": data["agents"]["executor"]["default_level"],
        "agents": sorted(data["agents"]),
        "limits": data["limits"],
        "files": sorted(updates),
        "guarantees": {
            "concurrency": "native_when_supported",
            "total_calls": "instruction_only",
            "delegation_targets": "instruction_only",
        },
    }
    if dry:
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        return
    home.mkdir(parents=True, exist_ok=True)
    journal = {}
    for name, after in updates.items():
        target = home / name
        before = saved[name]["before"] if name in saved else (target.read_text() if target.exists() else None)
        journal[name] = {"before": before, "after": after}
    fd = os.open(state, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(journal, stream, indent=2, ensure_ascii=False)
    for name, after in updates.items():
        target = home / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(after)
    print(json.dumps(preview, indent=2, ensure_ascii=False))


def resolve(data, cwd, agent, level=None):
    validate(data)
    merged = json.loads(json.dumps(data))
    path = str(Path(cwd).resolve())
    matches = [(root, value) for root, value in data["project_overrides"].items() if path == root or path.startswith(root.rstrip("/") + "/")]
    if matches:
        _, override = max(matches, key=lambda pair: len(pair[0]))
        for section in ("levels", "agents", "limits"):
            if section in override:
                for key, value in override[section].items():
                    if isinstance(value, dict) and key in merged[section]:
                        merged[section][key].update(value)
                    else:
                        merged[section][key] = value
    validate(merged)
    item = merged["agents"][agent]
    selected = level or item["default_level"]
    if LEVELS.index(selected) > LEVELS.index(item["max_level"]):
        raise ValueError(f"nivel {selected} excede maximo de {agent}")
    result = {"agent": agent, "level": selected, **merged["levels"][selected], "limits": merged["limits"]}
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("defaults")
    create.add_argument("--executor", default="gpt-5.6-sol")
    create.add_argument("--consultant", default="gpt-6-astra")
    create.add_argument("--effort", default="medium")
    for command in ("plan", "apply"):
        item = commands.add_parser(command)
        item.add_argument("--spec", type=Path, required=True)
    remove = commands.add_parser("uninstall")
    remove.add_argument("--dry-run", action="store_true")
    query = commands.add_parser("resolve")
    query.add_argument("--spec", type=Path)
    query.add_argument("--cwd", required=True)
    query.add_argument("--agent", required=True)
    query.add_argument("--level", choices=LEVELS)
    args = parser.parse_args()
    try:
        if args.command == "defaults":
            print(json.dumps(defaults(args.executor, args.consultant, args.effort), indent=2, ensure_ascii=False))
        elif args.command == "uninstall":
            apply(args.home, {}, dry=args.dry_run, uninstall=True)
        else:
            spec = args.spec or args.home / "executor-consultor/team.json"
            data = json.loads(spec.read_text())
            if args.command == "resolve":
                resolve(data, args.cwd, args.agent, args.level)
            else:
                apply(args.home, data, dry=args.command == "plan")
    except (KeyError, ValueError, OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
