# Executor Consultor para Codex

Plugin para configurar um modelo executor para o trabalho cotidiano e um
consultor para decisões importantes, bloqueios e revisão de marcos.

Configuração inicial sugerida: **Sol medium** como executor e **Astra medium**
como consultor. As escolhas podem ser alteradas pela skill configurar-modelos.
A disponibilidade depende da conta e da versão do Codex.

## Requisitos

- Codex com suporte a plugins, agentes personalizados e delegação.
- Python 3.11 ou superior para o instalador.
- Acesso aos modelos escolhidos na sua conta.
- Para repositório privado, acesso concedido e autenticação Git no GitHub.

## Instalar

No terminal:

    codex plugin marketplace add GersonDantas/codex-executor-consultor
    codex plugin add executor-consultor@executor-consultor

Abra uma nova conversa e peça:

> Use a skill configurar-modelos do plugin executor-consultor para configurar
> meu executor e consultor. Sugira modelos disponíveis e mostre as escolhas.

A skill consulta o catálogo, apresenta até dez opções visíveis, valida o esforço
e aplica as escolhas com backup. A instalação do plugin por si só não altera
o modelo principal: essa configuração acontece no primeiro uso da skill.

Se o catálogo só estiver disponível em cache, a skill deve informar essa limitação.
Modelos indisponíveis não devem ser substituídos silenciosamente.

## Funcionamento diário

O executor consulta o consultor:

- Antes de mudanças arquiteturais ou de contrato público.
- Após duas tentativas substantivas sem resolver o mesmo bloqueio.
- Ao concluir um marco importante com evidências de validação.
- Quando você solicita explicitamente.

Uma alteração pequena também exige consulta quando muda um contrato público.
Perguntas simples normalmente não exigem delegação. O consultor analisa evidências,
sem editar arquivos nem delegar novamente. O executor avalia a resposta e continua.

A política é uma instrução ao agente, não uma garantia determinística.
O cliente precisa disponibilizar delegação. Quando não houver suporte, o agente
deve informar a limitação, nunca simular uma consulta.

## Arquivos criados ou alterados

O instalador respeita CODEX_HOME; por padrão usa ~/.codex.

| Arquivo | Finalidade |
| --- | --- |
| config.toml | Modelo e esforço padrão do executor |
| agents/consultor.toml | Modelo, esforço e instruções do consultor |
| AGENTS.md | Política de acionamento |
| executor-consultor-state.json | Backup e registro da instalação |

Configurações de provedores, endpoints, hooks e demais campos são preservadas.
Conversas existentes podem conservar o modelo escolhido na interface: abra uma
nova conversa ou selecione o executor desejado.

Se AGENTS.md for gerado ou já existir um consultor, o instalador recusa
sobrescrita. A skill precisa integrar a política na fonte existente e preservar
backups próprios. Essa integração manual não é revertida pelo desinstalador padrão.

## Trocar os modelos

Peça:

> Use configurar-modelos para trocar apenas o consultor. Mostre as opções
> disponíveis e preserve o executor.

O script básico usa o mesmo esforço para os dois papéis. Esforços diferentes
exigem uma alteração pontual pela skill, com atualização do registro e validação.

Para instalação manual, após verificar os modelos:

    cd plugins/executor-consultor
    python3 scripts/setup.py --dry-run
    python3 scripts/setup.py --executor gpt-5.6-sol --consultor gpt-6-astra --effort medium

## Testar

Em uma nova conversa com o executor selecionado:

> Planeje renomear um campo público customerId para accountId.
> Avalie compatibilidade e migração. Não implemente nada.

Confira uma chamada real de subagente e seu resultado. Para verificar identidade,
use metadados de execução, não apenas o modelo dizendo qual é seu nome.

Testes locais do instalador, sem alterar a configuração real:

    python3 plugins/executor-consultor/scripts/test_setup.py

Cobrem prévia, instalação, atualização, preservação, conflito com edição posterior,
desinstalação e proteção de arquivos gerados. Os testes usam diretório temporário.

## Atualizar

Obtenha a nova versão pelo gerenciamento de marketplaces/plugins da sua versão
do Codex. Atualizar o pacote não executa a configuração e não troca modelos.
Execute configurar-modelos para aplicar mudanças intencionais de configuração
ou de política. As escolhas atuais devem ser preservadas.

## Remover

Antes de remover o plugin, na pasta dele:

    python3 scripts/setup.py --uninstall

Depois:

    codex plugin remove executor-consultor@executor-consultor

Se um arquivo gerenciado mudou após a instalação, a restauração é interrompida
para preservar a edição. Concilie as alterações usando o backup. O instalador
registra o backup antes das escritas; se houver interrupção parcial, pode ser
necessária recuperação manual.

## Privacidade e limites

O pacote não contém configurações pessoais, credenciais ou backups do autor.
O registro local de instalação pode conter configurações privadas: não publique
executor-consultor-state.json. O instalador não envia dados à rede; a descoberta
de modelos e as consultas usam os serviços configurados no seu Codex.

Não há garantia de economia. Compare consumo real, tempo e qualidade em tarefas
equivalentes. Reconsultas excessivas podem aumentar o custo.

## Estrutura

    .agents/plugins/marketplace.json
    plugins/executor-consultor/
      .codex-plugin/plugin.json
      skills/configurar-modelos/SKILL.md
      templates/
      scripts/setup.py
      scripts/test_setup.py

Documentação oficial: https://learn.chatgpt.com/docs/agent-configuration/subagents
