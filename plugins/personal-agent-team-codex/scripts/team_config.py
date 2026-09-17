"""Configure a personal Codex agent team from an approved JSON specification."""

import argparse
import json
import os
from pathlib import Path
import re
import tempfile
import tomllib

STATE_NAME = "personal-agent-team-codex-state.json"
LEGACY_STATE_NAME = "executor-consultor-state.json"
LEVELS = ("rotina", "analise", "critico", "estrategico")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
MANAGED_PATH = re.compile(r"^(config\.toml|AGENTS\.md|personal-agent-team-codex/team\.json|agents/[a-z][a-z0-9_-]{0,63}\.toml)$")


def _safe_target(home, name):
    if not isinstance(name, str) or not MANAGED_PATH.fullmatch(name):
        raise ValueError(f"caminho nao permitido no journal: {name!r}")
    target = home / name
    if target.is_symlink():
        raise ValueError(f"symlink nao permitido como destino: {target}")
    parent = target.parent
    while parent != home.parent and parent != home:
        if parent.is_symlink():
            raise ValueError(f"symlink nao permitido no caminho: {parent}")
        parent = parent.parent
    if parent != home:
        raise ValueError(f"destino fora do CODEX_HOME: {target}")
    return target


def _load_state(home):
    state = home / STATE_NAME
    if not state.exists():
        return {}
    raw = json.loads(state.read_text())
    if not isinstance(raw, dict):
        raise ValueError("journal invalido")
    for name, entry in raw.items():
        _safe_target(home, name)
        if not isinstance(entry, dict) or set(entry) != {"before", "after"}:
            raise ValueError(f"entrada invalida no journal: {name}")
        if entry["before"] is not None and not isinstance(entry["before"], str):
            raise ValueError(f"backup invalido no journal: {name}")
        if not isinstance(entry["after"], str):
            raise ValueError(f"conteudo invalido no journal: {name}")
    return raw


def _atomic_write(path, content, mode=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        if mode is not None:
            os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


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
                "requested_read_only": False,
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
                "requested_read_only": True,
                "read_only": True,
                "can_delegate": False,
                "delegates_to": [],
            },
        },
        "limits": {},
        "project_overrides": {},
    }


def _requested_read_only(item, name):
    has_requested = "requested_read_only" in item
    has_legacy = "read_only" in item
    if not has_requested and not has_legacy:
        raise ValueError(f"permissao solicitada ausente em {name}")
    if has_requested and not isinstance(item["requested_read_only"], bool):
        raise ValueError(f"requested_read_only invalido em {name}")
    if has_legacy and not isinstance(item["read_only"], bool):
        raise ValueError(f"read_only invalido em {name}")
    if has_requested and has_legacy and item["requested_read_only"] != item["read_only"]:
        raise ValueError(f"conflito entre requested_read_only e read_only em {name}")
    return item["requested_read_only"] if has_requested else item["read_only"]


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
        _requested_read_only(item, name)
        if not isinstance(item.get("can_delegate"), bool):
            raise ValueError(f"permissoes invalidas em {name}")
        targets = item.get("delegates_to", [])
        if not isinstance(targets, list) or any(x not in agents or x == name for x in targets):
            raise ValueError(f"destinos invalidos em {name}")
        if not item["can_delegate"] and targets:
            raise ValueError(f"{name} nao pode delegar, mas possui destinos")
    limits = data.get("limits")
    if not isinstance(limits, dict):
        raise ValueError("limits ausente")
    unknown_limits = set(limits) - {"max_concurrent", "max_calls_per_task"}
    if unknown_limits:
        raise ValueError(f"limites desconhecidos: {sorted(unknown_limits)}")
    for key in limits:
        if not isinstance(limits[key], int) or isinstance(limits[key], bool) or limits[key] < 1:
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


def effective_team(data, cwd):
    """Return validated personal configuration with the closest project override."""
    validate(data)
    merged = json.loads(json.dumps(data))
    path = str(Path(cwd).resolve())
    matches = [
        (root, value)
        for root, value in data["project_overrides"].items()
        if path == root or path.startswith(root.rstrip("/") + "/")
    ]
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
    return merged


