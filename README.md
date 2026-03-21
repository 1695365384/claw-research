# openclaw-market-demand-research

Reusable OpenClaw skill for market-demand research.

This repository only maintains the skill itself:

- [SKILL.md](/Users/limingwu/Documents/mvp/police/SKILL.md)
- [scripts/run_pipeline.py](/Users/limingwu/Documents/mvp/police/scripts/run_pipeline.py)
- [references/](/Users/limingwu/Documents/mvp/police/references)
- [tests/test_run_pipeline.py](/Users/limingwu/Documents/mvp/police/tests/test_run_pipeline.py)

The workflow prepares normalized candidate items, analysis inputs, reports, and a strict handoff contract for OpenClaw plus Notion MCP.

## Repository Shape

```text
openclaw-market-demand-research/
├── SKILL.md
├── README.md
├── requirements.txt
├── data/
├── input/
├── references/
├── scripts/
└── tests/
```

## Local Validation

```bash
python3 -m py_compile scripts/run_pipeline.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 /Users/limingwu/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```
