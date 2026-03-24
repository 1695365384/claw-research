# Analysis Result Schema

OpenClaw should write its final analysis to:

- `workspace/projects/{project_name}/data/analysis-result.json`

Use the current runtime UTC timestamp for `generated_at`. Do not reuse dates from this example.

## JSON Shape

```json
{
  "generated_at": "YYYY-MM-DDTHH:mm:ssZ",
  "project_name": "shopify-support-research",
  "research_charter_id": "optional - links to charter if used",

  "top_pain_points": [
    {
      "label": "Manual refund handling",
      "summary": "Refund work still moves through spreadsheets and chat.",
      "evidence_count": 4,
      "example_urls": ["https://example.com/post/1"]
    }
  ],
  "candidate_clusters": [
    {
      "name": "refund workflow",
      "summary": "Repeated complaints around refund execution and internal coordination.",
      "evidence_count": 5,
      "payment_signal": "weak",
      "example_titles": ["Refund handling is still manual"]
    }
  ],
  "payment_signals": [
    {
      "label": "Time loss",
      "summary": "Users explicitly describe losing hours every week."
    }
  ],
  "strongest_examples": [
    {
      "title": "Wish there was a better chargeback workflow",
      "url": "https://example.com/post/2",
      "reason": "Direct description of repeated time loss and a desire for a better tool."
    }
  ],
  "next_interview_targets": [
    {
      "persona": "Shopify seller operations lead",
      "reason": "Owns refund workflow and feels the pain directly."
    }
  ],
  "risks_or_gaps": [
    "Strong pain signal, but pricing evidence is still weak."
  ]
}
```

---

## Bayesian Scores (Dynamic Evaluation)

The `bayesian_scores` field provides context-aware probability estimates. Instead of hardcoded values, the AI dynamically assesses signal strength based on actual evidence and outputs full reasoning.

### Core Principle

```
Posterior = Prior + Signal_Contributions
P(Outcome|Evidence) = Prior + Σ(Signal_Strength × Relevance)
```

### Structure

```json
{
  "bayesian_scores": {
    "success_probability": {
      "posterior": 0.35,
      "prior": {
        "value": 0.12,
        "reasoning": "B2B SaaS in cross-border e-commerce customer service vertical has ~12% success rate based on industry benchmarks"
      },
      "confidence": "medium",
      "signal_assessments": [
        {
          "dimension": "pain_intensity",
          "strength": 0.75,
          "reasoning": "High emotional intensity, repeated mentions across sources",
          "evidence_quotes": ["quote1", "quote2"],
          "contribution": "+0.10"
        }
      ],
      "calculation_summary": "Prior 0.12 + pain_intensity 0.10 + market_evidence 0.07 + ... = 0.35",
      "key_uncertainties": ["Decision maker perspective missing", "No competitor comparison intent"]
    },
    "payment_probability": {
      "posterior": 0.18,
      "prior": {
        "value": 0.06,
        "reasoning": "Typical B2B tool conversion rate for this price range"
      },
      "confidence": "low",
      "signal_assessments": [...],
      "calculation_summary": "...",
      "key_uncertainties": ["Budget authority not mentioned", "No purchase timeline indicated"]
    }
  }
}
```

### Assessment Dimensions

#### Success Probability Dimensions

| Dimension | What to Evaluate | Strength Range |
|-----------|------------------|----------------|
| pain_intensity | Emotional word strength, pain specificity, repetition frequency | 0.0-1.0 |
| market_evidence | Evidence count, source diversity, content consistency | 0.0-1.0 |
| solution_gap | Dissatisfaction with existing solutions, lack of alternatives | 0.0-1.0 |
| timing_signal | Market timing, technology maturity, trends | 0.0-1.0 |
| execution_fit | Team-problem fit | 0.0-1.0 |

#### Payment Probability Dimensions

| Dimension | What to Evaluate | Strength Range |
|-----------|------------------|----------------|
| economic_impact | Quantified time/money loss | 0.0-1.0 |
| purchase_intent | Willingness to pay, explicit search for alternatives | 0.0-1.0 |
| budget_access | Decision authority, budget availability signals | 0.0-1.0 |
| urgency | Problem urgency, time pressure to solve | 0.0-1.0 |
| trust_signals | Trust foundation for the solution | 0.0-1.0 |

### Prior Estimation Guidelines

