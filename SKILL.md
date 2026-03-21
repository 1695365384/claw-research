---
name: market-demand-research
description: Collect, normalize, filter, and dedupe market-demand candidate items, then prepare local research artifacts for OpenClaw to analyze. Use when OpenClaw already has posts, comments, or other market-signal items and needs a repeatable workflow to turn them into candidate sets, analysis inputs, reports, and downstream handoff artifacts.
---

# Market Demand Research

Use this skill when you want OpenClaw to run a standard demand-research workflow instead of doing ad hoc browsing.

This skill is designed for:
- indie hackers validating what to build next
- repeatable market scanning runs
- OpenClaw-driven research runs where the outer agent gathers candidate items first
- writing structured research results into local files you can version and inspect
- handing structured output to an external MCP-based sync step such as Notion MCP
- reducing time spent reading raw community posts

## What This Skill Does

The bundled script can:
- accept externally collected items from OpenClaw or another outer agent
- optionally support built-in public source collection for compatibility
- filter by your keyword sets
- dedupe repeated content using URL and content fingerprints
- prepare a stable candidate set for OpenClaw analysis
- write local reports and machine-readable analysis inputs

## Workflow Shape

This skill is a workflow, not a scheduler.

- It does not decide when to run
- It does not own cron, automation, or service orchestration
- It only defines how one research run is executed from input to output

External systems may call this workflow on any schedule they want.

## Workflow Diagram

```text
+-------------------+
| config.json       |
| - project_name    |
| - keywords        |
| - input mode      |
| - input path      |
+---------+---------+
          |
          v
+-------------------+
| receive input     |
| - items.jsonl     |
| - items.json      |
| - CLI override    |
+---------+---------+
          |
          v
+-------------------+
| filter items      |
| - include_any     |
| - exclude_any     |
| - lookback        |
+---------+---------+
          |
          v
+-------------------+
| dedupe items      |
| - seen urls       |
| - fingerprints    |
+---------+---------+
          |
          v
+-------------------+
| prepare analysis  |
| - candidate jsonl |
| - analysis brief  |
+---------+---------+
          |
          v
+-------------------+
| analyze with AI   |
| - OpenClaw agent  |
| - user-directed   |
+---------+---------+
          |
          v
+-------------------+
| write outputs     |
| - raw.jsonl       |
| - candidate jsonl |
| - analysis_input  |
| - run_metrics     |
| - reports/*.md    |
+---------+---------+
          |
          v
+-------------------+
| external layers   |
| - automation      |
| - Notion MCP      |
| - manual review   |
+-------------------+
```

## Standard Run Flow

1. Prepare an external item file. OpenClaw should gather candidate posts, comments, or snippets and write them to `input/items.jsonl` or another path.
2. Run the pipeline once locally to prepare candidate inputs.
3. Let OpenClaw read `data/analysis_input.json` and `data/candidate_items.jsonl`.
4. Ask OpenClaw to extract repeated pain points, scenarios, workarounds, payment signals, and candidate clusters, then write `data/analysis-result.json`.
5. Unless the user explicitly says not to, use Notion MCP to create or update a Notion page with the final conclusion in the standard layout from `references/notion-mcp-sync.md`.

## Completion Definition

A research run is only complete when all of these are true:

1. `data/candidate_items.jsonl` exists and contains the filtered candidate set
2. `data/analysis_input.json` exists
3. `data/analysis-result.json` exists and follows `references/analysis-result-schema.md`
4. If Notion MCP is available and the user did not opt out, a Notion page was created or updated using the standard layout
5. If Notion MCP is not available, the final response explicitly says: `本次未同步`

Do not treat the run as complete after candidate preparation alone.

## Quick Start

```bash
cd /path/to/openclaw-market-demand-research

python3 scripts/run_pipeline.py \
  --project-name "shopify-support-research" \
  --input-jsonl input/example-items.jsonl \
  --include-keyword "refund" \
  --include-keyword "chargeback" \
  --exclude-keyword "hiring"

# optional: use a JSON config file if you prefer
python3 scripts/run_pipeline.py --config /path/to/config.json
```

The script is idempotent at the item level. It stores state and skips duplicates it has already processed.

## Configuration Notes

- Keep topics narrow. Scan one persona or workflow per config file.
- Prefer concrete keywords like `shopify seller refund` over broad words like `AI tools`.
- Prefer one external input file per market or persona.
- The default interface is CLI-first. A config file is optional.
- `input.mode=external_file` is the default and preferred mode.
- `input.mode=builtin_sources` exists only as a compatibility fallback.
- The OpenClaw agent should handle all extraction, scoring, and clustering decisions after this workflow finishes.
- The default completion behavior is: prepare analysis -> write `data/analysis-result.json` -> sync a formatted conclusion page to Notion via MCP.
- Use the current runtime date and time for all real outputs. Do not reuse dates from examples or templates.

## Outputs

The script writes:
- raw fetch archives
- candidate item JSONL records
- an analysis input JSON for the outer agent
- a target location for OpenClaw to write `data/analysis-result.json`
- a persistent state file for dedupe
- a daily markdown report
- a weekly markdown report
- run metrics for each execution
See [references/research-prompts.md](references/research-prompts.md) for the recommended OpenClaw analysis prompts.
See [references/notion-mcp-sync.md](references/notion-mcp-sync.md) for the recommended MCP sync contract.
See [references/input-config.md](references/input-config.md) for the input configuration contract.
See [references/output-spec.md](references/output-spec.md) for the output file contract.
See [references/analysis-result-schema.md](references/analysis-result-schema.md) for the expected OpenClaw analysis output.

## Responsibility Split

This skill owns:
- normalization of externally supplied research items
- filtering
- dedupe
- local output generation for agent analysis

This skill does not own:
- source discovery strategy
- source crawling policy
- LLM configuration
- clustering decisions
- scoring decisions
- scheduling
- service supervision
- external app authentication
- Notion schema design beyond the standard page layout in `references/notion-mcp-sync.md`

## Limitations

- The quality of this workflow now depends on the quality of the external items fed into it.
- Public-source signal is only screening evidence. You still need user interviews before building.
