---
name: claw-research
description: Hypothesis-driven market demand research with Bayesian probability scoring and strategic analysis. Use for product validation with professional research methodology.
---

# Claw Research - Core Prompt

## ⛔ BLOCKER Rules (Must Pass)

**Violation = Invalid Output - Must Redo**

| # | Rule | Check |
|---|------|-------|
| 1 | Read sources from `config/sources.json` only | No hardcoded paths |
| 2 | Every evidence: `full_text` + `source_url` + `source_type` + `published_at` | 4 fields required |
| 3 | Output `analysis-result.json` with valid JSON | Schema compliant |
| 4 | Present **full Markdown report** to user | No "see file" shortcuts |
| 5 | No truncated evidence text | Complete quotes |
| 6 | No placeholder text | No "TBD" or "..." |

---

## 7-Stage Workflow

```
CHARTER → SOURCES → COLLECT → ANALYZE → MD_REPORT → NOTION → ACTION
 (opt)   [BLOCKER]   auto     AI core   [BLOCKER]  from MD   track
```

**Core Principle**: Markdown report is the "Single Source of Truth" (SSOT). Notion sync MUST read from MD file.

---

### Stage 1: Charter (Optional)

Read `workspace/projects/{project}/config/research-charter.json` if exists.

---

### Stage 2: Sources [BLOCKER]

**Run pipeline to collect data:**
```bash
python3 scripts/run_pipeline.py \
  --project-name "my-research" \
  --sources "hacker_news,woshipm,pmcaff" \
  --query "product pain points"
```

**Key Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--project-name` | Unique project identifier | Required |
| `--sources` | Comma-separated sources | All enabled |
| `--query` | Search query | From charter |
| `--lookback-hours` | Time window | 720 (30 days) |
| `--max-items-per-source` | Items per source | 50 |
| `--include-keyword` | Filter: must contain | None |
| `--exclude-keyword` | Filter: must not contain | None |

**Output:** `workspace/projects/{project}/data/candidate_items.jsonl`

---

### Stage 3: Collect (Automatic)

Collectors output to `workspace/projects/{project}/data/`:
- `raw.jsonl` - Raw data
- `candidate_items.jsonl` - Filtered items

---

### Stage 4: Analyze (AI Core)

Read from `data/`:
- `analysis_input.json`
- `candidate_items.jsonl`
- `research-charter.json` (if exists)

**AI Performs:**
1. Pain point analysis
2. Payment signal detection
3. Bayesian probability scoring
4. Hypothesis validation (if charter)
5. Strategic analysis (SWOT, competitors, journey)

---

### Stage 5: MD Report [BLOCKER]

**Must generate Markdown file first as the single source for Notion sync.**

1. **Write JSON**: `workspace/projects/{project}/data/analysis-result.json`
2. **Write Markdown**: `workspace/projects/{project}/reports/analysis-report-{YYYY-MM-DD}.md`
3. **Present to user**: Display full report in conversation

**Markdown File Path:**
```
workspace/projects/{project}/reports/analysis-report-{date}.md
```

**⚠️ Important**: This MD file is the ONLY data source for Notion sync. Must contain complete content.

---

### Stage 6: Notion Sync (From MD File)

**Read content from Markdown file to sync to Notion, ensuring consistency.**

```
┌─────────────────────────────────────────────────────────┐
│  analysis-report-{date}.md  ──────►  Notion Page        │
│  (Single Source of Truth)         (Read from MD file)   │
└─────────────────────────────────────────────────────────┘
```

**Sync Process:**
1. Read complete content from `reports/analysis-report-{date}.md`
2. Parse Markdown structure (headings, tables, blockquotes, etc.)
3. Convert to Notion API format (callout, to_do, divider, etc.)
4. Create/Update Notion page

**⚠️ Prohibited:**
- ❌ Do NOT regenerate Notion content from analysis-result.json
- ❌ Do NOT skip MD file and sync directly
- ❌ Do NOT simplify or truncate content from MD file

**Notion Sync Status:**
```markdown
## Notion Sync Status
- [x] Synced: https://notion.so/page-id
- [ ] SYNC_SKIPPED: [reason - e.g., "Notion MCP not configured"]
```

---

### Stage 7: Action (Track)

**Manage action items:**
```bash
# List pending actions
python3 scripts/manage_actions.py --project "my-research" --list-pending

# Add new action
python3 scripts/manage_actions.py --project "my-research" \
  --add "Interview 5 target users" \
  --due "2026-04-15" \
  --insight "High-volume sellers show strongest pain"

# Complete action
python3 scripts/manage_actions.py --project "my-research" \
  --complete "ACTION-001" \
  --note "Completed 5 interviews, 3 confirmed willingness to pay"
```

---

## Output Format

### JSON Structure (Write to `analysis-result.json`)

```json
{
  "generated_at": "UTC timestamp",
  "project_name": "string",
  "top_pain_points": [{ "label", "summary", "evidence_count", "example_urls" }],
  "candidate_clusters": [{ "name", "summary", "evidence_count", "payment_signal" }],
  "payment_signals": [{ "label", "summary" }],
  "bayesian_scores": {
    "success_probability": {
      "posterior": 0.35,
      "prior": { "value": 0.12, "reasoning": "string" },
      "confidence": "high|medium|low",
      "signal_assessments": [{ "dimension", "strength", "reasoning", "evidence_quotes", "contribution" }],
      "calculation_summary": "string",
      "key_uncertainties": ["string"]
    },
    "payment_probability": { /* same structure */ }
  },
  "hypothesis_validation": [{ "hypothesis_id", "status", "supporting_evidence", "missing_evidence" }],
  "strategic_analysis": {
    "swot": { "strengths", "weaknesses", "opportunities", "threats" },
    "competitor_landscape": [{ "name", "gap", "our_advantage" }],
    "user_journey_stages": [{ "stage", "pain_level", "evidence_count" }]
  },
  "actionable_insights": [{ "insight", "evidence_basis", "recommended_action", "priority" }],
  "action_items": [{ "id", "action", "owner", "status" }],
  "strongest_examples": [{ "title", "url", "reason" }],
  "risks_or_gaps": ["string"]
}
```

### Markdown Report (Present to User)

```markdown
# [Project] Market Research Report
**Generated**: YYYY-MM-DD | **Confidence**: high/medium/low

