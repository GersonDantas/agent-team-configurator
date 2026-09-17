# Agent Team Configurator

Repositório multiplataforma para configurar equipes pessoais de agentes. A versão
atual oferece o pacote Codex **Personal Agent Team**. Um adaptador para Claude Code
está registrado no roadmap e será desenvolvido em outro pull request.

## Instalar no Codex

O plugin usa o mesmo fluxo de marketplace por GitHub adotado por plugins como o
Ponytail. No terminal, execute:

```sh
codex plugin marketplace add GersonDantas/agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

Depois, inicie o Codex CLI:

```sh
codex
```

Dentro do CLI, abra `/hooks`, revise e confie o hook **Loading personal agent
team**. O comando `/hooks` existe no Codex CLI; ele não aparece como comando no
Codex App.

Reinicie o Codex App, abra uma conversa nova e selecione **Personal Agent Team
Codex: Configurar Equipe**, ou peça:

> Use configurar-equipe para configurar minha equipe pessoal de agentes.

O hook injeta a política no início da sessão e após compactações, sem modificar
`AGENTS.md`.

A instalação do plugin não altera modelos automaticamente. A skill apresenta a
configuração, valida modelos, mostra os arquivos envolvidos e pede aprovação antes
de escrever na configuração pessoal.

O repositório precisa estar público para instalação aberta. Enquanto estiver
privado, somente contas com acesso ao repositório e GitHub autenticado poderão
adicionar o marketplace.

O passo a passo completo, incluindo verificação, atualização e remoção, está em
[docs/instalacao.md](docs/instalacao.md).

## O que configura

- Executor e consultor iniciais.
- Especialistas pessoais opcionais.
- Níveis Rotina, Análise, Crítico e Estratégico.
- Modelos, esforços e alternativas aprovadas.
- Limite nativo de concorrência quando suportado pelo host.
- Limite total e destinos de delegação como política orientativa até existir uma
  guarda de runtime validada.
- Exceções pessoais por projeto, armazenadas fora do repositório do projeto.
- Política carregada por hook no início da sessão, sem editar `AGENTS.md`.

## Estrutura atual

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

A arquitetura multiplataforma futura está documentada em
[docs/roadmap-multiplataforma.md](docs/roadmap-multiplataforma.md). Ela não faz
parte da implementação atual.

## Testar

```sh
python3 plugins/personal-agent-team-codex/scripts/test_setup.py
python3 plugins/personal-agent-team-codex/scripts/test_team_config.py
python3 plugins/personal-agent-team-codex/scripts/test_session_context.py
```

Para teste de instalação limpa, use um `CODEX_HOME` temporário ou outro usuário do
sistema. O guia detalhado está em
[docs/guia-testes-delegacao.md](docs/guia-testes-delegacao.md).

## Pacote para submissão

```sh
scripts/build-submission.sh
```

O ZIP é criado em `dist/personal-agent-team-codex-0.3.0.zip`. A submissão oficial
ainda depende de testes reais no CLI/App, identidade verificada e materiais
públicos exigidos pela loja.

## Recuperação de versões antigas

`setup.py` existe somente para restaurar instalações legadas 0.1 que possuam
`executor-consultor-state.json`. Ele recusa novas instalações. Após restaurar a
versão antiga, use `configurar-equipe` para uma instalação 0.2 limpa.

## Privacidade

Configurações, journals e backups pessoais não fazem parte do repositório ou do
ZIP. Não publique esses arquivos. O hook lê apenas `team.json` localmente e o
plugin não envia dados por conta própria.
