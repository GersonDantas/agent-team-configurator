"""Canonical schema, validation, migration, and project resolution for agent teams."""

import json
from pathlib import Path
import re


SCHEMA_VERSION = 2
LEVELS = ("rotina", "analise", "critico", "estrategico")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")

CONSULTOR_TRIGGERS = [
    {
        "id": "architecture",
        "description": "Mudanca arquitetural com impacto em varios componentes.",
        "timing": "before_implementation",
        "required": True,
    },
    {
        "id": "public_contract",
        "description": "Mudanca de contrato publico, mesmo quando localizada.",
        "timing": "before_implementation",
        "required": True,
    },
    {
        "id": "persistent_blocker",
        "description": "Duas tentativas substanciais sem resolver o mesmo bloqueio.",
        "timing": "before_next_attempt",
        "required": True,
    },
    {
        "id": "substantial_milestone",
        "description": "Marco substancial concluido com evidencias de validacao.",
        "timing": "before_completion",
        "required": True,
    },
    {
        "id": "explicit_request",
        "description": "Pedido explicito do usuario para consultar o papel.",
        "timing": "when_requested",
        "required": True,
    },
]

CONSULTOR_CONTRACT = {
    "contract_version": 1,
    "required_fields": [
        "request_id",
        "plan_revision",
        "analysis_status",
        "findings",
        "evidence",
        "hypotheses",
        "recommendation",
        "required_validations",
        "outcome",
    ],
    "outcomes": ["proceed", "revise", "insufficient_information"],
    "blocking_outcomes": ["revise", "insufficient_information"],
}

WORKFLOWS = {
    "consultation_on_trigger": {
        "description": "O executor trabalha e consulta quando um acionamento configurado se aplica.",
        "steps": [
            {"id": "execute", "agent": "executor", "when": "default"},
            {
                "id": "consult",
                "agent": "consultor",
                "when": "matching_trigger",
                "requires_response": True,
            },
        ],
    },
    "reviewed_plan": {
        "description": "O executor prepara o plano, o consultor revisa e a implementacao aguarda o parecer.",
        "steps": [
            {"id": "plan", "agent": "executor", "when": "always"},
            {
                "id": "review_plan",
                "agent": "consultor",
                "when": "always",
                "requires_response": True,
            },
            {
                "id": "implement",
                "agent": "executor",
                "when": "after_non_blocking_outcome",
                "after": ["review_plan"],
            },
        ],
    },
}


def _copy(value):
    return json.loads(json.dumps(value))


def requested_read_only(item):
    has_requested = "requested_read_only" in item
    has_legacy = "read_only" in item
    if not has_requested and not has_legacy:
        raise ValueError("agent permission intent is missing")
    if has_requested and not isinstance(item["requested_read_only"], bool):
        raise ValueError("requested_read_only must be boolean")
    if has_legacy and not isinstance(item["read_only"], bool):
        raise ValueError("read_only must be boolean")
    if has_requested and has_legacy and item["requested_read_only"] != item["read_only"]:
        raise ValueError("requested_read_only conflicts with legacy read_only")
    return item["requested_read_only"] if has_requested else item["read_only"]


def normalize(data):
    """Normalize v1/v2 into v2 without mutating input or enabling new v1 triggers."""
    normalized = _copy(data)
    version = normalized.get("schema_version")
    if version not in (1, SCHEMA_VERSION):
        raise ValueError(f"schema_version must be 1 or {SCHEMA_VERSION}")
    if version == 1:
        normalized["schema_version"] = SCHEMA_VERSION
        for item in normalized.get("agents", {}).values():
            if isinstance(item, dict):
                item.setdefault("triggers", [])
                item.setdefault("exclusions", [])
                item.setdefault("response_contract", {})
        global_agents = normalized.get("agents", {})
        for override in normalized.get("project_overrides", {}).values():
            if not isinstance(override, dict):
                continue
            for name, item in override.get("agents", {}).items():
                if name not in global_agents and isinstance(item, dict):
                    item.setdefault("triggers", [])
                    item.setdefault("exclusions", [])
                    item.setdefault("response_contract", {})
        normalized.setdefault(
            "workflow",
            {"active": "consultation_on_trigger", "definitions": _copy(WORKFLOWS)},
        )
    return normalized


