---
name: configurar-modelos
description: Configura ou troca modelos do executor e consultor no Codex, com descoberta de modelos, backup e restauracao.
---

# Configurar modelos

Use Portuguese. Resolve the plugin root two levels above this skill directory.
Read Codex config and agents/consultor.toml, respecting CODEX_HOME.
Inspection alone does not authorize writes.

Discover models with codex debug models or authenticated App Server model/list.
Show at most ten visible models, current choices first, offering more if needed.
Do not rank by catalog order. Validate IDs and reasoning effort support.
Label cached catalogs as cached. Never silently replace an unavailable model.
Suggest Sol medium executor and Astra medium consultant for first setup;
preserve explicit user choices.

After selection, run scripts/setup.py --dry-run from this plugin with chosen
--executor, --consultor and --effort, then apply without --dry-run.
The script uses one effort for both roles. For different efforts, perform a
backed-up surgical edit and update the journal after value after validation.

Existing consultants or generated AGENTS.md require integration through existing
sources, not forced overwrite. Inspect the generator, back up and apply only
requested settings and policy; restoration then uses those backups. Avoid duplicate
policies. Preserve providers, credentials, proxy URLs, hooks and permissions.

Verify TOML and a real focused consultation when delegation is available.
Verify model/effort through execution metadata, never self-reported identity.
Report unavailable checks. Existing conversations may retain their model:
advise a new session or explicit selection.

For uninstall, run scripts/setup.py --uninstall before removing the plugin.
It refuses restoration when managed files changed afterward. Reconcile owned
changes in that case; never overwrite later edits. Backups are private.
