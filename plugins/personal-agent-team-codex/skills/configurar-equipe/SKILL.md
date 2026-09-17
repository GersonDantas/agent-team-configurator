---
name: configurar-equipe
description: Configura a equipe pessoal de subagentes no Codex, incluindo papeis, niveis, modelos, substitutos, limites e excecoes pessoais por projeto. Use ao instalar, importar ou alterar a equipe.
---

# Configurar equipe

Converse em português. Resolva a raiz do plugin dois níveis acima desta skill.
Respeite `CODEX_HOME`; inspeção não autoriza escrita.

Leia a configuração atual, agentes pessoais e, quando existir, o estado legado
do Personal Agent Team. Descubra modelos com `codex debug models` ou `model/list`.
Mostre no máximo dez opções de cada vez, escolhas atuais primeiro. Não classifique
por ordem do catálogo, não invente custo/capacidade e identifique catálogo em cache.

Comece com executor e consultor. Ofereça, sem criar automaticamente: arquiteto,
revisor especializado, verificador independente, analista de merge, auditor
funcional e pesquisador de documentação. Para papel próprio, peça o objetivo e
proponha responsabilidades, acionamentos, exclusões, níveis e permissões. Comece
especialistas somente leitura. Somente o coordenador delega por padrão.

Use os níveis rotina, analise, critico e estrategico. Proponha modelos, esforços
e alternativas para aprovação. Nível não amplia permissões. Preserve limites mais
restritivos das skills e escolhas existentes. Não peça limites no fluxo inicial.
Preserve valores já configurados e ofereça, em opções avançadas, herdar o padrão
do host ou definir concorrência explicitamente. Ofereça orçamento de chamadas
somente como política orientativa opcional, sem bloqueio nativo garantido.

Trate `requested_read_only` como intenção de permissão, aceitando `read_only` como
alias legado. Nunca apresente essa intenção como isolamento confirmado. Mostre a
permissão efetiva como não verificada até conferir os metadados reais da thread.
Se o filho herdar `workspace-write`, informe a divergência. Quando a consulta
exigir isolamento técnico, oriente o usuário a selecionar Read Only na tarefa pai
antes da consulta e confirme novamente o sandbox efetivo do filho.

Mantenha configuração pessoal global. Exceções por projeto ficam no arquivo
pessoal usando caminho absoluto canônico, nunca no repositório. Mostre uma prévia
com papéis, níveis, modelos, permissões solicitadas, limites opcionais, arquivos e
garantias efetivamente disponíveis. Solicite
aprovação imediatamente antes de escrever.

Gere a especificação JSON em diretório temporário. A política da equipe é
carregada pelo hook `SessionStart` do plugin; não edite `AGENTS.md`. Na primeira
execução, informe que o usuário precisará abrir `codex` no terminal, executar
`/hooks` dentro do Codex CLI e revisar e confiar o hook. Explique que `/hooks`
não aparece no Codex App e que uma conversa nova deve ser aberta depois.
Execute primeiro:

`python3 scripts/team_config.py plan --spec <arquivo>`

Após aprovação, execute `apply` com o mesmo arquivo. Nunca substitua modelos
indisponíveis silenciosamente. O instalador cria backup privado e recusa agentes
preexistentes ou alterações posteriores. Instalações 0.2 que ainda gerenciem
`AGENTS.md` são migradas pelo script: a versão anterior do arquivo é restaurada
e a política passa ao hook.

Valide TOML/JSON e abra uma nova conversa. Quando delegação estiver disponível,
faça uma consulta focada e confira modelo, esforço e sandbox em metadados, não por
declaração do agente. Separe permissão solicitada de permissão efetiva. Informe os
testes indisponíveis. Não execute review, merge, publicação ou escrita externa para
testar configuração.

Para remover, mostre a prévia de `uninstall --dry-run`, peça aprovação e só então
execute `uninstall`. A restauração recusa sobrescrever mudanças posteriores.
