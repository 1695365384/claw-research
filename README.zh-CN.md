# claw-research

**基于贝叶斯推断的市场需求研究，为产品决策提供量化支持。**

[English README](./README.md)

## 简介

`claw-research` 是一个使用**贝叶斯推断**从市场信号中估算成功概率和付费概率的技能仓库。

不同于凭直觉验证或硬编码评分系统，这个技能提供：

- **动态概率估算** - 基于实际证据上下文
- **透明推理** - 清楚看到为什么是这个概率
- **证据支撑** - 每个评分都有原文引用
- **明确不确定性** - 知道哪些证据缺失

## 核心功能：贝叶斯概率评分

```
P(成功|证据) = 先验概率 + Σ(信号强度 × 相关性)
P(支付|证据) = 先验概率 + Σ(信号强度 × 相关性)
```

### 与传统评分的区别

| 传统评分 | Claw Research |
|---------|---------------|
| 硬编码阈值（≥5条 = true） | 动态强度评估（0.0-1.0） |
| 固定先验概率（10%） | 基于上下文估算先验 |
| 黑盒评分 | 完整推理 + 原文引用 |
| 不追踪不确定性 | 明确列出缺失证据 |

### 输出示例

```json
{
  “success_probability”: {
    “posterior”: 0.32,
    “prior”: {
      “value”: 0.12,
      “reasoning”: “B2B SaaS 在该垂直领域成功率约 12%”
    },
    “signal_assessments”: [{
      “dimension”: “pain_intensity”,
      “strength”: 0.75,
      “reasoning”: “用户使用强烈情绪词并给出具体时间损失”,
      “evidence_quotes”: [“每天处理退款要花3小时，太崩溃了”]
    }],
    “key_uncertainties”: [“未验证决策者视角”]
  }
}
```

## 适用场景

适合在以下情况下使用：

- **数据驱动的做/不做决策** - 量化概率代替直觉
- **透明的验证过程** - 利益相关者可以看到推理过程
- **证据追踪** - 每个评估都有原文支撑
- **不确定性意识** - 动手前知道哪些信息缺失

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
claw-research/
├── SKILL.md                    # 技能定义
├── README.md                   # 英文文档
├── README.zh-CN.md             # 中文文档
├── LICENSE
├── requirements.txt
├── .gitignore
├── data/
│   └── analysis-result.example.json  # 示例输出结构
├── input/
│   └── example-items.jsonl           # 示例输入
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

# 运行时工作空间（不提交到 git）
workspace/
├── data/
│   ├── raw.jsonl
│   ├── candidate_items.jsonl
│   ├── analysis_input.json
│   ├── analysis-result.json
│   ├── run_metrics.json
│   └── state.json
├── input/
│   └── *.jsonl              # 用户输入数据
└── reports/
    └── *.md                 # 生成的报告
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
