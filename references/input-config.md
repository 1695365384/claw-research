# Input Configuration Contract

This workflow expects an external item feed plus either CLI flags or an optional JSON config file.

## Preferred Model

The outer OpenClaw agent is responsible for:

- deciding where to gather information
- collecting raw candidate items
- normalizing them into JSON or JSONL
- passing that file into this workflow

This workflow is responsible for:

- filtering
- dedupe
- local output generation

## Preferred Invocation

Use CLI flags for the common case:

```bash
python3 scripts/run_pipeline.py \
  --project-name "shopify-support-research" \
  --input-jsonl input/items.jsonl \
  --include-keyword "refund" \
  --exclude-keyword "hiring"
```

Use a config file only when you want to preserve a reusable preset.

## Config Shape

```json
{
  "project_name": "shopify-support-research",
  "output_dir": "./workspace/data",
  "report_dir": "./workspace/reports",
  "state_file": "./workspace/data/state.json",
  "max_items_per_source": 50,
  "lookback_hours": 48,
  "cluster_window_hours": 168,
  "input": {
    "mode": "external_file",
    "name": "openclaw-collected-items",
    "path": "./workspace/input/items.jsonl"
  },
  "keywords": {
    "include_any": ["shopify seller", "refund"],
    "exclude_any": ["hiring", "newsletter"]
  }
}
```

## Input Modes

- `external_file`
  Preferred. Read items from `input.path`.

- `builtin_sources`
  Compatibility fallback. Allows static sources in config, but this is not the recommended architecture.

## External Item Schema

Each input item should be a JSON object like:

```json
{
  "source": "reddit-r-shopify",
  "source_type": "community_post",
  "title": "Handling refunds is still manual",
  "url": "https://example.com/post/123",
  "text": "Post or comment text here"
}
```

Required fields:

- `title` or `text`

Recommended fields:

- `source`
- `source_type`
- `url`
- `captured_at`
- `published_at`

If you provide `captured_at` or `published_at`, use the actual runtime values. Do not hardcode example dates into real runs.

## CLI Override

You can override any config-backed input file:

```bash
python3 scripts/run_pipeline.py --config config.json --input-jsonl /path/to/items.jsonl
```
