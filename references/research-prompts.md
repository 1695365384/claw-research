# Prompt Design

The workflow now stops at candidate preparation. OpenClaw should read from `workspace/projects/{project_name}/`:

- `data/analysis_input.json`
- `data/candidate_items.jsonl`
- `config/research-charter.json` (if exists)

Then run its own analysis.

Write the final structured result to:

- `data/analysis-result.json`

Use the current runtime UTC timestamp for `generated_at`. Do not copy dates from examples.

## Recommended Agent Tasks

Ask OpenClaw to produce:

- repeated pain points
- user scenarios
- current workarounds
- payment signals
- candidate clusters
- **Bayesian probability scores** (success and payment likelihood)
- next interview targets
- **Hypothesis validation** (if charter exists)
- **Strategic analysis** (SWOT, competitors, user journey)
- **Actionable insights** with evidence basis
- **Market sizing** (TAM/SAM)
- **Action items** for next steps

---

## Bayesian Scoring Instructions (Dynamic Evaluation)

**Core Principle**: Do not use hardcoded values. Evaluate dynamically based on actual evidence.

### Step 1: Estimate Prior Probability

Estimate based on project context, considering:
- Industry/vertical baseline success rate
- Business model (B2B/B2C, subscription/one-time)
- Market maturity
- Price range

**Must output prior estimation reasoning**, for example:
- "B2B SaaS in the cross-border e-commerce customer service vertical has ~12% success rate"
- "Consumer apps in this category have ~3% paid conversion"

### Step 2: Assess Signal Strength by Dimension

For each dimension, output:
- `strength`: 0.0-1.0 (not true/false)
- `reasoning`: why this strength
- `evidence_quotes`: supporting original text (must quote)
- `contribution`: contribution to posterior (e.g., "+0.12")

**Success Probability Dimensions**:
| Dimension | Evaluation Points |
|-----------|-------------------|
| pain_intensity | Emotional word strength, pain specificity, repetition frequency |
| market_evidence | Evidence count, source diversity, content consistency |
| solution_gap | Dissatisfaction with existing solutions, lack of alternatives |
| timing_signal | Market timing, technology trends |
| execution_fit | Team-problem fit |

**Payment Probability Dimensions**:
| Dimension | Evaluation Points |
|-----------|-------------------|
| economic_impact | Quantified time/money loss |
| purchase_intent | Willingness to pay, explicit search for alternatives |
| budget_access | Decision authority, budget availability signals |
| urgency | Problem urgency |
| trust_signals | Trust foundation |

### Step 3: Calculate Posterior and Output Uncertainty

```
posterior = prior + Σ(dimension_contributions)
```

**Must output**:
- `calculation_summary`: concise calculation process
- `key_uncertainties`: main uncertain factors (missing evidence, contradictory signals)

### Evaluation Principles

1. **Evidence-based**: Every assessment must be supported by original text
2. **Transparent reasoning**: Users should understand why this score
3. **Acknowledge uncertainty**: Clearly point out missing evidence
4. **Avoid overconfidence**: Lower confidence when evidence is insufficient

---

## Hypothesis-Driven Analysis

If a `research_charter` is provided in the analysis input, validate each hypothesis:

### Hypothesis Validation Process

1. **Read** the `research_charter` from `analysis_input.json`
2. **For each hypothesis** in `research_questions`:
   - Search for supporting or contradicting evidence in candidate items
   - Assess evidence quality (quantity, diversity, consistency)
   - Determine validation status:
     - `validated`: Strong supporting evidence from multiple sources
     - `partially_validated`: Some supporting evidence, but gaps remain
     - `not_validated`: Insufficient evidence to conclude
     - `refuted`: Evidence contradicts hypothesis
3. **Output hypothesis validation matrix** in `hypothesis_validation` field

### Hypothesis Validation Output Structure

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

---

## Strategic Analysis Framework

In addition to Bayesian scoring, provide multi-dimensional business analysis:

### SWOT Analysis

- **Strengths**: Internal advantages, strong signals, unique capabilities
- **Weaknesses**: Internal limitations, evidence gaps, competitive disadvantages
- **Opportunities**: Market trends, unmet needs, favorable conditions
- **Threats**: Competitive risks, market changes, potential obstacles

Each dimension MUST include at least 2 evidence quotes with reasoning.

### Competitor Landscape

Identify 2-5 direct/indirect competitors. For each competitor, analyze:
- **name**: Competitor name
- **positioning**: How they position themselves
- **price_range**: Pricing model (e.g., "$50-450/month")
- **gap**: What they don't solve well
- **our_advantage**: How your solution could be better

### User Journey Analysis

Map pain points across the user journey stages. For each stage:
- **stage**: Stage name (e.g., "Discover problem", "Evaluate options", "Implement solution")
- **pain_level**: high | medium | low
- **current_solutions**: What users do now
- **evidence_count**: Number of supporting evidence items
- **key_activities**: What users actually do at this stage

---

## Actionable Insights Framework

Extract evidence-based, actionable recommendations from the analysis.

### Insight Structure

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

## Market Sizing Framework

Provide TAM (Total Addressable Market) and SAM (Serviceable Addressable Market) estimates.

### Sizing Structure

```json
{
  "market_sizing": {
    "tam_estimate": {
      "value": "$XX million",
      "reasoning": "Calculation logic and data sources",
      "confidence": "low | medium | high"
    },
    "sam_estimate": {
      "value": "$XX million",
      "reasoning": "Calculation logic and data sources",
      "confidence": "low | medium | high"
    }
  }
}
```

---

## Action Items Framework

Generate specific next steps based on the analysis.

### Action Item Structure

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

## Suggested Prompt

```text
Read workspace/projects/{project_name}/data/analysis_input.json and workspace/projects/{project_name}/data/candidate_items.jsonl.
If research_charter exists in analysis_input.json, use it for hypothesis-driven analysis.

## Analysis Tasks

1. **Pain Point Analysis**
   - Identify repeated pain points with evidence counts
   - Group into opportunity clusters
   - Note current workarounds

2. **Payment Signal Detection**
   - Find explicit willingness-to-pay signals
   - Identify time/money loss quantification
   - Note budget authority signals

3. **Bayesian Probability Scoring**
   - Estimate prior based on industry/market context
   - Assess each dimension with evidence quotes
   - Calculate posterior with uncertainty

4. **Hypothesis Validation** (if charter exists)
   - Validate each hypothesis from research_charter
   - Determine status: validated/partially_validated/not_validated/refuted
   - List supporting and missing evidence

5. **Strategic Analysis**
   - SWOT: Each dimension with 2+ evidence quotes
   - Competitor landscape: 2-5 competitors with gaps
   - User journey: Map pain across stages

6. **Synthesis**
   - Extract 3-5 actionable insights with evidence basis
   - Estimate TAM/SAM with reasoning
   - Generate action items for next steps

Be strict about evidence quality. Do not invent unsupported conclusions.
Only mark signals as observed if there is clear textual evidence.

Write the answer as JSON following `references/analysis-result-schema.md`.
If Notion MCP is unavailable or the sync fails, state explicitly: `SYNC_SKIPPED`.
```

---

## Analysis Process Summary

1. Read research charter (if available)
2. Perform Bayesian probability analysis
3. Validate hypotheses against evidence
4. Generate strategic analysis (SWOT, competitors, user journey)
5. Extract actionable insights with evidence basis
6. Estimate market sizing (TAM/SAM)
7. Generate action items for next steps
8. Output comprehensive analysis following schema
