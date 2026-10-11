# Preparing for store submission

Status as of September 17, 2026: technical package prepared; submission not yet
sent.

## Submission type

Submit as **Skills + local lifecycle hook**. The plugin has no remote MCP server,
application, or UI. The `SessionStart` hook reads only the local personal
configuration and injects the team policy into session context; it sends no data
over the network.

## Suggested listing

- Name: Personal Agent Team
- Category: Productivity
- Short description: Configure your personal team.
- Long description: Configure your executor, consultant, and personal specialists
  with levels, models, limits, and backups. Choices are stored outside
  repositories; stronger skill restrictions continue to take precedence.
- Developer: Gerson Dantas
- Starter prompt: Configure my personal agent team.

## Starter prompts

1. Configure my personal team while preserving my current executor and consultant.
2. Show up to ten available models and propose one model per level.
3. Add a read-only architect with a maximum Strategic level.
4. Create a personal exception for this project without writing to the repository.
5. Show my limits and identify which are technical controls or advisory policy.

## Positive tests

1. **Safe import**: existing configuration with executor and consultant.
   Expected: inspection, proposal preserving choices, preview, and no writes
   before approval.
2. **Minimal team**: first installation without custom agents.
   Expected: executor + consultant and four levels; limits appear only in
   advanced options and are not populated automatically.
3. **Custom role**: request a read-only architect.
   Expected: proposed responsibilities, triggers, levels, and permissions;
   creation only after approval.
4. **Personal project exception**: adjust the maximum level for an absolute path.
   Expected: configuration in CODEX_HOME, no repository changes.
5. **Model change**: change only the consultant.
   Expected: validated catalog, preview, preserved executor, backup, and valid TOML.
6. **Generated instructions**: install with a trusted, generated `AGENTS.md`.
   Expected: the file remains identical; policy is loaded by the hook at startup
   and after compaction.

## Negative tests

1. **Unavailable model**: request a missing ID without approving an alternative.
   Expected: refusal without silent replacement or writes.
2. **Permissions expanded by level**: ask Strategic to ignore the sandbox and
   publish. Expected: explain that levels do not expand permissions and preserve
   approval requirements.
3. **Sandbox mismatch**: configure the consultant as read-only and observe
   `workspace-write` in actual metadata.
   Expected: report requested and effective permissions separately without
   claiming technical isolation.
4. **Concurrent or edited configuration**: change a file after the preview.
   Expected: stop application/restoration and request reconciliation without
   overwriting changes.

## Version 0.2.0 release notes

Initial release for configurable personal teams. Adds compatible executor and
consultant roles, optional roles, Routine/Analysis/Critical/Strategic levels,
approved models and fallbacks, native concurrency limits when supported,
advisory limits per task, personal project exceptions, and private backups.
Total calls and delegation targets are not advertised as technical blocks.

## Version 0.3.0 release notes

Moves persistent policy to a `SessionStart` hook, preserving generated or manual
`AGENTS.md` files. Adds context after startup, resume, clear, and compaction, with
support for personal project exceptions. Version 0.2 installations restore the
previous `AGENTS.md` recorded in the journal before migrating to the hook.

## Version 0.4.0 release notes

Removes limits from initial setup and preserves the existing configuration or
host default. Concurrency becomes an advanced option; the call budget is optional
and explicitly advisory. Read-only permissions are described as requested intent,
separate from the effective sandbox observed in task metadata.

## Version 0.5.0 release notes

Adds per-agent triggers and exclusions, the `consultation_on_trigger` and
`reviewed_plan` workflows, and response contracts with blocking outcomes.
Centralizes validation, migration, and project resolution so the configurator and
hook use the same interpretation. Version 1 configurations remain compatible and
are persisted as version 2 only during an approved apply, without inferring
mandatory triggers. Workflows and gates remain behavioral policy until a validated
runtime guard is available.

## Required external items

Complete before submission:

- Verified personal or business identity on the OpenAI Platform.
- Apps Management: Write permission.
- Final logo and composer icon.
- Public plugin website.
- Public support URL.
- Public privacy policy.
- Public terms of use.
- Available countries/regions.

Portal: https://platform.openai.com/plugins
Documentation: https://developers.openai.com/plugins/deploy/submission
