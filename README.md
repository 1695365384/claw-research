# claw-research

**Bayesian-powered market demand research for product validation.**

[中文说明](./README.zh-CN.md)

## Overview

`claw-research` is a standalone skill that uses **Bayesian inference** to estimate success and payment probabilities from market signals.

Unlike gut-feeling validation or hardcoded scoring systems, this skill provides:

- **Dynamic probability estimation** based on actual evidence context
- **Transparent reasoning** - see exactly why the probability is what it is
- **Evidence-backed assessments** - every score includes source quotes
- **Explicit uncertainties** - know what evidence is missing

## Core Feature: Bayesian Probability Scoring

```
P(成功|证据) = 先验概率 + Σ(信号强度 × 相关性)
P(支付|证据) = 先验概率 + Σ(信号强度 × 相关性)
```

### What Makes It Different

| Traditional Scoring | Claw Research |
|---------------------|---------------|
| Hardcoded thresholds (≥5 items = true) | Dynamic strength assessment (0.0-1.0) |
| Fixed prior probability (10%) | Context-aware prior estimation |
| Black box scores | Full reasoning with evidence quotes |
| No uncertainty tracking | Explicit list of missing evidence |

### Example Output

```json
{
  "success_probability": {
    "posterior": 0.32,
    "prior": {
      "value": 0.12,
      "reasoning": "B2B SaaS in this vertical has ~12% success rate"
    },
    "signal_assessments": [{
      "dimension": "pain_intensity",
      "strength": 0.75,
      "reasoning": "Users use strong emotional words with specific time loss",
      "evidence_quotes": ["Processing refunds takes 3 hours every day, it's crushing me"]
    }],
    "key_uncertainties": ["No decision-maker perspective validated"]
  }
}
```

## Use Cases

Use this skill when you need:

- **Data-driven go/no-go decisions** - Quantified probability instead of gut feeling
- **Transparent validation** - Stakeholders can see the reasoning
- **Evidence tracking** - Every assessment backed by source quotes
- **Uncertainty awareness** - Know what you don't know before building

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
claw-research/
├── SKILL.md                    # Skill definition
├── README.md                   # English docs
├── README.zh-CN.md             # Chinese docs
├── LICENSE
├── requirements.txt
├── .gitignore
├── data/
│   └── analysis-result.example.json  # Example output schema
├── input/
│   └── example-items.jsonl           # Example input
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

# Runtime workspace (not tracked in git)
workspace/
├── data/
│   ├── raw.jsonl
│   ├── candidate_items.jsonl
│   ├── analysis_input.json
│   ├── analysis-result.json
│   ├── run_metrics.json
│   └── state.json
├── input/
│   └── *.jsonl              # User input data
└── reports/
    └── *.md                 # Generated reports
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
