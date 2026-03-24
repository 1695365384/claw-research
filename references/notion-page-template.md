# Notion Page Template

Professional market research report structure for claw-research output.

## ⚠️ MANDATORY Requirements

When creating reports from this template:

1. **DO NOT simplify or abbreviate** - Include full content
2. **Include ALL evidence quotes** - Every claim needs supporting text
3. **Show Bayesian calculations** - Not just final scores
4. **Complete all sections** - No "see analysis-result.json" shortcuts
5. **Include source links** - Every evidence must have clickable URL

This template defines the **MINIMUM** required content. Add more detail when available.

---

# [Project Name] Market Research Report
**Generated**: `generated_at`
**Research Phase**: `exploration | validation | optimization`
**Data Sources**: `X` candidate signals
**Confidence Level**: `high | medium | low`

---

## Executive Summary (30-Second Decision)

**Core Conclusion**: One-sentence summary of the most important finding.

**Recommended Actions** (Top 3):
1. [P0] First priority action
2. [P1] Second priority action
3. [P2] Third priority action

**Risk Alert**: Top 2 risks that could invalidate the conclusion.

---

## Research Overview

| Aspect | Details |
|--------|---------|
| Research Questions | Links to `research_charter.research_questions` if charter exists |
| Data Sources | `source_stats` summary |
| Methodology | Bayesian scoring + Strategic analysis frameworks |
| Confidence | Overall confidence in conclusions |

### Hypothesis Validation (if charter exists)

| Hypothesis | Status | Key Evidence | Missing |
|------------|--------|--------------|---------|
| RQ1 | Validated | 12 mentions | Decision maker view |
| RQ2 | Partial | 3 mentions | Budget signals |

---

## Key Insights Matrix

| Insight | Evidence | Action | Priority |
|---------|----------|--------|----------|
| Refund workflow is core pain | High (12 evidence) | Develop refund MVP | P0 |
| Payment willingness needs validation | Medium (5 evidence) | Interview 5 target users | P1 |
| Cross-team coordination is a bottleneck | Medium (4 evidence) | Design notification features | P2 |

---

## Strategic Analysis

### SWOT Analysis

**Strengths** (Internal Advantages)
- Strong pain signal from target users `[evidence: 12 mentions]`
- Clear quantification of time loss `[evidence: 8 mentions of hours lost]`

**Weaknesses** (Internal Limitations)
- Missing decision maker perspective `[gap: no budget authority signals]`
- No competitor comparison intent `[gap: users not actively comparing]`

**Opportunities** (External Factors)
- Growing e-commerce automation market `[trend: AI/automation adoption]`
- Shopify app ecosystem expansion `[trend: platform growing]`

**Threats** (External Risks)
- Shopify may build native refund automation `[risk: platform competition]`
- Existing competitors expanding into this space `[risk: Gorgias, Zendesk]`

### Competitor Landscape

| Competitor | Positioning | Price | Gap | Our Advantage |
|------------|-------------|-------|-----|---------------|
| Gorgias | All-in-one CS for e-commerce | $50-450/mo | Not refund-focused | Dedicated refund automation |
| Zendesk | Enterprise CS platform | $49-99/agent/mo | Complex for small sellers | Simple, Shopify-native |
| [Competitor 3] | [Positioning] | [Price] | [Gap] | [Our Advantage] |

### User Journey Pain Distribution

```
Stage              Pain Level    Current Solutions         Evidence
─────────────────────────────────────────────────────────────────────
Discover Problem   HIGH          Spreadsheets, Slack        8 items
Evaluate Options   MEDIUM        Google search               3 items
Implement Solution LOW           Manual workarounds          2 items
```

---

## Bayesian Score Details

### Success Probability: `35%`
**Prior**: 12% (B2B SaaS in cross-border e-commerce CS vertical)

| Signal | Strength | Contribution | Evidence |
|--------|----------|--------------|----------|
| Pain Intensity | 0.75 | +10% | "losing hours every week" |
| Market Evidence | 0.60 | +7% | 12 independent mentions |
| Solution Gap | 0.45 | +5% | "wish there was a better tool" |
| Timing Signal | 0.30 | +3% | AI automation trend |
| Execution Fit | 0.20 | -2% | No team evidence |

