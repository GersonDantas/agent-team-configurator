---
name: configurar-modelos
description: Configura ou troca modelos do executor e consultor no Codex, com descoberta de modelos, backup e restauracao.
---

# Configurar modelos

Esta entrada permanece por compatibilidade. Para configurar equipe, papeis,
niveis, limites ou projetos, use `configurar-equipe`. Para trocar somente os
modelos existentes, aplique o mesmo fluxo seguro de `configurar-equipe`, sem
editar manualmente o journal.

Use Portuguese. Resolve the plugin root two levels above this skill directory.
Read Codex config and agents/consultor.toml, respecting CODEX_HOME.
Inspection alone does not authorize writes.

Discover models with codex debug models or authenticated App Server model/list.
Show at most ten visible models, current choices first, offering more if needed.
Do not rank by catalog order. Validate IDs and reasoning effort support.
Label cached catalogs as cached. Never silently replace an unavailable model.
Suggest Sol medium executor and Astra medium consultant for first setup;
preserve explicit user choices.

After selection, generate an approved team specification and run
`scripts/team_config.py plan --spec <file>`, then use `apply` only after approval.
Do not edit the journal manually. Keep `setup.py` only for legacy uninstall recovery.

Existing consultants or generated AGENTS.md require integration through existing
sources, not forced overwrite. Inspect the generator, back up and apply only
requested settings and policy; restoration then uses those backups. Avoid duplicate
policies. Preserve providers, credentials, proxy URLs, hooks and permissions.

Verify TOML and a real focused consultation when delegation is available.
Verify model/effort through execution metadata, never self-reported identity.
Report unavailable checks. Existing conversations may retain their model:
advise a new session or explicit selection.

For version 0.2 installations, preview and run `team_config.py uninstall`. For a
legacy 0.1 journal, use `setup.py --uninstall` before migration. Both refuse to
overwrite later edits. Reconcile owned changes manually. Backups are private.
