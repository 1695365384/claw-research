# openclaw-market-demand-research

OpenClaw / Codex 的市场需求调研技能仓库。

[English README](./README.md)

## 简介

`openclaw-market-demand-research` 是一个独立的技能仓库，用来承载可重复执行的市场需求调研工作流。

它适合这样的场景：外层 agent 已经拿到帖子、评论、抱怨、issue、剪藏摘录等市场信号，需要一套稳定流程去：

- 标准化噪音输入
- 用关键词规则过滤无关内容
- 对重复证据去重
- 生成机器可读的分析输入
- 强制产出完整调研结果
- 把最终结论交给 OpenClaw 和 Notion MCP

这个仓库只维护技能本体，不负责调度、服务编排或 LLM 提供方配置。

## 适用场景

适合在以下情况下使用：

- 针对某类人群或某条工作流做重复市场扫描
- 在做产品验证前先整理出本地证据包
- 希望用比“随手搜索”更严格的调研流程
- 希望在“收集 -> 分析 -> Notion 同步”之间建立稳定交付协议

## 工作流

```text
+------------------------+
| 外部市场信号输入       |
| 帖子 / 评论 / 等       |
+-----------+------------+
            |
            v
+------------------------+
| run_pipeline.py        |
| 标准化/过滤/去重       |
+-----------+------------+
            |
            v
+------------------------+
| 本地产物               |
| analysis_input.json    |
| candidate_items.jsonl  |
| reports/*.md           |
+-----------+------------+
            |
            v
+------------------------+
| OpenClaw 分析          |
| analysis-result.json   |
+-----------+------------+
            |
            v
+------------------------+
| Notion MCP 同步        |
| 创建/更新页面          |
+------------------------+
```

## 仓库结构

```text
openclaw-market-demand-research/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── LICENSE
├── requirements.txt
├── data/
│   └── analysis-result.example.json
├── input/
│   └── example-items.jsonl
├── references/
│   ├── analysis-result-schema.md
│   ├── input-config.md
│   ├── notion-mcp-sync.md
│   ├── notion-page-template.md
│   ├── output-spec.md
│   └── research-prompts.md
├── scripts/
│   └── run_pipeline.py
└── tests/
    └── test_run_pipeline.py
```

## 输入

典型输入是外层准备好的 `items.jsonl` 或 `items.json` 文件。每条 item 代表一条市场信号。

详见 [references/input-config.md](/Users/limingwu/Documents/mvp/police/references/input-config.md)。

## 输出

流水线会先准备：

- `data/raw.jsonl`
- `data/candidate_items.jsonl`
- `data/analysis_input.json`
- `data/run_metrics.json`
- `reports/*.md`

随后 OpenClaw 必须继续产出：

- `data/analysis-result.json`

详见：

- [references/output-spec.md](/Users/limingwu/Documents/mvp/police/references/output-spec.md)
- [references/analysis-result-schema.md](/Users/limingwu/Documents/mvp/police/references/analysis-result-schema.md)

## 完成定义

只有满足下面这些条件，一次调研才算完成：

1. 候选集已经生成
2. `analysis_input.json` 已生成
3. `analysis-result.json` 已生成
4. 如果 Notion MCP 可用且用户没有拒绝同步，则已创建或更新 Notion 页面
5. 如果 Notion MCP 不可用，最终回复必须明确写 `本次未同步`

## 快速开始

```bash
python3 scripts/run_pipeline.py \
  --project-name "cross-border-ecommerce-merchant-pain" \
  --input-jsonl input/example-items.jsonl \
  --include-keyword "refund" \
  --include-keyword "chargeback" \
  --exclude-keyword "hiring"
```

然后让 OpenClaw：

1. 读取 `data/analysis_input.json`
2. 读取 `data/candidate_items.jsonl`
3. 写出 `data/analysis-result.json`
4. 通过 MCP 同步结论到 Notion

## 校验

```bash
python3 -m py_compile scripts/run_pipeline.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 /Users/limingwu/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

## 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](/Users/limingwu/Documents/mvp/police/LICENSE)。
