# Analysis Result Schema

OpenClaw should write its final analysis to:

- `data/analysis-result.json`

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

## Field Notes

- `top_pain_points`
  Highest-confidence repeated pains backed by multiple candidate items.

- `candidate_clusters`
  Opportunity-shaped groupings, not just keyword buckets.

- `payment_signals`
  Evidence that time loss, revenue loss, switching intent, or willingness to pay exists.

- `strongest_examples`
  Best supporting examples to show a human reviewer.

- `next_interview_targets`
  Which personas to contact next and why.

- `risks_or_gaps`
  Missing evidence, ambiguity, or reasons not to over-interpret the signal.