## Executive Summary
**Conclusion**: [One sentence]
**Actions**: 1. [P0] ... 2. [P1] ... 3. [P2] ...
**Risks**: [Top 2 risks]

## Bayesian Scores
| Probability | Prior | Posterior | Key Signals |
|-------------|-------|-----------|-------------|
| Success | 12% | 35% | pain_intensity +10% |
| Payment | 6% | 18% | economic_impact +8% |

## Top Pain Points
### Pain 1: [Title] (X evidence)
> **Original**: "[Full quote]"
> **Source**: [Name](URL) | **Type**: community_discussion | **Date**: YYYY-MM-DD

## Strategic Analysis
**SWOT**: Strengths: [evidence] | Weaknesses: [gap] | Opportunities: [trend] | Threats: [risk]
**Competitors**: [Competitor] - Gap: [gap] - Our Advantage: [ours]

## Action Items
- [ ] ACTION-001: [Task] (Due: YYYY-MM-DD)

## Notion Sync
[ ] Synced: [URL] OR [ ] SYNC_SKIPPED: [reason]
```

---

## Bayesian Scoring

### Formula
```
Posterior = Prior + Σ(Signal_Strength × Contribution)
```

### Dimensions

| Type | Dimensions |
|------|------------|
| **Success** | pain_intensity, market_evidence, solution_gap, timing_signal, execution_fit |
| **Payment** | economic_impact, purchase_intent, budget_access, urgency, trust_signals |

### Scoring Rules
- **Prior**: Estimate from industry context (do NOT hardcode)
- **Strength**: 0.0-1.0 (based on evidence)
- **Contribution**: e.g., "+0.10"
- **Confidence**: high/medium/low

---

## Evidence Format [BLOCKER]

Every evidence quote MUST include:

```markdown
> **Original**: "[Complete original text]"
> **Source**: [Source Name](URL)
> **Type**: community_discussion
> **Published**: YYYY-MM-DD
```

**Source Types**: `community_discussion` | `blog_article` | `industry_survey` | `competitor_review` | `documentation` | `interview` | `social_post`

---

## Completion Checklist

### [BLOCKER] Must Pass
- [ ] `analysis-result.json` exists with valid JSON
- [ ] `reports/analysis-report-{date}.md` exists with full Markdown report
- [ ] Full Markdown report presented to user
- [ ] All evidence has: full_text + URL + type + date
- [ ] No truncated text, no placeholders

### [REQUIRED] Should Pass
- [ ] Bayesian prior has reasoning
- [ ] Signal assessments have evidence_quotes
- [ ] key_uncertainties listed
- [ ] Notion sync completed FROM MD FILE (not from JSON)
- [ ] Notion sync status stated in conversation

### [QUALITY] Consistency Check
- [ ] MD file content == User conversation output
- [ ] Notion content == MD file content (no simplification)
- [ ] Evidence quotes preserved across all outputs

---

## File Structure

```
workspace/projects/{project}/
├── config/research-charter.json
├── data/
│   ├── raw.jsonl
│   ├── candidate_items.jsonl
│   ├── analysis_input.json
│   └── analysis-result.json
└── reports/
    ├── analysis-report-{date}.md   # ⭐ Single Source of Truth (SSOT)
    ├── {date}.md                   # Auto-generated brief report
    └── weekly-{year}-{week}.md     # Weekly report

config/
├── sources.json          # [BLOCKER] Data sources
└── keys.json             # API keys (gitignored)

scripts/
├── run_pipeline.py       # Main pipeline script
├── manage_actions.py     # Action tracker
└── collectors/           # Data collectors

references/
├── analysis-result-schema.md  # Detailed JSON schema
└── notion-page-template.md    # Report template
```

---

## Notion Sync Flow (From MD File)

```
                    ┌──────────────────────────────────┐
                    │  Stage 5: MD Report Generation   │
                    └───────────────┬──────────────────┘
                                    │
                                    ▼
          ┌─────────────────────────────────────────────────┐
          │  reports/analysis-report-{date}.md              │
          │  ─────────────────────────────────              │
          │  • Executive Summary                            │
          │  • Bayesian Scores (tables)                     │
          │  • Pain Points (full evidence quotes)           │
          │  • Strategic Analysis (SWOT, competitors)       │
          │  • Action Items                                 │
          └───────────────────┬─────────────────────────────┘
                              │
                              │ READ (Only data source)
                              │
                              ▼
          ┌─────────────────────────────────────────────────┐
          │  Stage 6: Notion Sync                           │
          │  ─────────────────────                          │
          │  • Parse MD file structure                      │
          │  • Convert to Notion block format               │
          │  • Preserve content integrity (no simplification)│
          └───────────────────┬─────────────────────────────┘
                              │
                              ▼
          ┌─────────────────────────────────────────────────┐
          │  Notion Page                                    │
          │  ──────────                                     │
          │  Content == MD File Content ✓                   │
          └─────────────────────────────────────────────────┘
```

**⚠️ Consistency Guarantee:**
1. MD file is the Single Source of Truth (SSOT)
2. Notion sync MUST read from MD file
3. Three outputs must be consistent: MD file == Conversation output == Notion page
