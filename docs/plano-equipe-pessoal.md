# Plano técnico: equipe pessoal configurável

Data: 17/09/2026. Estado: base implementada; controles rígidos de orçamento e
telemetria continuam planejados.

## 1. Resultado esperado e decisões aprovadas

Evoluir o configurador atual para configurar uma equipe pessoal por conversa,
sem obrigar o usuário a repetir instruções de roteamento em cada prompt.
Preservar o nome técnico do plugin nesta etapa para evitar uma migração extra.

- Codex primeiro; definições independentes da integração para futuras plataformas.
- Configuração pessoal global e exceções pessoais por projeto, fora dos repositórios.
- Executor/coordenador e consultor inicialmente; especialistas e papéis próprios opcionais.
- Níveis dinâmicos: Rotina, Análise, Crítico e Estratégico. Não são uma escala científica.
- Sugestão de modelo e esforço por nível, aprovada pelo usuário; exceções por agente.
- Escalada automática dentro do intervalo aprovado, com justificativa; acima, autorização.
- Alternativas previamente aprovadas quando um modelo estiver indisponível, com aviso.
- Restrições das skills prevalecem; exceções explícitas não removem gates de segurança.
- Somente o coordenador delega por padrão. Delegação entre agentes é opt-in, com
  destinatários e profundidade limitados.
- Limites opcionais e editáveis: sugestão de 3 subagentes simultâneos e 6 chamadas
  por tarefa, considerando a cadeia inteira. Permitir exceções pessoais por projeto.
- Avisos curtos e resumo final; registro pessoal mínimo, sem prompts/código completos.
- Importar a configuração existente; prévia, aprovação e backup antes de aplicar.
- Skill conversacional como interface inicial; arquivo legível para edição avançada.

## 2. Evidência e limites da pesquisa

Inspeção local: CLI 0.147.0; plugin 0.1.0; árvore Git limpa antes desta documentação.
O configurador administra a configuração nativa, agentes, equipe declarativa e
um journal. A política é injetada por `SessionStart`, sem editar `AGENTS.md`.
Ainda não há orçamento rígido de chamadas ou roteador externo.
O comando local de ajuda confirma a existência de `codex debug models`.