**Key Uncertainties**:
- Missing decision maker perspective
- No evidence of team-problem fit

### Payment Probability: `18%`
**Prior**: 6% (Typical B2B tool conversion rate)

| Signal | Strength | Contribution | Evidence |
|--------|----------|--------------|----------|
| Economic Impact | 0.80 | +8% | "2+ hours weekly on refunds" |
| Purchase Intent | 0.40 | +4% | "looking for alternatives" |
| Budget Access | 0.15 | +1% | No decision maker evidence |
| Urgency | 0.30 | +2% | "need this solved now" |
| Trust | 0.10 | -3% | No trust foundation |

**Key Uncertainties**:
- Budget authority unknown
- No explicit price sensitivity data

---

## Action Plan

### This Week (Immediate)

- [ ] **Interview 3 high-volume sellers** (Owner: X, Due: YYYY-MM-DD)
  - Target: Sellers with >100 orders/month
  - Validation: 3/5 confirm willingness to pay $50-100/month

- [ ] **Complete competitor pricing analysis** (Owner: Y, Due: YYYY-MM-DD)
  - Scope: Gorgias, Zendesk, native Shopify apps
  - Output: Pricing comparison table

### Next Week

- [ ] Based on interviews, adjust MVP scope
- [ ] Prepare user testing script for top 3 features
- [ ] Set up landing page for early interest validation

---

## Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shopify launches native refund tool | Medium | High | Focus on differentiation, build migration cost |
| Target users lack budget | Medium | High | Offer free tier, upsell to power users |
| Competitor price war | Low | Medium | Focus on unique value, not price |
| Market timing wrong | Low | Medium | Build relationships, iterate quickly |

---

## Knowledge Archive

**Insights Saved to Library**:
- Shopify seller refund pain concentrated in manual tracking and cross-team coordination
- High-volume sellers show stronger payment willingness

**Actions Tracked**:
- ACTION-001: Interview 5 high-volume sellers

**Next Review Date**: YYYY-MM-DD

---

## Appendix

- **Full Evidence List**: `candidate_items.jsonl`
- **Research Charter**: `research-charter.json`
- **Historical Reports**: [Link to Notion database]

---

## Template Variables Reference

When generating Notion pages, replace these placeholders:

| Placeholder | Source | Example |
|-------------|--------|---------|
| `[Project Name]` | `project_name` | "Shopify Refund Research" |
| `generated_at` | `generated_at` | "2026-03-24T10:30:00Z" |
| `Research Phase` | `research_charter.research_phase` | "exploration" |
| `X candidate signals` | `item_count` | "15" |
| `Confidence Level` | `bayesian_scores.*.confidence` | "medium" |
| Hypothesis table | `hypothesis_validation` | Dynamic rows |
| Insights Matrix | `actionable_insights` | Dynamic rows |
| SWOT content | `strategic_analysis.swot` | Dynamic content |
| Competitor table | `strategic_analysis.competitor_landscape` | Dynamic rows |
| Journey heatmap | `strategic_analysis.user_journey_stages` | Dynamic content |
| Bayesian details | `bayesian_scores` | Dynamic calculations |
| Action items | `action_items` | Dynamic tasks |
| Risk matrix | From analysis | Dynamic risks |

---

## Notion Block Structure

When using Notion MCP to create pages:

1. **Header Block**: Project name as H1
2. **Metadata Callout**: Generated date, phase, sources, confidence
3. **Executive Summary**: Callout with conclusion, actions, risks
4. **Research Overview**: Table with research details
5. **Hypothesis Validation** (if charter): Table with status
6. **Insights Matrix**: Table with priorities
7. **Strategic Analysis**: Toggle blocks for SWOT, Competitors, Journey
8. **Bayesian Details**: Toggle for each probability type
9. **Action Plan**: To-do blocks with checkboxes
10. **Risk Matrix**: Table with mitigation
11. **Knowledge Archive**: Summary of what was saved
12. **Appendix**: Links to source files

