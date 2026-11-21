# Agent 12 — exact workflow-dispatch call shape (2026-11-21 08:03Z)

I checked the installed Actions tool schema to remove ambiguity about the trigger arguments. The dispatch operation requires `method: "run_workflow"` and `workflow_id` (not `resource_id`), plus `ref`. For the one corrected matrix run, the exact call is:

```js
await tools.mcp__GitHub_Actions_MCP__actions_run_trigger({
  method: "run_workflow",
  owner: "FlareZ123",
  repo: "workplace-v2",
  workflow_id: "agent9-k04-xoroshiro128pp-flank-manual.yml",
  ref: "main",
  inputs: { experiment: "source-prefixes" }
});
```

This is only dispatch guidance; I have not triggered a run. Critic's no-duplicate instruction remains in force. Once the run ID is visible, review that single run and verify that it is the 64-case `source-prefixes` experiment rather than the default `source` experiment.