The AI should estimate prior probability based on:

1. **Industry context**: Baseline success rates for different industries/verticals
2. **Business model**: B2B/B2C, subscription/one-time payment
3. **Market maturity**: Emerging vs mature markets
4. **Price point**: Typical conversion rates for the price range

**Do NOT use hardcoded defaults.** Estimate based on the specific context.

### Confidence Levels

- `high`: Strong signals + consistent evidence + low uncertainty
- `medium`: Moderate signals + partial evidence + medium uncertainty
- `low`: Weak signals + contradictory evidence + high uncertainty

---

## Hypothesis Validation (Optional)

If a research charter was provided, validate each hypothesis:

```json
{
  "hypothesis_validation": [
    {
      "hypothesis_id": "RQ1",
      "hypothesis": "Sellers with >100 monthly orders struggle with manual refund tracking",
      "status": "validated",
      "supporting_evidence": [
        "12 independent mentions of manual refund tracking",
        "8 users explicitly mention spending 2+ hours weekly on refunds"
      ],
      "missing_evidence": [
        "Need interviews with operations leads",
        "Decision maker perspective missing"
      ],
      "confidence": "medium",
      "next_steps": "Interview 3-5 operations leads to validate decision process"
    }
  ]
}
```

**Validation Status Values**:
- `validated`: Strong supporting evidence from multiple sources
- `partially_validated`: Some supporting evidence, but gaps remain
- `not_validated`: Insufficient evidence to conclude
- `refuted`: Evidence contradicts hypothesis

---

## Strategic Analysis (New)

Multi-dimensional business analysis framework.

### SWOT Analysis

```json
{
  "strategic_analysis": {
    "swot": {
      "strengths": [
        "Strong pain signal from target users",
        "Clear evidence of time loss quantification"
      ],
      "weaknesses": [
        "Missing decision maker perspective",
        "No competitor comparison intent in evidence"
      ],
      "opportunities": [
        "Growing e-commerce automation market",
        "Shopify app ecosystem expansion"
      ],
      "threats": [
        "Shopify may build native refund automation",
        "Existing competitors (Gorgias, Zendesk) expanding into this space"
      ]
    }
  }
}
```

Each SWOT dimension MUST include at least 2 items with evidence references.

### Competitor Landscape
```json
{
  "strategic_analysis": {
    "competitor_landscape": [
      {
        "name": "Gorgias",
        "positioning": "All-in-one customer support for e-commerce",
        "price_range": "$50-450/month",
        "gap": "Not specifically focused on refund workflow automation",
        "our_advantage": "Dedicated refund automation with deeper workflow integration"
      },
      {
        "name": "Zendesk",
        "positioning": "Enterprise customer service platform",
        "price_range": "$49-99/agent/month",
        "gap": "Complex setup, not tailored for small Shopify sellers",
        "our_advantage": "Simple setup, Shopify-native, focused on refund operations"
      }
    ]
  }
}
```

Identify 2-5 direct/indirect competitors.

### User Journey Analysis
```json
{
  "strategic_analysis": {
    "user_journey_stages": [
      {
        "stage": "Discover Problem",
        "pain_level": "high",
        "current_solutions": ["Manual tracking in spreadsheets", "Slack notifications"],
        "evidence_count": 8,
        "key_activities": ["Manually logging refund requests", "Checking order status across systems"]
      },
      {
        "stage": "Evaluate Options",
        "pain_level": "medium",
        "current_solutions": ["Google search for alternatives", "Asking in seller communities"],
        "evidence_count": 3,
        "key_activities": ["Researching refund tools", "Comparing pricing and features"]
      }
    ]
  }
}
```

Map pain across 3-5 user journey stages.

---

## Market Sizing (New)

```json
{
  "market_sizing": {
    "tam_estimate": {
      "value": "$120M",
      "reasoning": "Global Shopify sellers: 1.2M. Assuming 10% have refund pain point. ARPU: $100/year",
      "confidence": "low"
    },
    "sam_estimate": {
      "value": "$12M",
      "reasoning": "Focus on North America, sellers with >100 orders/month",
      "confidence": "medium"
    }
  }
}
```

---

## Actionable Insights (New)
Evidence-based recommendations with clear next steps.

