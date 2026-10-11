# Agent Team Configurator

A cross-platform repository for configuring personal agent teams. The current
version provides the Codex **Personal Agent Team** package. A Claude Code adapter
is listed on the roadmap and will be developed in a separate pull request.

## Install in Codex

The plugin uses the same GitHub marketplace workflow adopted by plugins such as
Ponytail. Run the following commands in a terminal:

```sh
codex plugin marketplace add GersonDantas/agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

Then start the Codex CLI:

```sh
codex
```

Inside the CLI, open `/hooks`, review the **Loading personal agent team** hook,
and mark it as trusted. The `/hooks` command is available in the Codex CLI; it
does not appear as a command in the Codex App.

Restart the Codex App, open a new conversation, and select **Personal Agent Team
Codex: Configurar Equipe**, or ask:

> Use configurar-equipe to configure my personal agent team.

The hook injects the policy at session start and after context compaction without
modifying `AGENTS.md`.

Installing the plugin does not change models automatically. The skill presents
the configuration, validates models, shows the files involved, and asks for
approval before writing to the personal configuration.

The repository must be public for open installation. While it is private, only
accounts with repository access and authenticated GitHub credentials can add the
marketplace.

The complete installation guide, including verification, updates, and removal,
is available in [docs/instalacao.md](docs/instalacao.md).

To change models without the interactive skill, see
[docs/configuracao-manual-modelos.md](docs/configuracao-manual-modelos.md). The
guide covers the file map, safe specification editing, validation, application,
and per-project overrides.

## What it configures

- Initial executor and consultant agents.
- Optional personal specialists.
- Routine, Analysis, Critical, and Strategic levels.
- Approved models, reasoning efforts, and fallbacks.
- Optional concurrency in advanced settings. Without an explicit choice, the
  plugin preserves the existing configuration or the host default.
- Optional call budgets and delegation targets as advisory policy until a
  validated runtime guard is available.
- Read-only permission as configured intent, always distinguished from the
  sandbox actually observed in the task.
- Personal per-project exceptions stored outside the project repository.
- Policy loaded by a session-start hook without editing `AGENTS.md`.
- Configurable triggers and exclusions for each agent.
- Workflows for trigger-based consultation or mandatory plan review.
- A response contract with outcomes that either allow progress or keep a step
  pending.

## Current structure

```text
.agents/plugins/marketplace.json
plugins/personal-agent-team-codex/
  .codex-plugin/plugin.json
  skills/
  hooks/
  scripts/
  templates/
docs/
scripts/build-submission.sh
```

The future cross-platform architecture is documented in
[docs/roadmap-multiplataforma.md](docs/roadmap-multiplataforma.md). It is not
part of the current implementation.

## Test

```sh
python3 plugins/personal-agent-team-codex/scripts/test_setup.py
python3 plugins/personal-agent-team-codex/scripts/test_team_config.py
python3 plugins/personal-agent-team-codex/scripts/test_session_context.py
```

For a clean-install test, use a temporary `CODEX_HOME` or another system user.
The detailed guide is available in
[docs/guia-testes-delegacao.md](docs/guia-testes-delegacao.md).

## Submission package

```sh
scripts/build-submission.sh
```

The ZIP is created at `dist/personal-agent-team-codex-0.5.0.zip`. Official store
submission still depends on real CLI/App tests, verified identity, and the public
materials required by the store.

## Recover older versions

`setup.py` exists only to restore legacy 0.1 installations that contain
`executor-consultor-state.json`. It refuses new installations. After restoring
the old version, use `configurar-equipe` for a clean 0.2 installation.

## Privacy

Personal configurations, journals, and backups are not included in the
repository or ZIP. Do not publish these files. The hook reads only the local
`team.json`, and the plugin does not send data on its own.
