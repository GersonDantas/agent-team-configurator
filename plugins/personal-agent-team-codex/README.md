# Personal Agent Team for Codex

Plugin Codex para configurar uma equipe pessoal com executor, consultor,
especialistas opcionais, níveis, modelos e limites.

## Instalação pelo repositório

```sh
codex plugin marketplace add GersonDantas/agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

Abra uma conversa nova e use `configurar-equipe`. A skill valida modelos e mostra
uma prévia antes de alterar a configuração pessoal.

## Uso manual em ambiente de teste

```sh
python3 scripts/team_config.py defaults > /tmp/equipe.json
python3 scripts/team_config.py plan --spec /tmp/equipe.json
python3 scripts/team_config.py apply --spec /tmp/equipe.json
```

Revise o arquivo temporário antes de aplicar. O total de chamadas e os destinos de
delegação são políticas orientativas; apenas a concorrência possui limite nativo
quando o host oferece suporte.

## Remover uma instalação 0.2

```sh
python3 scripts/team_config.py uninstall --dry-run
python3 scripts/team_config.py uninstall
```

A restauração recusa sobrescrever mudanças posteriores. O backup
`personal-agent-team-codex-state.json` é privado e não deve ser publicado.

## Recuperar uma instalação legada 0.1

```sh
python3 scripts/setup.py --uninstall
```

`setup.py` é somente um recuperador legado e recusa novas instalações. Restaure a
versão antiga antes de iniciar uma instalação 0.2.

## Verificação

Confira chamadas reais e metadados do modelo, não apenas declarações do agente.
Compare qualidade, consumo e tempo em tarefas equivalentes. Não há garantia de
economia.
