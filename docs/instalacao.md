# Instalação pelo GitHub

O Personal Agent Team é distribuído como um marketplace Git, no mesmo formato
usado por plugins como o Ponytail. A instalação vale para o Codex CLI e para o
Codex App da mesma máquina.

## Requisitos

- Codex CLI instalado e autenticado.
- Git instalado.
- Acesso ao repositório. Se ele estiver privado, a conta local do GitHub precisa
  ter permissão de leitura.

## Instalar

Execute os dois comandos separadamente no terminal:

```sh
codex plugin marketplace add GersonDantas/agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

O primeiro registra o repositório como marketplace. O segundo instala o plugin
desse marketplace.

## Autorizar o hook

O plugin usa um hook `SessionStart` para carregar a política pessoal da equipe em
cada conversa e após compactações. Hooks instalados por plugins precisam ser
revisados antes da primeira execução.

Abra o Codex CLI:

```sh
codex
```

Dentro da interface do CLI, execute `/hooks`, localize **Loading personal agent
team**, revise o comando e marque o hook como confiável.

`/hooks` é um comando do Codex CLI. Ele não aparece no Codex App. A confiança
registrada pelo CLI é usada pelo Codex da mesma máquina.

## Primeira configuração no Codex App

Reinicie o Codex App após a instalação e abra uma conversa nova. Digite
`$configurar` e selecione **Personal Agent Team Codex: Configurar Equipe**.

Use **Configurar Modelos** somente quando a equipe já existir e você quiser
trocar os modelos do executor ou do consultor preservando os demais papéis,
níveis e limites.

A configuração é pessoal e fica fora dos repositórios de trabalho. O plugin
mostra uma prévia e pede aprovação antes de escrever os arquivos.

## Verificar

No terminal, confirme que o plugin está instalado e habilitado:

```sh
codex plugin list
```

Procure por:

```text
personal-agent-team-codex@agent-team-configurator  installed, enabled
```

Depois de configurar a equipe, abra outra conversa no Codex App. A nova conversa
deve carregar a política automaticamente. A configuração não deve adicionar nem
alterar `AGENTS.md` do usuário ou do projeto.

## Atualizar

Atualize a cópia do marketplace e reinstale o plugin:

```sh
codex plugin marketplace upgrade agent-team-configurator
codex plugin remove personal-agent-team-codex@agent-team-configurator
codex plugin add personal-agent-team-codex@agent-team-configurator
```

Se a definição do hook mudar, abra `/hooks` novamente no Codex CLI e revise a
nova versão. Inicie uma conversa nova após atualizar.

## Remover

Primeiro use **Configurar Equipe** para solicitar a remoção da configuração
pessoal. O configurador mostra uma prévia antes de restaurar arquivos e remover
o estado que pertence ao plugin.

Depois remova o plugin e, se não usar mais nenhum plugin desse marketplace,
remova também o marketplace:

```sh
codex plugin remove personal-agent-team-codex@agent-team-configurator
codex plugin marketplace remove agent-team-configurator
```

Remover somente o plugin não deve ser usado como substituto da remoção guiada da
configuração pessoal, porque backups e arquivos gerados ficam fora do cache do
plugin.

## Problemas comuns

### O marketplace não pode ser clonado

Confirme que o repositório existe e que sua conta possui acesso. Para distribuição
sem convite individual, o repositório precisa ser público.

### O plugin aparece, mas a política não carrega

Abra o Codex CLI, execute `/hooks` e confirme que **Loading personal agent team**
está confiável. Depois abra uma conversa nova.

### `/hooks` não aparece no App

Esse comando existe somente na interface do Codex CLI. Execute `codex` no
terminal e use `/hooks` dentro dela.
