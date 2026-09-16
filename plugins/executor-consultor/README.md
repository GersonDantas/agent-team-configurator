# Executor Consultor

Plugin Codex com executor cotidiano e consultor para planos, bloqueios e marcos.
Python 3.11+ e Codex com plugins e delegacao sao necessarios.

## Instalacao compartilhada

Extraia o pacote de distribuicao e, na raiz executor-consultor-distribution, execute:

    codex plugin marketplace add .
    codex plugin add executor-consultor@executor-consultor

Abra uma conversa e invoque configurar-modelos do plugin. Escolha os modelos.
A skill verifica disponibilidade antes de aplicar. Atualizar o plugin nao troca
suas escolhas nem executa o instalador.

Para Git, publique o conteudo de executor-consultor-distribution como raiz de um
repositorio. O destinatario substitui o ponto por DONO/REPOSITORIO no primeiro
comando. Nenhum repositorio remoto foi criado automaticamente.

## Uso manual

Na pasta do plugin, apos confirmar disponibilidade dos modelos:

    python3 scripts/setup.py --dry-run
    python3 scripts/setup.py

O padrao e Sol medium e Astra medium. Conversas existentes podem conservar
o modelo selecionado. AGENTS.md gerado ou consultor existente exigem conciliacao
pela skill. Nao ha hooks adicionais nem perguntas por prompt.

## Remover e recuperar

    python3 scripts/setup.py --uninstall

Depois remova o plugin no Codex. Restauracao recusa sobrescrever edicoes posteriores.
O backup executor-consultor-state.json pode conter configuracoes privadas:
nao publique. Se houver interrupcao durante escrita, use esse backup para
conciliacao manual. Atualizacoes da politica exigem reexecutar a configuracao.

## Verificacao

Peca planejamento de mudanca de contrato publico e confira a chamada real ao
consultor. A politica orienta delegacao, mas nao e um bloqueio deterministico.
Compare qualidade e consumo reais; nao ha garantia de economia.