A documentação oficial descreve agentes pessoais em `~/.codex/agents/*.toml`,
com nome, descrição, instruções e opções como modelo, esforço e sandbox. Também
documenta `agents.max_concurrent_threads_per_session`, excluindo o agente principal,
e `agents.max_threads` como alias legado. São limites de threads abertas, não
uma contagem de chamadas nem necessariamente de agentes executando naquele instante.
[Fonte: subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Hooks podem interceptar ferramentas compatíveis antes da execução. Porém,
`SubagentStart` não impede o início por `continue: false`; `PreToolUse` não oferece
`permissionDecision: ask` funcional. Assim, não usar esses campos para prometer
aprovação ou bloqueio. Precisamos provar cobertura das ferramentas de delegação
reais antes de construir um contador preventivo.
[Fonte: hooks](https://learn.chatgpt.com/docs/hooks).

Documentação online e cliente instalado podem divergir. A página de referência
consultada não apresentou a mesma chave de simultaneidade na busca textual.
Validar o esquema e o comportamento do host antes de gerar opções.
[Referência de configuração](https://learn.chatgpt.com/docs/config-file/config-reference).

Esta análise não executou delegações, testes de bloqueio ou testes no App. CLI
instalado não comprova a versão do runtime utilizado pelo aplicativo.

## 3. Matriz de viabilidade

| Recurso | Caminho proposto | Condição de entrega |
| --- | --- | --- |
| Papéis, modelo e esforço | Arquivos nativos e parâmetros de delegação suportados | Confirmar por metadados reais |
| Escolha dinâmica de nível | Política do coordenador + resolvedor determinístico de opções aprovadas | Classificação semântica continua sendo decisão do modelo |
| Limite simultâneo | Cap nativo de threads abertas, quando suportado | Testar contagem, liberação e filhos aninhados |
| Total por tarefa | Contador local antes da chamada, se interceptação for comprovada | Não anunciar como limite rígido sem cobertura total |
| Quem pode delegar e profundidade | Restrições nativas disponíveis + guarda validada | Não presumir chave de profundidade nem suporte por papel |
| Somente leitura | Sandbox e restrição das ferramentas disponíveis | Sandbox de arquivos sozinho não bloqueia escrita em serviços externos |
| Exceções pessoais por projeto | Resolução local pelo diretório canônico | Não reescrever config global ao alternar projetos |
| Avisos e eventos | Política concisa + registro de eventos observados | Separar configuração solicitada de execução comprovada |

Se a interceptação não for confiável, oferecer modo orientativo apenas com
consentimento informado. Não reduzir silenciosamente garantias aprovadas.
Um runtime próprio de orquestração seria expansão de escopo, não fallback automático.

## 4. Arquitetura mínima proposta

Manter Python 3.11+ e biblioteca padrão para validação e instalação. Não adicionar
servidor MCP, serviço residente ou interface gráfica inicialmente.

Quatro componentes:

1. Skill `configurar-equipe`: entrevista, descoberta, proposta e aprovação.
   Manter `configurar-modelos` como entrada compatível, sem instruções divergentes.
2. Configuração declarativa versionada: fonte pessoal das escolhas.
3. Resolvedor: combina padrão, projeto, papel, nível, restrições e disponibilidade.
4. Adaptador Codex: gera somente opções suportadas; identifica capacidades e
   nível de garantia. Guarda/registro apenas após o teste de viabilidade.

Local adotado: `$CODEX_HOME/personal-agent-team-codex/`, padrão `~/.codex/personal-agent-team-codex/`.
Usar `team.toml` para escolhas, `projects/` para ajustes pessoais, `state/` para
eventos/contadores e `backups/` para recuperação. Diretórios privados e arquivos
sensíveis com permissões restritas; não incluir esses dados no pacote distribuído.

Projeto identificado por caminho canônico aprovado. Worktrees podem compartilhar
um perfil mediante associação explícita. Não usar somente nome de pasta, URL de
remote ou instruções do repositório para selecionar configurações pessoais.

Não trocar arquivos globais a cada tarefa: duas conversas de projetos diferentes
devem poder rodar simultaneamente sem uma alterar o modelo da outra.
Resolver parâmetros por chamada quando suportado; perfis nativos gerados por
combinação habilitada são alternativa a validar, sem gerar todo produto cartesiano.
Não prometer troca do modelo principal em uma conversa já aberta.

## 5. Contrato dos dados

| Grupo | Campos conceituais |
| --- | --- |
| Identidade | Versão do esquema, revisão da configuração |
| Níveis | ID estável, modelo, esforço, alternativas aprovadas |
| Agente | ID, nome, objetivo, instruções, acionamentos e exclusões |
| Roteamento | Nível padrão, níveis permitidos, máximo, exceções modelo/esforço |
| Permissões | Leitura/escrita, ferramentas permitidas, aprovações preservadas |
| Delegação | Habilitada, destinos permitidos, profundidade máxima |
| Limites | Simultâneos, total por tarefa, opção explícita de desabilitar limite |
| Projeto | Identificador local, campos substituídos, revisão aprovada |
| Capacidades | Recursos detectados, host/versão, data e testes realizados |

Nível, modelo e esforço são independentes. Não interpretar tamanho de modelo como
número de parâmetros ou deduzir preço/capacidade pela ordem do catálogo. Mostrar
até dez modelos por página e permitir ver todos. Ausência de dados confiáveis
exige escolha humana; catálogo em cache deve aparecer como tal.

Modelos novos não substituem os atuais automaticamente. Validar combinação de
modelo/esforço e alternativas; nunca promover permissões junto com o nível.

## 6. Catálogo inicial e compatibilidade

| Papel sugerido | Uso | Cuidados |
| --- | --- | --- |
| Executor/coordenador | Condução e integração | É o agente principal, não criar cópia por tarefa |
| Consultor | Bloqueios, planos e marcos relevantes | Consulta focada; sem repetição sem evidência nova |
| Arquiteto | Estrutura, contratos e migrações | Sobreposição com consultor exige pergunta distinta |
| Revisor especializado | Segurança, dados, concorrência ou testes | Recebe apenas recorte relevante |
| Verificador independente | Confirmação de achados | Contexto novo e projeção cega |
| Analista de merge | Estudo das duas linhas de mudanças | Somente leitura; isolamento conforme skill |
| Auditor funcional | Fluxos após integração | Não substitui testes de paridade |
| Pesquisador de documentação | Contratos de APIs e versões | Opcional; fontes primárias |

Papéis sugeridos não significam criação/execução automática de todos os agentes.
Criar papel próprio por descrição e proposta aprovada. Especialistas começam
somente leitura; permissões de escrita precisam de autorização separada.

Para workflows especializados de revisão e integração, preservar as classificações econômicas existentes,
os tetos dos agentes comuns, a exceção do consultor e os procedimentos obrigatórios.
Não mapear Critical/DEEP automaticamente para um modelo mais caro. Os quatro níveis
do plugin não substituem as classificações internas das skills.
Conflitos sem opção compatível devem ser explicitados, não resolvidos relaxando limites.

Consultor usado como verificador precisa de instância independente, contexto cego
e esquema exigido pela skill. Consulta de arquitetura não conta como auditoria
funcional. Triagem humana, provas, paridade e autorizações Git/publicação permanecem.
Não editar skills de terceiros durante instalação sem aprovação específica.

## 7. Ciclo de execução e orçamento

Proposta de definição operacional: tarefa é um objetivo explícito com identificador
local, persistido entre turnos até conclusão/cancelamento. Nova mensagem, compactação
ou reinício não zeram o orçamento. Objetivo novo precisa ser identificado como tal.

1. Resolver perfil pessoal e restrições aplicáveis; não abrir configurador a cada prompt.
2. Decidir se delegar é necessário; trabalho simples pode ficar no executor.
3. Classificar nível e selecionar apenas combinações aprovadas e compatíveis.
4. Conferir autorização, independência, destinos, profundidade e orçamento.
5. Reservar chamada de modo atômico, anunciar brevemente e executar.
6. Registrar resultado observado, reconciliar reserva e atualizar resumo.

Uma chamada é uma nova atribuição de trabalho a subagente: spawn ou continuação
que inicia trabalho adicional. Polling/wait não conta. Filhos e retries que iniciam
execução contam; falha confirmada antes de iniciar libera reserva. Resultado incerto
mantém reserva até conciliação, sem retry cego. Essa semântica precisa ser documentada.

Usar transação local (por exemplo SQLite da biblioteca padrão) se a guarda for viável.
Testar corridas, duplicatas, interrupções e recuperação. Limite de threads abertas
e limite de chamadas são diferentes; agente finalizado pode ainda precisar ser
fechado para liberar slot nativo. Não contar SubagentStop como fechamento sem prova.

Acima do limite: negar a nova delegação e solicitar decisão ao usuário pelo
coordenador. Não simular uma aprovação por hook. Uma concessão temporária deve ser
limitada à tarefa e registrada, sem aumentar permanentemente o padrão.

Registro mínimo: horário, tarefa, pai/filho, papel, nível, motivo resumido,
modelo/esforço solicitado e observado, substituição, estado e garantia disponível.
Não registrar raciocínio interno, prompts, código, credenciais ou payloads de tools.
Propor retenção de 30 dias, editável, sujeita à aprovação inicial. Não chamar
contagem de agentes ou RTK gain de economia financeira comprovada.

## 8. Migração segura

1. Inspecionar arquivos e symlinks existentes sem executar configuração.
2. Importar executor, consultor e escolhas atuais. Não alterar modelos pela sugestão.
3. Mostrar diff, arquivos atingidos, limitações e permissões para aprovação.
4. Gerar em staging, validar, criar backup privado e journal de recuperação.
5. Aplicar arquivos individualmente de forma atômica, com recuperação para interrupção
   entre arquivos; não chamar conjunto de operações de transação atômica completa.
6. Verificar hashes e estado. Reexecução idempotente, sem duplicar política.

Preservar providers, endpoints, hooks RTK, credenciais, ferramentas e permissões.
Não editar `AGENTS.md`: a política persistente vem do hook `SessionStart` do plugin.
Não depender de importação com `@`. O hook precisa ser revisado e confiado pelo
usuário e deve reaplicar contexto após compactação.

O journal 0.1.0 guarda snapshots integrais. Migração deve preservar sua recuperação
e passar a registrar propriedade das mudanças, sem sobrescrever edições posteriores.
Colisões de nomes, configurações manuais e mudanças externas exigem conciliação.
Desinstalação remove/reverte apenas itens administrados e preserva conteúdo alheio.

## 9. Etapas e critérios de aceite

| Etapa | Entrega | Verificação |
| --- | --- | --- |
| 0. Viabilidade | Matriz por host CLI/App e estratégia de controle | Host isolado, limites, aninhamento, hooks e metadados |
| 1. Dados | Esquema versionado e resolvedor puro | Entradas inválidas, precedência, alternativas e ciclos |
| 2. Interface | Skill e catálogo opcional | Fluxos criar/editar/desativar, prévia, sem escrita antes de aprovação |
| 3. Instalação | Importação e geração compatível | Temp home, idempotência, interrupção, symlinks, rollback |
| 4. Controles | Guarda comprovada ou limitação explicitamente aprovada | Corrida de chamadas, retries, reinício, filhos e bypasses |
| 5. Integração | Exemplos review/merge | Economia, verificação cega, paridade e gates preservados |
| 6. Distribuição | Documentação e pacote | Validadores de skill/plugin e instalação limpa |

Teste negativo obrigatório: duas chamadas simultâneas disputando a última vaga;
delegação para destino não permitido; modelo indisponível; esforço inválido; limite
atingido após compactação; dois projetos em paralelo; custom role com nome colidente;
ferramenta externa de escrita em perfil somente leitura; fonte AGENTS.md gerada.

Critério final: usuário configura uma vez, nova sessão usa a política sem prompt
especial, execução comprova modelos/esforços, migração preserva configurações e
todo controle é marcado como nativo, validado pelo plugin ou apenas orientativo.

Não executar merge/review real, publicar, alterar instalação pessoal ou realizar
chamadas pagas para validação sem autorização correspondente. Primeiro implementar
e testar em diretórios temporários. Publicação e migração pessoal são passos separados.

## 10. Próxima ação recomendada

Começar pela etapa 0 e pelo resolvedor puro. Não reescrever o instalador inteiro
antes de descobrir se o runtime permite impor os limites aprovados. Se não permitir,
apresentar a limitação e obter decisão sobre modo orientativo ou escopo adicional.