```json
{
  "actionable_insights": [
    {
      "insight": "Refund workflow automation is the most promising opportunity",
      "evidence_basis": [
        "12 independent pain mentions",
        "Bayesian success probability: 0.35",
        "3 users explicitly mentioned willingness to pay"
      ],
      "recommended_action": "Develop MVP focused on refund workflow automation",
      "expected_impact": "high",
      "confidence": "medium",
      "priority": "P0",
      "next_steps": [
        "Interview 5 high-volume sellers to validate payment willingness",
        "Research competitor pricing in refund automation space"
      ]
    }
  ]
}
```

---

## Action Items (New)
Specific next steps to take.

```json
{
  "action_items": [
    {
      "id": "ACTION-001",
      "action": "Interview 5 high-volume Shopify sellers",
      "due_date": "YYYY-MM-DD",
      "owner": "user",
      "status": "pending",
      "linked_insight": "High-volume sellers show strongest pain and payment signals",
      "validation_criteria": "At least 3 sellers confirm willingness to pay $50-100/month"
    }
  ]
}
```

---

## Field Notes

- `top_pain_points`
  Highest-confidence repeated pains backed by multiple candidate items.

- `candidate_clusters`
  Opportunity-shaped groupings, not just keyword buckets.

- `payment_signals`
  Evidence that time loss, revenue loss, switching intent, willingness to pay exists.

- `bayesian_scores`
  Quantitative probability estimates. Use to prioritize which opportunities deserve deeper validation.

- `hypothesis_validation` (optional)
  Validation status for each hypothesis from research charter.

- `strategic_analysis` (new)
  SWOT, competitor landscape, and user journey analysis.

- `market_sizing` (new)
  TAM and SAM estimates with reasoning.

- `actionable_insights` (new)
  Evidence-based recommendations with next steps.

- `action_items` (new)
  Specific tasks to take, with owners and due dates.

- `strongest_examples`
  Best supporting examples to show a human reviewer.

- `next_interview_targets`
  Which personas to contact next and why.

- `risks_or_gaps`
  Main uncertain factors and missing evidence.

---

## Output Requirements

For each probability assessment, MUST include:
1. `prior.value` + `prior.reasoning`: Why this prior
2. `signal_assessments`: Assessment for each dimension + original evidence
3. `contribution`: This dimension's contribution to posterior
4. `calculation_summary`: Concise calculation process
5. `key_uncertainties`: Main uncertain factors

For strategic analysis, MUST include:
1. SWOT with evidence references
2. 2-5 competitors with gaps and advantages
3. User journey stages with pain levels

For actionable insights, MUST include:
1. Clear insight statement
2. Evidence basis (at least 2 items)
3. Recommended action
4. Expected impact and confidence
5. Priority level

---

## Evidence Requirements (CRITICAL)

### Every Evidence Item MUST Include

When referencing evidence from `candidate_items.jsonl`, you MUST preserve:

1. **`full_text`**: Complete original text (not truncated)
2. **`source_url`**: Clickable URL to the original source
3. **`source_type`**: community_discussion, blog_article, industry_survey, etc.
4. **`source_name`**: Human-readable source name (e.g., "Reddit r/ProductManagement")
5. **`published_at`**: Publication date for context

### Evidence Format in Output

```json
{
  "evidence": {
    "full_text": "As a PM, I spend 6+ hours in meetings daily. By the time I get to actual work like writing PRDs or analyzing data, my brain is fried.",
    "source_url": "https://reddit.com/r/ProductManagement/comments/abc123",
    "source_type": "community_discussion",
    "source_name": "Reddit r/ProductManagement",
    "published_at": "2026-03-20T14:30:00Z"
  }
}
```

### In Markdown Output

```markdown
> **原文**: "As a PM, I spend 6+ hours in meetings daily. By the time I get to actual work like writing PRDs or analyzing data, my brain is fried."
>
> **来源**: [Reddit r/ProductManagement](https://reddit.com/r/ProductManagement/comments/abc123)
> **类型**: community_discussion
> **发布时间**: 2026-03-20
```

### DO NOT

- ❌ Truncate evidence text
- ❌ Paraphrase instead of quoting
- ❌ Omit source URLs
- ❌ Use generic sources like "various posts"
- ❌ Skip evidence for claims

### ALWAYS

- ✅ Quote complete original text
- ✅ Include clickable source link
- ✅ Specify source type
- ✅ Include publication date
- ✅ Tag special signals (payment, quantified data)

