# Technical plan: configurable personal team

Date: September 21, 2026. Status: workflows, triggers, and response contracts
implemented as behavioral policy; persistent state, hard budget controls, and
telemetry remain planned.

## 1. Expected outcome and approved decisions

Extend the current configurator to set up a personal team per conversation,
without requiring users to repeat routing instructions in every prompt.
Preserve the plugin's technical name at this stage to avoid another migration.

- Codex first; definitions independent of integration for future platforms.
- Global personal configuration and personal project exceptions outside repositories.
- Executor/coordinator and consultant initially; specialists and custom roles optional.
- Dynamic levels: Routine, Analysis, Critical, and Strategic. These are not a
  scientific scale.
- Suggested model and effort per level, approved by the user; per-agent exceptions.
- Automatic escalation within the approved range, with a reason; authorization
  required above it.
- Previously approved alternatives when a model is unavailable, with notice.
- Skill restrictions take precedence; explicit exceptions do not remove safety gates.
- Only the coordinator delegates by default. Delegation between agents is opt-in,
  with limited destinations and depth.
- Optional advanced limits. Without an explicit choice, preserve existing
  configuration or the host default. Concurrency can use native controls; budgets
  per task remain advisory until a validated guard exists.
- Brief notices and a final summary; minimal personal records without full
  prompts or code.
- Import existing configuration; preview, approval, and backup before applying.
- Conversational skill as the initial interface; readable file for advanced editing.

## 2. Evidence and research limitations

Initial inspection: CLI 0.147.0; plugin 0.1.0. Later validation in Codex App
0.155.0-alpha.2.6 showed a custom consultant requested as `read-only` running with
an effective `workspace-write` sandbox inherited from the main task.
The configurator manages native configuration, agents, a declarative team, and a
journal. Policy is injected through `SessionStart` without editing `AGENTS.md`.
There is no hard call budget or external router yet. Local command help confirms
that `codex debug models` exists.

