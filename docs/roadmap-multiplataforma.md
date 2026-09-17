# Roadmap multiplataforma

Esta arquitetura está registrada para implementação posterior em outro pull
request. O trabalho atual continua limitado ao adaptador Codex.

```text
agent-team-configurator/
├── core/                 # esquema, validação e resolução independentes
├── adapters/
│   ├── codex/            # AGENTS.md, agents/*.toml e integração Codex
│   └── claude-code/      # CLAUDE.md, agents, hooks e integração Claude Code
├── plugins/
│   ├── codex/
│   └── claude-code/
├── docs/
└── tests/
```

## Princípios para o futuro PR

- Extrair apenas lógica comprovadamente compartilhada, sem antecipar abstrações.
- Manter instalação, permissões, hooks e empacotamento específicos por plataforma.
- Reutilizar o esquema de papéis, níveis, modelos, limites e exceções pessoais.
- Não presumir que Codex e Claude Code oferecem os mesmos controles de runtime.
- Preservar migração e desinstalação independentes para cada adaptador.
- Testar cada pacote separadamente e publicar identificadores distintos.

Nomes planejados:

- Repositório e projeto: `agent-team-configurator`.
- Produto: `Personal Agent Team`.
- Pacote Codex: `personal-agent-team-codex`.
- Futuro pacote Claude Code: `personal-agent-team-claude`.