def _agent_toml(name, item, levels):
    level = levels[item["default_level"]]
    sandbox = "read-only" if _requested_read_only(item, name) else "workspace-write"
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


def _normalized_data(data):
    normalized = json.loads(json.dumps(data))
    for name, item in normalized["agents"].items():
        requested = _requested_read_only(item, name)
        item["requested_read_only"] = requested
        item["read_only"] = requested
    return normalized


def build_updates(home, data, saved):
    data = _normalized_data(data)
    config = home / "config.toml"
    current_config = config.read_text() if config.exists() else ""
    if current_config.strip():
        tomllib.loads(current_config)
    executor_level = data["levels"][data["agents"]["executor"]["default_level"]]
    config_text = _set_top(current_config, "model", executor_level["model"])
    config_text = _set_top(config_text, "model_reasoning_effort", executor_level["effort"])
    if "max_concurrent" in data["limits"]:
        config_text = _set_agents_limit(config_text, data["limits"]["max_concurrent"])
    tomllib.loads(config_text)

    updates = {
        "config.toml": config_text,
        "personal-agent-team-codex/team.json": json.dumps(data, indent=2, ensure_ascii=False) + "\n",
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
    legacy_state = home / LEGACY_STATE_NAME
    if legacy_state.exists():
        raise ValueError(
            f"configuracao legada detectada em {legacy_state}; "
            "use setup.py --uninstall para restaurar a versao 0.1 antes da nova instalacao"
        )
    saved = _load_state(home)
    for name, entry in saved.items():
        target = _safe_target(home, name)
        if not target.exists() or target.read_text() != entry["after"]:
            raise ValueError(f"alteracao posterior em {target}; concilie pelo backup {state}")
    if uninstall:
        if dry:
            print(json.dumps({"restore": list(saved)}, ensure_ascii=False))
            return
        for name, entry in saved.items():
            target = _safe_target(home, name)
            if entry["before"] is None:
                target.unlink(missing_ok=True)
            else:
                _atomic_write(target, entry["before"])
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
            "concurrency": (
                "native_when_configured_and_supported"
                if "max_concurrent" in data["limits"]
                else "host_default_or_existing_config"
            ),
            "total_calls": (
                "instruction_only" if "max_calls_per_task" in data["limits"] else "not_configured"
            ),
            "delegation_targets": "instruction_only",
            "permissions": "requested_only_until_runtime_metadata_confirms_effective_sandbox",
        },
    }
    if dry:
        preview["legacy_agents_policy_restore"] = "AGENTS.md" in saved
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        return
    home.mkdir(parents=True, exist_ok=True)
    journal = {}
    for name, after in updates.items():
        target = _safe_target(home, name)
        before = saved[name]["before"] if name in saved else (target.read_text() if target.exists() else None)
        journal[name] = {"before": before, "after": after}
    migrating_agents_policy = "AGENTS.md" in saved
    transition_journal = dict(journal)
    if migrating_agents_policy:
        transition_journal["AGENTS.md"] = saved["AGENTS.md"]
    _atomic_write(state, json.dumps(transition_journal, indent=2, ensure_ascii=False) + "\n", 0o600)
    for name, after in updates.items():
        target = _safe_target(home, name)
        _atomic_write(target, after, 0o600 if name == "personal-agent-team-codex/team.json" else None)
    if migrating_agents_policy:
        target = _safe_target(home, "AGENTS.md")
        before = saved["AGENTS.md"]["before"]
        if before is None:
            target.unlink(missing_ok=True)
        else:
            _atomic_write(target, before)
        _atomic_write(state, json.dumps(journal, indent=2, ensure_ascii=False) + "\n", 0o600)
    print(json.dumps(preview, indent=2, ensure_ascii=False))


def resolve(data, cwd, agent, level=None):
    merged = effective_team(data, cwd)
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
            spec = args.spec or args.home / "personal-agent-team-codex/team.json"
            data = json.loads(spec.read_text())
            if args.command == "resolve":
                resolve(data, args.cwd, args.agent, args.level)
            else:
                apply(args.home, data, dry=args.command == "plan")
    except (KeyError, ValueError, OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
