<div align="center">

# Claw Research

**Bayesian-Powered Market Demand Research for Product Validation**

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+">
  </a>
  <a href="./tests/">
    <img src="https://img.shields.io/badge/Tests-57%20passed-brightgreen.svg" alt="Tests">
  </a>
</p>

[English](#overview) · [中文文档](./README.zh-CN.md)

*A standalone skill that transforms market signals into quantified success probabilities.*

</div>

---

## Overview

`claw-research` uses **Bayesian inference** to estimate success and payment probabilities from market signals.

Unlike gut-feeling validation or hardcoded scoring systems:

| Feature | Traditional Scoring | Claw Research |
|:-------:|:-------------------:|:-------------:|
| **Thresholds** | Hardcoded (>=5 = true) | Dynamic (0.0-1.0) |
| **Prior Probability** | Fixed (10%) | Context-aware estimation |
| **Transparency** | Black box | Full reasoning + evidence quotes |
| **Uncertainty** | Not tracked | Explicit missing evidence list |

### Key Benefits

- **Dynamic probability estimation** based on actual evidence context
- **Transparent reasoning** - see exactly why the probability is what it is
- **Evidence-backed assessments** - every score includes source quotes
- **Explicit uncertainties** - know what evidence is missing

---

## Bayesian Scoring Engine

```
P(success|evidence) = prior + sum(signal_strength x relevance)
P(payment|evidence) = prior + sum(signal_strength x relevance)
```

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
      "reasoning": "Users express strong emotional words with specific time loss",
      "evidence_quotes": ["Processing refunds takes 3 hours every day, it's crushing me"]
    }],
    "key_uncertainties": ["No decision-maker perspective validated"]
  }
}
```

---

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

1. Read `data/analysis_input.json`
2. Read `data/candidate_items.jsonl`
3. Write `data/analysis-result.json`
4. Sync the conclusion to Notion through MCP

---

## Use Cases

Use this skill when you need:

- **Data-driven go/no-go decisions** - Quantified probability instead of gut feeling
- **Transparent validation** - Stakeholders can see the reasoning
- **Evidence tracking** - Every assessment backed by source quotes
- **Uncertainty awareness** - Know what you don't know before building

---

## Workflow

```
+------------------------+
| External Market Items  |
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

---

## Repository Layout

```
claw-research/
├── SKILL.md                    # Skill definition
├── README.md                   # English docs
├── README.zh-CN.md             # Chinese docs
├── LICENSE
├── requirements.txt
│
├── config/
│   └── sources.json            # Data source configuration
│
├── data/
│   └── analysis-result.example.json
│
├── input/
│   └── example-items.jsonl     # Example input
│
├── references/
│   ├── analysis-result-schema.md
│   ├── input-config.md
│   ├── notion-mcp-sync.md
│   ├── notion-page-template.md
│   ├── output-spec.md
│   └── research-prompts.md
│
├── scripts/
│   ├── run_pipeline.py
│   └── collectors/              # Data collectors
│       ├── selector.py          # Smart source selector
│       ├── search_collector.py  # Multi-engine search
│       ├── rss_generic.py       # RSS feed collector
│       └── hacker_news.py       # HN API collector
│
└── tests/
    └── test_*.py
```

---

## Data Sources

| Source | Type | Auth Required | Best For |
|:------:|:----:|:-------------:|:---------|
| Hacker News | API | No | Tech discussions, startup feedback |
| Reddit | API | Yes | Community pain points |
| Bing | Search | No | General web search |
| Baidu | Search | No | Chinese content |
| Google | Search | No | Global results |
| DuckDuckGo | Search | No | Privacy-focused search |
| Woshipm | RSS | No | Chinese PM community |
| PMCAFF | RSS | No | Product management |
| TechCrunch | RSS | No | Tech news |
| 36Kr | RSS | No | Chinese tech/startup |

---

## Completion Rules

A run is **complete** when:

- [x] Candidate items prepared
- [x] `analysis_input.json` exists
- [x] `analysis-result.json` exists
- [x] Notion page created/updated (or explicitly noted as skipped)

---

## Validation

```bash
# Syntax check
python3 -m py_compile scripts/run_pipeline.py

# Run tests
python3 -m pytest tests/ -v

# Quick validation
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

---

## License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.
