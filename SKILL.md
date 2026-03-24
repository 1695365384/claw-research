---
name: claw-research
description: Hypothesis-driven market demand research with Bayesian probability scoring, strategic analysis frameworks, and action tracking. Use when you need data-driven decision support for product validation with professional research methodology.
---

# Claw Research

## 6-Stage Workflow

```text
+=============================================================================+
|                          CLAW RESEARCH WORKFLOW                              |
+=============================================================================+

+-------------------+     +-------------------+     +-------------------+
|  STAGE 1: CHARTER | --> |  STAGE 2: SOURCES | --> | STAGE 3: COLLECT  |
|  Define Charter    |     |  Read Sources     |     |  Collect Evidence |
+-------------------+     +-------------------+     +-------------------+
|                     |     |  [MANDATORY]      |     |                     |
| research-charter   |     | config/sources.json|     | collectors/        |
| - questions        |     | - hacker_news      |     | - api_collector    |
| - hypotheses       |     | - woshipm          |     | - rss_collector    |
| - personas         |     | - pmcaff           |     | - search_collector |
| - success_criteria |     | - reddit           |     |                     |
|                     |     | - techcrunch       |     |                     |
+-------------------+     +----------+--------+     +----------+--------+
                                   |                               |
                                   v                               v
                          +---------------------------+    +-------------------+
                          |  MUST READ THIS FILE      |    | raw.jsonl         |
                          |  config/sources.json      |    | candidate_items   |
                          +---------------------------+    +----------+--------+
                                                                    |
                                                                    v
+-------------------+     +-------------------+     +-------------------+
|  STAGE 6: ACTION  | <-- |  STAGE 5: OUTPUT  | <-- | STAGE 4: ANALYZE  |
|  Action & Knowledge|     |  Output Results   |     |  AI Analysis      |
+-------------------+     +-------------------+     +-------------------+
|                     |     |                     |     |                     |
| action-tracker     |     | analysis-result    |     | Bayesian scoring   |
| insight-library    |     | .json              |     | Hypothesis valid.  |
| Notion sync        |     |                     |     | SWOT analysis      |
|                     |     |                     |     | Competitor map     |
|                     |     |                     |     | User journey       |
+-------------------+     +-------------------+     +-------------------+


+=============================================================================+
|                          DATA FLOW (数据流详解)                               |
+=============================================================================+

+---------------------------+
|  config/sources.json      |  <=== [FIXED SOURCE] Must read from here
+---------------------------+
| type: api / rss / search  |
| enabled: true / false     |
| keywords: [...]           |
| requires_auth: bool       |
+------------+--------------+
             |
             v
+---------------------------+
|  scripts/collectors/      |  <=== Called by run_pipeline.py
+---------------------------+
| api_collector.py          |  --> Hacker News, Reddit
| rss_collector.py          |  --> woshipm, pmcaff, 36kr, techcrunch
| search_collector.py       |  --> Google, Bing, Baidu (TODO)
+------------+--------------+
             |
             v
+-------------------------------------------+
|  workspace/projects/{project_name}/data/  |
+-------------------------------------------+
| raw.jsonl                 |  --> Raw collected data
| candidate_items.jsonl     |  --> Filtered candidates
| analysis_input.json       |  --> AI input
+------------+------------------------------+
             |
             v
+---------------------------+
|  AI Analysis              |
+---------------------------+
| Bayesian scoring          |
| Hypothesis validation     |
| Strategic analysis        |
+------------+--------------+
             |
             v
+---------------------------+
|  Output                   |
+---------------------------+
| analysis-result.json      |
| Notion page (via MCP)     |
| action-tracker.json       |
+---------------------------+
```

---

## Execution Steps

### Step 1: Read Charter (Optional)
Read `workspace/projects/{project_name}/config/research-charter.json` if exists:
```json
{
  "project_id": "string",
  "research_questions": [{ "id": "RQ1", "question": "...", "hypothesis": "..." }],
  "target_personas": [...],
  "success_criteria": {...}
}
```

### Step 2: Read Sources [MANDATORY]
Read `config/sources.json` to get available data sources:
```json
{
  "sources": {
    "source_name": {
      "type": "api | rss | search",
      "url": "...",
      "enabled": true,
      "keywords": [...]
    }
  }
}
```

### Step 3: Collect Evidence via Collectors
Call collectors from `scripts/collectors/` based on source type:

| Source Type | Collector | Example Sources |
|-------------|-----------|-----------------|
| `api` | `HackerNewsCollector` | hacker_news |
| `rss` | `RSSCollector` | woshipm, pmcaff, techcrunch, 36kr |
| `search` | `SearchCollector` | google, bing, baidu |

```bash
# Run pipeline - ALWAYS uses config/sources.json
python3 scripts/run_pipeline.py \
  --project-name "project-name" \
  --sources "hacker_news,woshipm,pmcaff" \
  --query "product pain points"
```

### Step 4: AI Analysis
Read from `workspace/projects/{project_name}/data/`:
- `analysis_input.json`
- `candidate_items.jsonl`

Generate `analysis-result.json`:
- Bayesian scoring (P(success|evidence), P(payment|evidence))
- Hypothesis validation (validate or refute each hypothesis)
- Strategic analysis (SWOT, competitors, user journey)
- Action items with validation criteria

### Step 5: Output Results
Write to `workspace/projects/{project_name}/data/analysis-result.json` following `references/analysis-result-schema.md`.

### Step 6: Sync & Track
- Sync to Notion (if MCP available) following `references/notion-page-template.md`
- Update action tracker: `python3 scripts/manage_actions.py --project {name} --add "..."`

---

## Completion Checklist

All paths relative to `workspace/projects/{project_name}/`:
- [ ] `data/candidate_items.jsonl` exists
- [ ] `data/analysis_input.json` exists
- [ ] `data/analysis-result.json` exists with complete analysis
- [ ] Full report presented to user
- [ ] Evidence quotes with source URLs included
- [ ] Bayesian calculation shown
- [ ] Notion synced (or `SYNC_SKIPPED` with reason)

---

## File Structure

```
workspace/projects/{project_name}/
├── config/
│   └── research-charter.json
├── data/
│   ├── raw.jsonl
│   ├── candidate_items.jsonl
│   ├── analysis_input.json
│   ├── analysis-result.json
│   └── action-tracker.json
└── reports/
    └── *.md

config/
├── sources.json          # [FIXED] Data sources config
└── keys.json             # API keys (gitignored)
```

---

## References

- `references/research-prompts.md` - AI analysis instructions
- `references/analysis-result-schema.md` - Output JSON schema
- `references/notion-page-template.md` - Report template
