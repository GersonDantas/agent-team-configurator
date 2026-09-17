# Equipe Pessoal Codex

Plugin Codex para configurar uma equipe pessoal com executor, consultor,
especialistas opcionais, níveis, modelos e limites.
Python 3.11+ e Codex com plugins e delegacao sao necessarios.

## Instalacao compartilhada

Extraia o pacote de distribuicao e, na raiz executor-consultor-distribution, execute:

    codex plugin marketplace add .
    codex plugin add executor-consultor@executor-consultor

Abra uma conversa e invoque configurar-equipe do plugin. Revise a equipe proposta.
A skill verifica disponibilidade antes de aplicar. Atualizar o plugin nao troca
suas escolhas nem executa o instalador.

Para Git, publique o conteudo de executor-consultor-distribution como raiz de um
repositorio. O destinatario substitui o ponto por DONO/REPOSITORIO no primeiro
comando. Nenhum repositorio remoto foi criado automaticamente.

## Uso manual

Na pasta do plugin, apos confirmar disponibilidade dos modelos:

    python3 scripts/team_config.py defaults > /tmp/equipe.json
    python3 scripts/team_config.py plan --spec /tmp/equipe.json
    python3 scripts/team_config.py apply --spec /tmp/equipe.json

Revise e ajuste o arquivo temporário antes de aplicar.

O padrão inicial mantém executor e consultor; modelos precisam ser confirmados
no catálogo disponível. Conversas existentes podem conservar
o modelo selecionado. AGENTS.md gerado ou consultor existente exigem conciliacao
pela skill. Nao ha hooks adicionais nem perguntas por prompt.

## Remover e recuperar

    python3 scripts/team_config.py uninstall --dry-run
    python3 scripts/team_config.py uninstall

Depois remova o plugin no Codex. Restauracao recusa sobrescrever edicoes posteriores.
O backup executor-consultor-state.json pode conter configuracoes privadas:
nao publique. Se houver interrupcao durante escrita, use esse backup para
conciliacao manual. Atualizacoes da politica exigem reexecutar a configuracao.

## Verificacao

Peça planejamento de mudança de contrato público e confira a chamada real ao
consultor. A política de total de chamadas e destinos orienta delegação, mas não
é um bloqueio determinístico. A concorrência usa o limite nativo quando suportado.
Compare qualidade e consumo reais; nao ha garantia de economia.
