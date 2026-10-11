# Personal Agent Team for Codex

Codex plugin for configuring a personal team with an executor, consultant,
optional specialists, levels, models, limits, triggers, and workflows.

## Install from the repository

```sh
codex plugin marketplace add GersonDantas/agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

Open `codex` in a terminal and run `/hooks` inside the Codex CLI. Review and trust
the **Loading personal agent team** hook. The `/hooks` command does not appear in
the Codex App.

Restart the Codex App, open a new conversation, and use `configurar-equipe`. The
skill validates models and shows a preview before changing personal configuration.

In the first conversation after installation or update, the hook loads policy
at startup and after compaction without editing `AGENTS.md`. Without trust
recorded in the CLI, agents remain configured, but selection, delegation, and
limit policies are not loaded into context.

The complete installation, verification, update, and removal guide is available
in [../../docs/installation.md](../../docs/installation.md).

To configure models manually without the interactive skill, use
[../../docs/manual-models-configuration.md](../../docs/manual-models-configuration.md).
The procedure preserves configurator validation and the journal.

## Manual use in a test environment

```sh
python3 scripts/team_config.py defaults > /tmp/team.json
python3 scripts/team_config.py plan --spec /tmp/team.json
python3 scripts/team_config.py apply --spec /tmp/team.json
```

Review the temporary file before applying. Concurrency is an advanced option and
uses native controls when configured and supported by the host. Total call
budgets and delegation targets are advisory policies. An agent's `read-only`
permission represents configured intent; confirm the actual sandbox in task
metadata before treating the agent as technically isolated.

The recommended `consultation_on_trigger` workflow consults only when a configured
trigger applies. `reviewed_plan` requires a review of the plan before
implementation. Transitions, trigger classification, and response format remain
behavioral policies until a validated runtime guard exists. Version 1
configurations remain readable and are persisted as version 2 on the next `apply`,
without automatically creating mandatory triggers.

## Remove a version 0.2 or later installation

```sh
python3 scripts/team_config.py uninstall --dry-run
python3 scripts/team_config.py uninstall
```

Restoration refuses to overwrite later changes. The
`personal-agent-team-codex-state.json` backup is private and must not be published.
When updating a version 0.2 installation, the configurator restores the version
of `AGENTS.md` saved in the journal and switches to the hook.

## Recover a legacy version 0.1 installation

```sh
python3 scripts/setup.py --uninstall
```

`setup.py` is only a legacy recovery tool and refuses new installations. Restore
the old version before starting a version 0.2 installation.

## Verification

```sh
python3 scripts/test_team_config.py
python3 scripts/test_session_context.py
```

Check actual calls and model metadata, not just agent declarations. Compare
quality, usage, and time across equivalent tasks. Savings are not guaranteed.