---

## Evidence Block Format (MANDATORY)

### Standard Evidence Block

Every evidence MUST follow this exact format:

```markdown
### 核心痛点 N: [Pain Point Title] (X条证据)

#### 证据 1: [Source Name]
> **原文**: "[Complete original text without truncation. Include full context and surrounding sentences if needed for understanding.]"
>
> **来源**: [Source Name](URL)
> **类型**: community_discussion | blog_article | industry_survey | interview
> **发布时间**: YYYY-MM-DD
> **标签**: #支付意愿 #时间量化 #痛点 #解决方案

#### 证据 2: [Source Name]
> **原文**: "[Another complete quote...]"
>
> **来源**: [Source Name](URL)
> **类型**: community_discussion
> **发布时间**: YYYY-MM-DD
```

### Evidence for Payment Signals

```markdown
### 支付信号: 明确支付意愿 (X条证据)

#### 证据 1: Hacker News
> **原文**: "Would pay good money for a unified PM workspace. I've tried everything - Notion, Linear, Coda, you name it. Nothing works for the PM workflow specifically."
>
> **来源**: [Hacker News](https://news.ycombinator.com/item?id=12345)
> **类型**: community_discussion
> **发布时间**: 2026-03-17
> **支付意愿**: 明确 - "Would pay good money"
> **价格范围**: 未量化
```

### Evidence for Quantified Data

```markdown
### 时间损失量化 (X条证据)

#### 证据 1: Medium Article
> **原文**: "Traditional PRDs take 20+ hours to write, become outdated within weeks, and nobody reads them anyway. PMs are stuck in documentation hell while the product moves forward."
>
> **来源**: [Medium - Product Management](https://medium.com/@pm/why-prds-are-broken)
> **类型**: blog_article
> **发布时间**: 2026-03-18
> **量化数据**: 20+ hours/PRD
> **痛点类型**: 时间浪费
```

---

## WRONG vs RIGHT Examples

### ❌ WRONG: No evidence, no sources

```markdown
## 核心发现

- PM 面临会议过多的痛点
- 文档负担重
- 建议开发 MVP
```

### ✅ RIGHT: Full evidence with sources

```markdown
## 核心发现

### 痛点 1: 会议过多/上下文切换 (8条证据)

#### 证据 1: Reddit r/ProductManagement
> **原文**: "As a PM, I spend 6+ hours in meetings daily. By the time I get to actual work like writing PRDs or analyzing data, my brain is fried. The constant context switching between strategic discussions, tactical execution, and stakeholder management is exhausting. I feel like I never have time for deep work anymore."
>
> **来源**: [Reddit r/ProductManagement](https://reddit.com/r/ProductManagement/comments/abc123)
> **类型**: community_discussion
> **发布时间**: 2026-03-20
> **标签**: #痛点 #时间量化

#### 证据 2: 知乎
> **原文**: "做了三年产品经理，感觉每天80%的时间都在开会。早会、需求评审、技术评审、设计评审、周报会、月度复盘。真正思考产品的时间少之又少。这种状态正常吗？大家都是怎么管理时间的？"
>
> **来源**: [知乎](https://zhihu.com/question/12345678)
> **类型**: community_discussion
> **发布时间**: 2026-03-08
> **标签**: #痛点 #时间量化
```

---

## Source Type Taxonomy

Use these standardized source types:

| Type | Chinese | Description |
|------|---------|-------------|
| `community_discussion` | 社区讨论 | Reddit, Hacker News, 知乎, Twitter/X |
| `blog_article` | 博客文章 | Medium, Substack, 个人博客 |
| `industry_survey` | 行业调研 | User Interviews, ProductPlan State of PM |
| `competitor_review` | 竞品评论 | G2, Capterra, Product Hunt reviews |
| `documentation` | 官方文档 | Company docs, API docs |
| `interview` | 用户访谈 | Direct interview transcripts |
| `social_post` | 社交媒体 | LinkedIn, Twitter/X threads |

