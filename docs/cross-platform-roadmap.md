# Cross-platform roadmap

This architecture is recorded for later implementation in a separate pull
request. Current work remains limited to the Codex adapter.

```text
agent-team-configurator/
├── core/                 # independent schema, validation, and resolution
├── adapters/
│   ├── codex/            # AGENTS.md, agents/*.toml, and Codex integration
│   └── claude-code/      # CLAUDE.md, agents, hooks, and Claude Code integration
├── plugins/
│   ├── codex/
│   └── claude-code/
├── docs/
└── tests/
```

## Principles for the future PR

- Extract only logic proven to be shared, without anticipating abstractions.
- Keep installation, permissions, hooks, and packaging specific to each platform.
- Reuse the schema for roles, levels, models, limits, and personal exceptions.
- Do not assume Codex and Claude Code provide the same runtime controls.
- Preserve independent migration and uninstallation for each adapter.
- Test each package separately and publish distinct identifiers.

Planned names:

- Repository and project: `agent-team-configurator`.
- Product: `Personal Agent Team`.
- Codex package: `personal-agent-team-codex`.
- Future Claude Code package: `personal-agent-team-claude`.