def _validate_agent(name, item, agents):
    if not NAME.fullmatch(name) or not isinstance(item, dict):
        raise ValueError(f"invalid agent: {name}")
    for field in ("description", "instructions"):
        if not isinstance(item.get(field), str) or not item[field].strip() or '"""' in item[field]:
            raise ValueError(f"invalid {field} in {name}")
    if item.get("default_level") not in LEVELS or item.get("max_level") not in LEVELS:
        raise ValueError(f"invalid level in {name}")
    if LEVELS.index(item["default_level"]) > LEVELS.index(item["max_level"]):
        raise ValueError(f"default level exceeds maximum in {name}")
    requested = requested_read_only(item)
    item["requested_read_only"] = requested
    item["read_only"] = requested
    if not isinstance(item.get("can_delegate"), bool):
        raise ValueError(f"invalid delegation permission in {name}")
    targets = item.get("delegates_to", [])
    if not isinstance(targets, list) or any(target not in agents or target == name for target in targets):
        raise ValueError(f"invalid delegation destinations in {name}")
    if not item["can_delegate"] and targets:
        raise ValueError(f"{name} cannot delegate but has destinations")

    triggers = item.get("triggers")
    if not isinstance(triggers, list):
        raise ValueError(f"invalid triggers in {name}")
    trigger_ids = set()
    for trigger in triggers:
        expected = {"id", "description", "timing", "required"}
        if not isinstance(trigger, dict) or set(trigger) != expected:
            raise ValueError(f"invalid trigger in {name}")
        if not NAME.fullmatch(trigger["id"]) or trigger["id"] in trigger_ids:
            raise ValueError(f"invalid or duplicate trigger id in {name}")
        trigger_ids.add(trigger["id"])
        if not isinstance(trigger["description"], str) or not trigger["description"].strip():
            raise ValueError(f"invalid trigger description in {name}")
        if not isinstance(trigger["timing"], str) or not trigger["timing"].strip():
            raise ValueError(f"invalid trigger timing in {name}")
        if not isinstance(trigger["required"], bool):
            raise ValueError(f"invalid trigger requirement in {name}")

    if any(trigger["required"] for trigger in triggers):
        delegators = [
            source
            for source, source_item in agents.items()
            if source_item.get("can_delegate") and name in source_item.get("delegates_to", [])
        ]
        if not delegators:
            raise ValueError(f"required triggers for unreachable agent {name}")

    exclusions = item.get("exclusions")
    if not isinstance(exclusions, list) or any(
        not isinstance(value, str) or not value.strip() for value in exclusions
    ):
        raise ValueError(f"invalid exclusions in {name}")

    contract = item.get("response_contract")
    if not isinstance(contract, dict):
        raise ValueError(f"invalid response contract in {name}")
    if contract:
        expected = {"contract_version", "required_fields", "outcomes", "blocking_outcomes"}
        if set(contract) != expected or contract["contract_version"] != 1:
            raise ValueError(f"invalid response contract fields in {name}")
        for field in ("required_fields", "outcomes", "blocking_outcomes"):
            values = contract[field]
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value for value in values
            ) or len(values) != len(set(values)):
                raise ValueError(f"invalid {field} in {name}")
        if not set(contract["blocking_outcomes"]).issubset(contract["outcomes"]):
            raise ValueError(f"blocking outcomes outside outcomes in {name}")


def _validate_workflow(workflow, agents):
    if not isinstance(workflow, dict) or set(workflow) != {"active", "definitions"}:
        raise ValueError("workflow must contain active and definitions")
    definitions = workflow["definitions"]
    if not isinstance(definitions, dict) or workflow["active"] not in definitions:
        raise ValueError("active workflow does not exist")
    for name, definition in definitions.items():
        if not NAME.fullmatch(name) or not isinstance(definition, dict):
            raise ValueError(f"invalid workflow: {name}")
        if set(definition) != {"description", "steps"}:
            raise ValueError(f"invalid workflow fields in {name}")
        if not isinstance(definition["description"], str) or not definition["description"].strip():
            raise ValueError(f"invalid workflow description in {name}")
        steps = definition["steps"]
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"invalid workflow steps in {name}")
        seen = set()
        for step in steps:
            allowed = {"id", "agent", "when", "requires_response", "after"}
            if not isinstance(step, dict) or not {"id", "agent", "when"}.issubset(step) or set(step) - allowed:
                raise ValueError(f"invalid workflow step in {name}")
            if not NAME.fullmatch(step["id"]) or step["id"] in seen:
                raise ValueError(f"invalid or duplicate step id in {name}")
            if step["agent"] not in agents:
                raise ValueError(f"unknown agent in workflow {name}: {step['agent']}")
            if not isinstance(step["when"], str) or not step["when"].strip():
                raise ValueError(f"invalid step condition in {name}")
            if "requires_response" in step and not isinstance(step["requires_response"], bool):
                raise ValueError(f"invalid requires_response in {name}")
            if step.get("requires_response") and name == workflow["active"]:
                contract = agents[step["agent"]].get("response_contract", {})
                reachable = any(
                    agents[previous["agent"]].get("can_delegate")
                    and step["agent"] in agents[previous["agent"]].get("delegates_to", [])
                    for previous in steps[: len(seen)]
                )
                is_conditional_without_triggers = (
                    step["when"] == "matching_trigger"
                    and not agents[step["agent"]].get("triggers")
                )
                if not is_conditional_without_triggers and not contract:
                    raise ValueError(f"response contract required for step {step['id']} in {name}")
                if not is_conditional_without_triggers and not reachable:
                    raise ValueError(f"no authorized delegation path for step {step['id']} in {name}")
            dependencies = step.get("after", [])
            if not isinstance(dependencies, list) or any(value not in seen for value in dependencies):
                raise ValueError(f"invalid step dependency in {name}")
            seen.add(step["id"])


