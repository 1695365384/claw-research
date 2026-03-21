# Prompt Design

The workflow now stops at candidate preparation. OpenClaw should read:

- `data/analysis_input.json`
- `data/candidate_items.jsonl`

Then run its own analysis.

Write the final structured result to:

- `data/analysis-result.json`

Use the current runtime UTC timestamp for `generated_at`. Do not copy dates from examples.

## Recommended Agent Tasks

Ask OpenClaw to produce:

- repeated pain points
- user scenarios
- current workarounds
- payment signals
- candidate clusters
- next interview targets

## Suggested Prompt

```text
Read data/analysis_input.json and data/candidate_items.jsonl.

Identify repeated pain points, scenarios, workarounds, and payment signals.
Group the candidate items into opportunity clusters.
Be strict about evidence quality and do not invent unsupported conclusions.

Return:
1. Top pain points
2. Candidate clusters
3. Payment signals
4. Most useful source examples
5. Next interview targets
6. Risks or evidence gaps

Write the answer as JSON following `references/analysis-result-schema.md`.
If Notion MCP is unavailable or the sync fails, state explicitly in the final reply: `本次未同步`.
```
