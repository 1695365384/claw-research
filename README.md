# openclaw-market-demand-research

Market-demand research skill for OpenClaw and Codex.

[中文说明](./README.zh-CN.md)

## Overview

`openclaw-market-demand-research` is a standalone skill repository for repeatable market-demand research workflows.

It is designed for cases where an outer agent already has market-signal items such as posts, comments, complaints, issues, or clipped notes, and needs a reliable workflow to:

- normalize noisy inputs
- filter irrelevant items with keyword rules
- dedupe repeated evidence
- prepare machine-readable analysis inputs
- enforce required research outputs
- hand final conclusions to OpenClaw and Notion MCP

This repository maintains the skill itself only. It does not own scheduling, service orchestration, or LLM provider configuration.

## Use Cases

Use this skill when you need:

- repeatable market scans for a specific persona or workflow
- a local evidence package before doing product validation
- a stricter research workflow than ad hoc browsing
- a handoff contract between collection, analysis, and Notion sync

## Workflow

```text
+------------------------+
| external market items  |
| posts / comments / etc |
+-----------+------------+
            |
            v
+------------------------+
| run_pipeline.py        |
| normalize/filter/dedupe|
+-----------+------------+
            |
            v
+------------------------+
| local artifacts        |
| analysis_input.json    |
| candidate_items.jsonl  |
| reports/*.md           |
+-----------+------------+
            |
            v
+------------------------+
| OpenClaw analysis      |
| analysis-result.json   |
+-----------+------------+
            |
            v
+------------------------+
| Notion MCP sync        |
| create/update page     |
+------------------------+
```

## Repository Layout

```text
openclaw-market-demand-research/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── LICENSE
├── requirements.txt
├── data/
│   └── analysis-result.example.json
├── input/
│   └── example-items.jsonl
├── references/
│   ├── analysis-result-schema.md
│   ├── input-config.md
│   ├── notion-mcp-sync.md
│   ├── notion-page-template.md
│   ├── output-spec.md
│   └── research-prompts.md
├── scripts/
│   └── run_pipeline.py
└── tests/
    └── test_run_pipeline.py
```

## Inputs

Typical input is an externally prepared `items.jsonl` or `items.json` file. Each item represents one market signal.

See [references/input-config.md](/Users/limingwu/Documents/mvp/police/references/input-config.md).

## Outputs

The pipeline prepares:

- `data/raw.jsonl`
- `data/candidate_items.jsonl`
- `data/analysis_input.json`
- `data/run_metrics.json`
- `reports/*.md`

OpenClaw must then produce:

- `data/analysis-result.json`

See:

- [references/output-spec.md](/Users/limingwu/Documents/mvp/police/references/output-spec.md)
- [references/analysis-result-schema.md](/Users/limingwu/Documents/mvp/police/references/analysis-result-schema.md)

## Completion Rules

A run is only complete when:

1. candidate items have been prepared
2. `analysis_input.json` exists
3. `analysis-result.json` exists
4. if Notion MCP is available and the user did not opt out, a Notion page was created or updated
5. if Notion MCP is unavailable, the final response explicitly says `本次未同步`

## Quick Start

```bash
python3 scripts/run_pipeline.py \
  --project-name "cross-border-ecommerce-merchant-pain" \
  --input-jsonl input/example-items.jsonl \
  --include-keyword "refund" \
  --include-keyword "chargeback" \
  --exclude-keyword "hiring"
```

Then ask OpenClaw to:

1. read `data/analysis_input.json`
2. read `data/candidate_items.jsonl`
3. write `data/analysis-result.json`
4. sync the conclusion to Notion through MCP

## Validation

```bash
python3 -m py_compile scripts/run_pipeline.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 /Users/limingwu/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

## License

This project is licensed under the MIT License. See [LICENSE](/Users/limingwu/Documents/mvp/police/LICENSE).
