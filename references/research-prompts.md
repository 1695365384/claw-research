# Prompt Design

The workflow now stops at candidate preparation. OpenClaw should read:

- `workspace/data/analysis_input.json`
- `workspace/data/candidate_items.jsonl`

Then run its own analysis.

Write the final structured result to:

- `workspace/data/analysis-result.json`

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

## Suggested Prompt

```text
Read workspace/data/analysis_input.json and workspace/data/candidate_items.jsonl.

Identify repeated pain points, scenarios, workarounds, and payment signals.
Group the candidate items into opportunity clusters.
Calculate Bayesian probability scores for success and payment likelihood.

**Bayesian Analysis**:
- Use prior P(success)=0.10, P(payment)=0.05
- Detect signals from the text (time loss, revenue loss, switching intent, etc.)
- Calculate posterior probabilities using likelihood ratios from the schema
- Assign confidence based on signal strength and consistency

Be strict about evidence quality and do not invent unsupported conclusions.
Only mark signals as observed if there is clear textual evidence.

Return:
1. Top pain points
2. Candidate clusters
3. Payment signals
4. Bayesian scores (success_probability and payment_probability)
5. Most useful source examples
6. Next interview targets
7. Risks or evidence gaps

Write the answer as JSON following `references/analysis-result-schema.md`.
If Notion MCP is unavailable or the sync fails, state explicitly in the final reply: `SYNC_SKIPPED`.
```
