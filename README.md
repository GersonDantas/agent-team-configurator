# Agent Team Configurator

Repositório multiplataforma para configurar equipes pessoais de agentes. A versão
atual oferece o pacote Codex **Personal Agent Team**. Um adaptador para Claude Code
está registrado no roadmap e será desenvolvido em outro pull request.

## Instalar no Codex

```sh
codex plugin marketplace add GersonDantas/agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

Abra uma conversa nova e peça:

> Use configurar-equipe para configurar minha equipe pessoal de agentes.

A instalação do plugin não altera modelos automaticamente. A skill apresenta a
configuração, valida modelos, mostra os arquivos envolvidos e pede aprovação antes
de escrever na configuração pessoal.

## O que configura

- Executor e consultor iniciais.
- Especialistas pessoais opcionais.
- Níveis Rotina, Análise, Crítico e Estratégico.
- Modelos, esforços e alternativas aprovadas.
- Limite nativo de concorrência quando suportado pelo host.
- Limite total e destinos de delegação como política orientativa até existir uma
  guarda de runtime validada.
- Exceções pessoais por projeto, armazenadas fora do repositório do projeto.

## Estrutura atual

```text
.agents/plugins/marketplace.json
plugins/personal-agent-team-codex/
  .codex-plugin/plugin.json
  skills/
  scripts/
  templates/
docs/
scripts/build-submission.sh
```

A arquitetura multiplataforma futura está documentada em
[docs/roadmap-multiplataforma.md](docs/roadmap-multiplataforma.md). Ela não faz
parte da implementação atual.

## Testar

```sh
python3 plugins/personal-agent-team-codex/scripts/test_setup.py
python3 plugins/personal-agent-team-codex/scripts/test_team_config.py
```

Para teste de instalação limpa, use um `CODEX_HOME` temporário ou outro usuário do
sistema. O guia detalhado está em
[docs/guia-testes-delegacao.md](docs/guia-testes-delegacao.md).

## Pacote para submissão

```sh
scripts/build-submission.sh
```

O ZIP é criado em `dist/personal-agent-team-codex-0.2.0.zip`. A submissão oficial
ainda depende de testes reais no CLI/App, identidade verificada e materiais
públicos exigidos pela loja.

## Recuperação de versões antigas

`setup.py` existe somente para restaurar instalações legadas 0.1 que possuam
`executor-consultor-state.json`. Ele recusa novas instalações. Após restaurar a
versão antiga, use `configurar-equipe` para uma instalação 0.2 limpa.

## Privacidade

Configurações, journals e backups pessoais não fazem parte do repositório ou do
ZIP. Não publique esses arquivos. O plugin não envia dados por conta própria.
