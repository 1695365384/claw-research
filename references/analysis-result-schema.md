# Analysis Result Schema (Reference)

> ⚠️ This is a **reference file**. The core prompt is in `SKILL.md`.
> Use this file only when you need detailed field definitions.

## JSON Schema

### Root Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `generated_at` | string | ✅ | UTC timestamp |
| `project_name` | string | ✅ | Project identifier |
| `top_pain_points` | array | ✅ | Pain points with evidence |
| `candidate_clusters` | array | ✅ | Opportunity clusters |
| `bayesian_scores` | object | ✅ | Probability assessments |
| `action_items` | array | ✅ | Next steps |

### Bayesian Scores Structure

```json
{
  "bayesian_scores": {
    "success_probability": {
      "posterior": 0.35,
      "prior": { "value": 0.12, "reasoning": "string" },
      "confidence": "high|medium|low",
      "signal_assessments": [
        { "dimension": "pain_intensity", "strength": 0.75, "contribution": "+0.10" }
      ],
      "calculation_summary": "Prior 0.12 + ... = 0.35",
      "key_uncertainties": ["string"]
    },
    "payment_probability": { /* same structure */ }
  }
}
```

### Hypothesis Validation

```json
{
  "hypothesis_validation": [{
    "hypothesis_id": "RQ1",
    "status": "validated|partially_validated|not_validated|refuted",
    "supporting_evidence": ["string"],
    "missing_evidence": ["string"]
  }]
}
```

### Strategic Analysis

```json
{
  "strategic_analysis": {
    "swot": {
      "strengths": ["string"],
      "weaknesses": ["string"],
      "opportunities": ["string"],
      "threats": ["string"]
    },
    "competitor_landscape": [{
      "name": "string",
      "gap": "string",
      "our_advantage": "string"
    }],
    "user_journey_stages": [{
      "stage": "string",
      "pain_level": "high|medium|low",
      "evidence_count": 5
    }]
  }
}
```

## Evidence Fields [BLOCKER]

Every evidence item must have:
- `full_text` - Complete original text
- `source_url` - Clickable URL
- `source_type` - Standardized type
- `published_at` - Publication date