def _merge_override(data, override):
    merged = _copy(data)
    override = _copy(override)
    for item in override.get("agents", {}).values():
        if not isinstance(item, dict):
            continue
        has_requested = "requested_read_only" in item
        has_legacy = "read_only" in item
        if has_requested and has_legacy and item["requested_read_only"] != item["read_only"]:
            raise ValueError("conflicting permission aliases in project override")
        if has_requested:
            item["read_only"] = item["requested_read_only"]
        elif has_legacy:
            item["requested_read_only"] = item["read_only"]
    for section in ("levels", "agents", "limits", "workflow"):
        if section not in override:
            continue
        for key, value in override[section].items():
            if isinstance(value, dict) and isinstance(merged[section].get(key), dict):
                merged[section][key].update(_copy(value))
            else:
                merged[section][key] = _copy(value)
    return merged


def validate(data, validate_overrides=True):
    data = normalize(data)
    levels = data.get("levels")
    if not isinstance(levels, dict) or set(levels) != set(LEVELS):
        raise ValueError("levels must contain rotina, analise, critico and estrategico")
    for name, item in levels.items():
        if not isinstance(item, dict) or not isinstance(item.get("model"), str) or not item["model"]:
            raise ValueError(f"invalid model in {name}")
        if item.get("effort") not in EFFORTS:
            raise ValueError(f"invalid effort in {name}")
        fallbacks = item.get("fallbacks", [])
        if not isinstance(fallbacks, list) or any(not isinstance(value, str) or not value for value in fallbacks):
            raise ValueError(f"invalid fallbacks in {name}")

    agents = data.get("agents")
    if not isinstance(agents, dict) or "executor" not in agents or "consultor" not in agents:
        raise ValueError("agents must contain executor and consultor")
    for name, item in agents.items():
        _validate_agent(name, item, agents)
    _validate_workflow(data.get("workflow"), agents)

    limits = data.get("limits")
    if not isinstance(limits, dict):
        raise ValueError("limits must be an object")
    unknown_limits = set(limits) - {"max_concurrent", "max_calls_per_task"}
    if unknown_limits:
        raise ValueError(f"unknown limits: {sorted(unknown_limits)}")
    for key, value in limits.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"{key} must be a positive integer")

    overrides = data.get("project_overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("project_overrides must be an object")
    for path, override in overrides.items():
        if not Path(path).is_absolute() or not isinstance(override, dict):
            raise ValueError(f"invalid project override: {path}")
        unknown = set(override) - {"limits", "agents", "levels", "workflow"}
        if unknown:
            raise ValueError(f"unknown override fields in {path}: {sorted(unknown)}")
        for section in override:
            if not isinstance(override[section], dict):
                raise ValueError(f"invalid override section in {path}: {section}")
        if validate_overrides:
            candidate = _merge_override(data, override)
            candidate["project_overrides"] = {}
            validate(candidate, validate_overrides=False)
    return data


def effective_team(data, cwd):
    data = validate(data)
    path = str(Path(cwd).resolve())
    matches = [
        (root, override)
        for root, override in data["project_overrides"].items()
        if path == root or path.startswith(root.rstrip("/") + "/")
    ]
    if not matches:
        return data
    _, override = max(matches, key=lambda pair: len(pair[0]))
    merged = _merge_override(data, override)
    merged["project_overrides"] = data["project_overrides"]
    return validate(merged, validate_overrides=False)
