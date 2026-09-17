# Preparação para submissão à loja

Estado em 17/09/2026: pacote técnico preparado, submissão ainda não enviada.

## Modalidade

Enviar como **Skills only**. O plugin não possui MCP remoto, aplicativo ou UI.

## Ficha sugerida

- Nome: Personal Agent Team
- Categoria: Productivity
- Descrição curta: Configure sua equipe pessoal.
- Descrição longa: Configure executor, consultor e especialistas pessoais com
  níveis, modelos, limites e backups. As escolhas ficam fora dos repositórios;
  restrições mais fortes das skills continuam prevalecendo.
- Desenvolvedor: Gerson Dantas
- Prompt inicial: Configure minha equipe pessoal de agentes.

## Prompts iniciais

1. Configure minha equipe pessoal preservando meu executor e consultor atuais.
2. Mostre até dez modelos disponíveis e proponha um modelo por nível.
3. Adicione um arquiteto somente leitura com nível máximo Estratégico.
4. Crie uma exceção pessoal para este projeto sem escrever no repositório.
5. Mostre meus limites e diga quais são técnicos ou apenas orientativos.

## Testes positivos

1. **Importação segura**: configuração existente com executor e consultor.
   Esperado: leitura, proposta preservando escolhas, prévia e nenhuma escrita
   antes da aprovação.
2. **Equipe mínima**: primeira instalação sem agentes personalizados.
   Esperado: executor + consultor, quatro níveis e sugestões de limites.
3. **Papel personalizado**: pedir arquiteto somente leitura.
   Esperado: proposta de responsabilidades, acionamentos, níveis e permissões;
   criação apenas após aprovação.
4. **Exceção pessoal de projeto**: ajustar nível máximo para caminho absoluto.
   Esperado: configuração em CODEX_HOME, nenhuma alteração no repositório.
5. **Troca de modelo**: alterar somente o consultor.
   Esperado: catálogo validado, prévia, preservação do executor, backup e TOML válido.

## Testes negativos

1. **Modelo indisponível**: solicitar ID ausente e não aprovar alternativa.
   Esperado: recusa, sem substituição ou escrita silenciosa.
2. **Permissão ampliada pelo nível**: pedir que Estratégico ignore sandbox e publique.
   Esperado: explicar que nível não amplia permissões e manter aprovações.
3. **Configuração concorrente ou editada**: alterar arquivo após a prévia.
   Esperado: interromper aplicação/restauração e pedir conciliação, sem sobrescrever.

## Notas da versão 0.2.0

Versão inicial para equipe pessoal configurável. Adiciona executor e consultor
compatíveis, papéis opcionais, níveis Rotina/Análise/Crítico/Estratégico,
modelos e substitutos aprovados, limite nativo de concorrência quando suportado,
limite orientativo por tarefa, exceções pessoais por projeto e backup privado.
Total de chamadas e destinos de delegação não são anunciados como bloqueios técnicos.

## Itens externos obrigatórios

Preencher antes da submissão:

- Identidade pessoal ou empresarial verificada na OpenAI Platform.
- Permissão Apps Management: Write.
- Logo e ícone de compositor finais.
- Website público do plugin.
- URL pública de suporte.
- Política de privacidade pública.
- Termos de uso públicos.
- Países/regiões disponíveis.

Portal: https://platform.openai.com/plugins
Documentação: https://developers.openai.com/plugins/deploy/submission
