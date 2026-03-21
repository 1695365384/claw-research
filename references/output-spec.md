# Output File Contract

Each run writes a stable set of local artifacts.

## Output Files

- `data/raw.jsonl`
  Raw normalized items from the current and previous runs.

- `data/candidate_items.jsonl`
  Filtered and deduped items prepared for OpenClaw analysis.

- `data/analysis_input.json`
  Machine-readable brief for the outer agent.

- `data/analysis-result.json`
  Final structured analysis written by OpenClaw after reviewing the candidate set.

- `data/state.json`
  Dedupe state and last run timestamp.

- `data/run_metrics.json`
  Metrics for the most recent run.

- `reports/YYYY-MM-DD.md`
  Daily report for the current run.

- `reports/weekly-YYYY-WW.md`
  Weekly rollup based on recent enriched items.

## Key Payloads

### `run_metrics.json`

Contains:

- source stats
- filter stats
- new item count

### `analysis_input.json`

Contains:

- run summary
- source stats
- filter stats
- top titles to review
- item count

This file is intentionally optimized for the outer agent so it does not need to infer workflow context from the raw candidate set.

### `analysis-result.json`

Contains:

- top pain points
- candidate clusters
- payment signals
- strongest evidence examples
- next interview targets
- risks or evidence gaps

This file is the handoff artifact for downstream review and Notion MCP sync.
