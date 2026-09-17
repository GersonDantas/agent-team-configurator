<!-- executor-consultor -->
## Personal agent team

For delegated work, read the personal configuration at
`~/.codex/executor-consultor/team.json` (respect `CODEX_HOME`). Choose the lowest
approved level sufficient for the task: rotina, analise, critico or estrategico.
Stay within the agent's maximum level and approved fallbacks. Announce the role,
level and reason briefly; summarize calls and substitutions at the end.

Only the coordinator delegates by default. Other agents may delegate solely when
their personal configuration permits the exact destination. Do not recursively
delegate without that permission. Treat `max_calls_per_task` and destination
rules as behavioral policy unless a validated runtime guard reports enforcement;
never claim a technical block without a real tool result. The native concurrent
thread limit applies only when supported by the active Codex host.

More restrictive skill rules prevail. Agent levels do not replace a skill's own
routing classes, approvals, independent verification, proof, parity, publication
or Git gates. Escalating analysis never expands write or external permissions.
Do not repeat a consultation without new evidence or a new decision.
<!-- /executor-consultor -->
