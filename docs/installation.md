# Installation from GitHub

Personal Agent Team is distributed through a Git marketplace, using the same
format as plugins such as Ponytail. The installation applies to the Codex CLI
and Codex App on the same machine.

## Requirements

- Codex CLI installed and authenticated.
- Git installed.
- Repository access. If it is private, the local GitHub account must have read
  access.

## Install

Run these two commands separately in a terminal:

```sh
codex plugin marketplace add GersonDantas/agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

The first registers the repository as a marketplace. The second installs the
plugin from that marketplace.

## Trust the hook

The plugin uses a `SessionStart` hook to load the personal team policy into each
conversation and after context compaction. Hooks installed by plugins must be
reviewed before their first execution.

Open the Codex CLI:

```sh
codex
```

Inside the CLI, run `/hooks`, find **Loading personal agent team**, review its
command, and mark the hook as trusted.

`/hooks` is a Codex CLI command. It does not appear in the Codex App. The trust
recorded by the CLI is used by Codex on the same machine.

## First configuration in the Codex App

Restart the Codex App after installation and open a new conversation. Type
`$configurar` and select **Personal Agent Team Codex: Configurar Equipe**.

Use **Configurar Modelos** only when the team already exists and you want to
change the executor or consultant models while preserving other roles, levels,
and limits.

The configuration is personal and stored outside your working repositories. The
plugin shows a preview and asks for approval before writing files.

During initial setup, choose trigger-based consultation (recommended) or a plan
that is always reviewed. Triggers, exclusions, and the response contract can be
customized. These controls are policies loaded into context; the interface
identifies any controls technically enforced by the runtime separately.

## Verify

In a terminal, confirm that the plugin is installed and enabled:

```sh
codex plugin list
```

Look for:

```text
personal-agent-team-codex@agent-team-configurator  installed, enabled
```

After configuring the team, open another conversation in the Codex App. The new
conversation should load the policy automatically. Configuration should neither
add nor modify the user's or project's `AGENTS.md`.

To check the workflow, request a public contract change and verify that the
consultant is called before implementation. Then request a small mechanical
change and confirm that it does not trigger consultation when no mandatory
trigger applies. A `revise`, `insufficient_information`, interrupted, or invalid
response must leave the dependent step pending.

## Update

Update the marketplace copy and reinstall the plugin:

```sh
codex plugin marketplace upgrade agent-team-configurator
codex plugin remove personal-agent-team-codex@agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

If the hook definition changes, open `/hooks` again in the Codex CLI and review
the new version. Start a new conversation after updating.

## Remove

First use **Configurar Equipe** to request removal of the personal configuration.
The configurator shows a preview before restoring files and removing state owned
by the plugin.

Then remove the plugin and, if you no longer use any plugins from this
marketplace, remove the marketplace as well:

```sh
codex plugin remove personal-agent-team-codex@agent-team-configurator
codex plugin marketplace remove agent-team-configurator
```

Removing only the plugin should not replace guided removal of the personal
configuration, because backups and generated files are stored outside the plugin
cache.

## Common problems

### The marketplace cannot be cloned

Confirm that the repository exists and your account has access. Distribution
without individual invitations requires a public repository.

### The plugin appears, but the policy does not load

Open the Codex CLI, run `/hooks`, and confirm that **Loading personal agent team**
is trusted. Then open a new conversation.

### `/hooks` does not appear in the App

This command exists only in the Codex CLI interface. Run `codex` in a terminal
and use `/hooks` inside it.