Official documentation describes personal agents in `~/.codex/agents/*.toml`,
with name, description, instructions, and options such as model, effort, and
sandbox. It also documents `agents.max_concurrent_threads_per_session`, excluding
the main agent, and `agents.max_threads` as a legacy alias. These limit open
threads, not calls or necessarily the agents executing at that moment.
[Source: subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Hooks can intercept supported tools before execution. However, `SubagentStart`
does not prevent startup through `continue: false`; `PreToolUse` does not provide
a functional `permissionDecision: ask`. Do not use these fields to promise
approval or blocking. Coverage of actual delegation tools must be proven before
building a preventive counter.
[Source: hooks](https://learn.chatgpt.com/docs/hooks).

Online documentation and the installed client may differ. The reference page
consulted did not show the same concurrency key in a text search. Validate the
host schema and behavior before generating options.
[Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

This analysis did not execute delegations, blocking tests, or App tests. An
installed CLI does not prove the runtime version used by the application.

## 3. Feasibility matrix

| Feature | Proposed approach | Delivery condition |
| --- | --- | --- |
| Roles, model, and effort | Native files and supported delegation parameters | Confirm through actual metadata |
| Dynamic level selection | Coordinator policy + deterministic resolver for approved options | Semantic classification remains a model decision |
| Concurrency limit | Native cap on open threads, when supported | Test counting, release, and nested children |
| Total per task | Local counter before calls, if interception is proven | Do not advertise a hard limit without complete coverage |
| Who can delegate and depth | Available native restrictions + validated guard | Do not assume a depth key or per-role support |
| Read-only | Agent intent + effective sandbox confirmed by metadata | The App may inherit `workspace-write` from the parent; without metadata, mark unverified |
| Personal project exceptions | Local resolution through the canonical directory | Do not rewrite global configuration when switching projects |
| Notices and events | Concise policy + observed event records | Separate requested configuration from proven execution |

If interception is unreliable, offer advisory mode only with informed consent.
Do not silently weaken approved guarantees. A custom orchestration runtime would
expand scope rather than serve as an automatic fallback.

## 4. Proposed minimal architecture

Keep Python 3.11+ and the standard library for validation and installation. Do
not initially add an MCP server, background service, or graphical interface.

Four components:

1. `configurar-equipe` skill: interview, discovery, proposal, and approval.
   Keep `configurar-modelos` as a compatible entry without conflicting instructions.
2. Versioned declarative configuration: personal source of choices.
3. Resolver: combines default, project, role, level, restrictions, and availability.
4. Codex adapter: generates only supported options; identifies capabilities and
   guarantee levels. Guard/records only after feasibility testing.

Schema v2 centralizes normalization, validation, and project resolution in a
module shared by application and hook. It includes triggers, exclusions, a
response contract, and two workflows: trigger-based consultation and reviewed
plan. Version 1 schemas are normalized in memory without inferring new triggers;
only an approved `apply` persists version 2.

Selected location: `$CODEX_HOME/personal-agent-team-codex/`, defaulting to
`~/.codex/personal-agent-team-codex/`. The proposed layout uses `team.toml` for
choices, `projects/` for personal adjustments, `state/` for events/counters, and
`backups/` for recovery. Private directories and sensitive files have restricted
permissions; these data must not be included in the distributed package.

Identify projects by an approved canonical path. Worktrees may share a profile
through explicit association. Do not use only a folder name, remote URL, or
repository instructions to select personal configuration.

Do not swap global files for each task: two conversations in different projects
must run concurrently without one changing the other's model. Resolve parameters
per call when supported; native profiles generated per enabled combination are
an alternative to validate, without generating the entire Cartesian product.
Do not promise to change the main model in an already open conversation.

## 5. Data contract

| Group | Conceptual fields |
| --- | --- |
| Identity | Schema version, configuration revision |
| Levels | Stable ID, model, effort, approved alternatives |
| Agent | ID, name, objective, instructions, triggers, and exclusions |
| Routing | Default level, allowed levels, maximum, model/effort exceptions |
| Permissions | Read/write, allowed tools, preserved approvals |
| Delegation | Enabled, allowed destinations, maximum depth |
| Limits | Concurrent agents, total per task, explicit option to disable limits |
| Project | Local identifier, overridden fields, approved revision |
| Capabilities | Detected features, host/version, date, and tests performed |

Level, model, and effort are independent. Do not interpret model size as parameter
count or infer price/capability from catalog order. Show up to ten models per page
and allow viewing all. Missing reliable data requires human choice; cached
catalogs must be labeled as cached.

New models do not replace current ones automatically. Validate model/effort
combinations and alternatives; never expand permissions alongside a level.

## 6. Initial catalog and compatibility

| Suggested role | Use | Considerations |
| --- | --- | --- |
| Executor/coordinator | Coordination and integration | This is the main agent; do not create a copy per task |
| Consultant | Blockers, plans, and substantial milestones | Focused consultation; no repetition without new evidence |
| Architect | Structure, contracts, and migrations | Overlap with the consultant requires a distinct question |
| Specialized reviewer | Security, data, concurrency, or tests | Receives only the relevant scope |
| Independent verifier | Finding confirmation | Fresh context and blind verification |
| Merge analyst | Study of both change histories | Request read-only and confirm the actual sandbox |
| Functional auditor | Flows after integration | Does not replace parity tests |
| Documentation researcher | API contracts and versions | Optional; primary sources |

Suggested roles do not mean automatic creation/execution of every agent. Create
custom roles through a description and approved proposal. Specialists start with
read-only intent; the interface must show the sandbox as unverified until task
metadata confirms the restriction. Write permissions require separate approval.

For specialized review and integration workflows, preserve existing economical
classifications, ordinary agent ceilings, the consultant exception, and mandatory
procedures. Do not map Critical/DEEP automatically to a more expensive model. The
plugin's four levels do not replace internal skill classifications. Conflicts
without a compatible option must be disclosed rather than resolved by relaxing
limits.

A consultant acting as a verifier needs an independent instance, blind context,
and the schema required by the skill. Architecture consultation does not count
as a functional audit. Human triage, proofs, parity, and Git/publication approval
remain required. Do not edit third-party skills during installation without
specific approval.

## 7. Execution lifecycle and budget

Proposed operational definition: a task is an explicit objective with a local
identifier, persisted across turns until completion/cancellation. A new message,
compaction, or restart does not reset the budget. A new objective must be
identified as such.

1. Resolve the personal profile and applicable restrictions; do not open the
   configurator for every prompt.
2. Decide whether delegation is needed; simple work can stay with the executor.
3. Classify the level and select only approved, compatible combinations.
4. Check authorization, independence, destinations, depth, budget, and effective
   sandbox when the task depends on technical isolation.
5. Reserve a call atomically, announce it briefly, and execute.
6. Record the observed result, reconcile the reservation, and update the summary.

A call is a new assignment to a subagent: spawning or continuing an agent with
additional work. Polling/waiting does not count. Children and retries that begin
execution count; a confirmed failure before startup releases the reservation.
An uncertain result retains its reservation until reconciliation, without blind
retry. These semantics must be documented.

Use a local transaction (for example standard-library SQLite) if the guard is
feasible. Test races, duplicates, interruptions, and recovery. Open thread limits
and call limits differ; a completed agent may still need to be closed to release
a native slot. Do not count SubagentStop as closure without evidence.

Above the limit, deny new delegation and have the coordinator request a user
decision. Do not simulate approval through a hook. A temporary exception must be
limited to the task and recorded without permanently raising the default.

Minimal record: time, task, parent/child, role, level, brief reason, requested and
observed model/effort, substitution, state, and available guarantee. Do not record
internal reasoning, prompts, code, credentials, or tool payloads. Propose editable
30-day retention, subject to initial approval. Do not describe agent counts or
RTK gain as proven financial savings.

## 8. Safe migration

1. Inspect existing files and symlinks without running configuration.
2. Import the executor, consultant, and current choices. Do not change models
   based on suggestions.
3. Show the diff, affected files, limitations, and permissions for approval.
4. Generate in staging, validate, and create a private backup and recovery journal.
5. Apply files individually with atomic writes and recovery from interruption
   between files; do not call the entire operation a fully atomic transaction.
6. Verify hashes and state. Reexecution must be idempotent without duplicated policy.

Preserve providers, endpoints, RTK hooks, credentials, tools, and permissions. Do
not edit `AGENTS.md`: persistent policy comes from the plugin's `SessionStart`
hook. Do not rely on `@` imports. The user must review and trust the hook, which
must reapply context after compaction.

The 0.1.0 journal stores full snapshots. Migration must preserve recovery and
start tracking change ownership without overwriting later edits. Name collisions,
manual configurations, and external changes require reconciliation. Uninstallation
removes/reverts only managed items and preserves unrelated content.

## 9. Stages and acceptance criteria

| Stage | Deliverable | Verification |
| --- | --- | --- |
| 0. Feasibility | CLI/App host matrix and control strategy | Isolated host, limits, nesting, hooks, and metadata |
| 1. Data | Versioned schema and pure resolver | Invalid input, precedence, alternatives, and cycles |
| 2. Interface | Skill and optional catalog | Create/edit/disable flows, preview, no writes before approval |
| 3. Installation | Compatible import and generation | Temporary home, idempotence, interruption, symlinks, rollback |
| 4. Controls | Proven guard or explicitly approved limitation | Call races, retries, restart, children, and bypasses |
| 5. Integration | Review/merge examples | Economy, blind verification, parity, and preserved gates |
| 6. Distribution | Documentation and package | Skill/plugin validators and clean installation |

Required negative tests: two concurrent calls competing for the last slot;
delegation to a forbidden destination; unavailable model; invalid effort; limit
reached after compaction; two projects in parallel; custom role with a colliding
name; requested/effective sandbox mismatch; external write tool; generated
AGENTS.md source.

Final criterion: the user configures once, a new session uses the policy without
a special prompt, execution proves models/efforts, migration preserves
configuration, and every control is marked native, validated by the plugin, or
advisory only.

Do not perform a real merge/review, publish, change personal installation, or
make paid validation calls without corresponding authorization. Implement and
test in temporary directories first. Publication and personal migration are
separate steps.

## 10. Recommended next action

Start with stage 0 and the pure resolver. Do not rewrite the entire installer
before finding out whether the runtime can enforce approved limits. If it cannot,
present the limitation and obtain a decision about advisory mode or additional
scope.
