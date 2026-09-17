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
restritivos das skills e escolhas existentes. Sugira 3 threads concorrentes e 6
chamadas por tarefa, ambos editáveis; explique que apenas a concorrência possui
limite nativo quando o host o suporta. Total e destinos são orientativos até uma
guarda validada existir.

Mantenha configuração pessoal global. Exceções por projeto ficam no arquivo
pessoal usando caminho absoluto canônico, nunca no repositório. Mostre uma prévia
com papéis, níveis, modelos, permissões, limites, arquivos e garantias. Solicite
aprovação imediatamente antes de escrever.

Gere a especificação JSON em diretório temporário. A política da equipe é
carregada pelo hook `SessionStart` do plugin; não edite `AGENTS.md`. Na primeira
execução, informe que o usuário precisará revisar e confiar o hook em `/hooks`.
Execute primeiro:

`python3 scripts/team_config.py plan --spec <arquivo>`

Após aprovação, execute `apply` com o mesmo arquivo. Nunca substitua modelos
indisponíveis silenciosamente. O instalador cria backup privado e recusa agentes
preexistentes ou alterações posteriores. Instalações 0.2 que ainda gerenciem
`AGENTS.md` são migradas pelo script: a versão anterior do arquivo é restaurada
e a política passa ao hook.

Valide TOML/JSON e abra uma nova conversa. Quando delegação estiver disponível,
faça uma consulta focada e confira modelo/esforço em metadados, não por declaração
do agente. Informe os testes indisponíveis. Não execute review, merge, publicação
ou escrita externa para testar configuração.

Para remover, mostre a prévia de `uninstall --dry-run`, peça aprovação e só então
execute `uninstall`. A restauração recusa sobrescrever mudanças posteriores.
