# Analysis Result Schema

OpenClaw should write its final analysis to:

- `workspace/data/analysis-result.json`

Use the current runtime UTC timestamp for `generated_at`. Do not reuse dates from this example.

## JSON Shape

```json
{
  "generated_at": "YYYY-MM-DDTHH:mm:ssZ",
  "project_name": "shopify-support-research",
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

- `bayesian_scores` (optional but recommended)
  Dynamic Bayesian probability estimates with transparent reasoning.

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
          "strength": 0.8,
          "reasoning": "Multiple users describe pain with strong emotional words like 'crushing' and 'wasting 3 hours daily'",
          "evidence_quotes": ["Processing refunds takes 3 hours every day, it's crushing me", "This problem cost me customers"],
          "contribution": "+0.12"
        },
        {
          "dimension": "market_evidence",
          "strength": 0.6,
          "reasoning": "5 independent evidence points from Reddit, Twitter, industry forums covering different user segments",
          "evidence_count": 5,
          "source_diversity": "Across 3 platforms, 2 role types",
          "contribution": "+0.08"
        }
      ],
      "calculation_summary": "Prior 0.12 + Signal contributions 0.23 = Posterior 0.35",
      "key_uncertainties": ["Missing pricing sensitivity data", "Decision-maker perspective not validated"]
    },
    "payment_probability": {
      "posterior": 0.22,
      "prior": {
        "value": 0.08,
        "reasoning": "B2B SaaS in this price range ($50-200/month) has ~8% paid conversion rate"
      },
      "confidence": "low",
      "signal_assessments": [
        {
          "dimension": "economic_impact",
          "strength": 0.7,
          "reasoning": "Users explicitly mention time cost and revenue loss, but lack specific amounts",
          "evidence_quotes": ["Wasting 10 hours per week", "Lost 2 customers because of this"],
          "contribution": "+0.10"
        },
        {
          "dimension": "purchase_intent",
          "strength": 0.4,
          "reasoning": "Users express 'want better tools' but no explicit 'looking for alternatives' or 'willing to pay'",
          "evidence_quotes": ["Hope there's a better workflow"],
          "contribution": "+0.04"
        }
      ],
      "calculation_summary": "Prior 0.08 + Signal contributions 0.14 = Posterior 0.22",
      "key_uncertainties": ["Budget authority not mentioned", "No competitor comparison intent"]
    }
  }
}
```

### Assessment Dimensions

#### Success Probability Dimensions

| Dimension | What to Evaluate | Strength Range |
|-----------|------------------|----------------|
| pain_intensity | Pain emotional intensity, frequency, specificity | 0.0-1.0 |
| market_evidence | Evidence count, source diversity, consistency | 0.0-1.0 |
| solution_gap | Dissatisfaction with existing solutions, lack of alternatives | 0.0-1.0 |
| timing_signal | Market timing, technology maturity, trends | 0.0-1.0 |
| execution_fit | Founder/team fit with the problem | 0.0-1.0 |

#### Payment Probability Dimensions

| Dimension | What to Evaluate | Strength Range |
|-----------|------------------|----------------|
| economic_impact | Quantified time/money loss | 0.0-1.0 |
| purchase_intent | Explicit willingness to pay or search for alternatives | 0.0-1.0 |
| budget_access | Decision authority, budget availability | 0.0-1.0 |
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

### Output Requirements

For each probability assessment, MUST include:
1. `prior.value` + `prior.reasoning`: Why this prior
2. `signal_assessments`: Assessment for each dimension + original evidence
3. `contribution`: This dimension's contribution to posterior
4. `calculation_summary`: Concise calculation process
5. `key_uncertainties`: Main uncertain factors

## Field Notes

- `top_pain_points`
  Highest-confidence repeated pains backed by multiple candidate items.

- `candidate_clusters`
  Opportunity-shaped groupings, not just keyword buckets.

- `payment_signals`
  Evidence that time loss, revenue loss, switching intent, or willingness to pay exists.

- `bayesian_scores`
  Quantitative probability estimates. Use to prioritize which opportunities deserve deeper validation.

- `strongest_examples`
  Best supporting examples to show a human reviewer.

- `next_interview_targets`
  Which personas to contact next and why.

- `risks_or_gaps`
  Missing evidence, ambiguity, or reasons not to over-interpret the signal.
