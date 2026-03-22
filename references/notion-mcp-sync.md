# Notion MCP Sync Contract

Default behavior after a research run:

1. Produce `workspace/data/analysis-result.json`
2. Create or update one Notion page for the run
3. Use the standard page layout below unless the user explicitly asks for a different format
4. Use the current runtime date for the page title and any generated timestamps

This skill does not write to Notion directly at the script layer.

Instead, it emits:

- `workspace/reports/YYYY-MM-DD.md`
- `workspace/reports/weekly-YYYY-WW.md`
- `workspace/data/analysis_input.json`
- `workspace/data/analysis-result.json`

An external agent can read those local artifacts and sync them to Notion through Notion MCP.

## Recommended Notion Layout

Use one page per run or one database row per run. Store:

- project name
- generated time
- new item count
- top pain points
- candidate clusters
- run metrics

## Standard Page Layout

Write the page in this order:

1. A short callout with the top conclusion
2. A `Top Opportunity` section
3. A `Research Overview` section
4. A `Priority Matrix` section
5. A `Key Findings` section
6. A `Top Pain Points` section
7. A `Candidate Opportunities` section
8. A `Payment Signals` section
9. A `Strongest Examples` section
10. A `Next Interview Targets` section
11. A `Risks & Evidence Gaps` section
12. A `Recommended Next Steps` section

When possible:

- use short sections instead of long paragraphs
- use callouts for the top conclusion and the best product cut
- use a table for the priority matrix
- keep evidence links directly under the relevant pain point
- keep the page decision-oriented rather than source-dump oriented

## Recommended MCP Flow

1. Read the latest report and analysis inputs
2. Let OpenClaw produce `workspace/data/analysis-result.json`
3. Create or update a Notion page for the current run
4. Write:
   - a summary section
   - top pain points section
   - candidate clusters section
   - run metrics section
   - strongest evidence examples
5. Optionally link the local markdown report for deeper review

## Fallback Behavior

If Notion MCP is unavailable, unreachable, or fails:

1. Keep `workspace/data/analysis-result.json` as the source of truth
2. Do not silently skip the sync step
3. State explicitly in the final response: `SYNC_SKIPPED`
4. Briefly explain whether the issue was tool availability, permission, or write failure

## Naming Convention

Use a page title in this pattern unless the user asks otherwise:

- `{research topic} Research - YYYY-MM-DD`

Always substitute `YYYY-MM-DD` with the current local date at runtime. Do not copy dates from examples.

## Why This Split Exists

This keeps the research skill portable and easy to maintain:

- the skill owns research
- the MCP layer owns external-system writes
- changing Notion structure does not require changing the research pipeline
