<div align="center">

# Claw Research

**基于贝叶斯推断的市场需求研究，为产品决策提供量化支持**

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+">
  </a>
  <a href="./tests/">
    <img src="https://img.shields.io/badge/Tests-57%20passed-brightgreen.svg" alt="Tests">
  </a>
</p>

[English](./README.md) · 中文文档

*将市场信号转化为量化成功概率的独立技能。*

</div>

---

## 简介

`claw-research` 使用**贝叶斯推断**从市场信号中估算成功概率和付费概率。

不同于凭直觉验证或硬编码评分系统：

| 特性 | 传统评分 | Claw Research |
|:----:|:--------:|:-------------:|
| **阈值判断** | 硬编码（>=5条 = true） | 动态评估（0.0-1.0） |
| **先验概率** | 固定（10%） | 基于上下文估算 |
| **透明度** | 黑盒 | 完整推理 + 原文引用 |
| **不确定性** | 不追踪 | 明确列出缺失证据 |

### 核心优势

- **动态概率估算** - 基于实际证据上下文
- **透明推理** - 清楚看到为什么是这个概率
- **证据支撑** - 每个评分都有原文引用
- **明确不确定性** - 知道哪些证据缺失

---

## 贝叶斯评分引擎

```
P(Success|Evidence) = Prior + Summation(Signal_Strength x Relevance)
P(Payment|Evidence)  = Prior + Summation(Signal_Strength x Relevance)
```

### 输出示例

```json
{
  "success_probability": {
    "posterior": 0.32,
    "prior": {
      "value": 0.12,
      "reasoning": "B2B SaaS 在该垂直领域成功率约 12%"
    },
    "signal_assessments": [{
      "dimension": "pain_intensity",
      "strength": 0.75,
      "reasoning": "用户使用强烈情绪词并给出具体时间损失",
      "evidence_quotes": ["每天处理退款要花3小时，太崩溃了"]
    }],
    "key_uncertainties": ["未验证决策者视角"]
  }
}
```

---

## 适用场景

在以下情况下使用此技能：

- **数据驱动的做/不做决策** - 量化概率代替直觉
- **透明的验证过程** - 利益相关者可以看到推理过程
- **证据追踪** - 每个评估都有原文支撑
- **不确定性意识** - 动手前知道哪些信息缺失

---

## 工作流

```
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

---

## 仓库结构

```
claw-research/
├── SKILL.md                    # 技能定义
├── README.md                   # 英文文档
├── README.zh-CN.md             # 中文文档
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── config/
│   └── sources.json           # 数据源配置
│
├── data/
│   └── analysis-result.example.json  # 示例输出结构
│
├── input/
│   └── example-items.jsonl           # 示例输入
│
├── references/
│   ├── analysis-result-schema.md
│   ├── input-config.md
│   ├── notion-mcp-sync.md
│   ├── notion-page-template.md
│   ├── output-spec.md
│   └── research-prompts.md
│
├── scripts/
│   ├── run_pipeline.py
│   └── collectors/              # 数据收集器
│       ├── selector.py          # 智能源选择器
│       ├── search_collector.py  # 多引擎搜索
│       ├── rss_generic.py       # RSS 收集器
│       └── hacker_news.py       # HN API 收集器
│
└── tests/
    └── test_*.py
```

---

## 数据源

| 数据源 | 类型 | 需要认证 | 适用场景 |
|:------:|:----:|:--------:|:---------|
| Hacker News | API | 否 | 技术讨论、创业反馈 |
| Reddit | API | 是 | 社区痛点 |
| Bing | 搜索 | 否 | 通用网页搜索 |
| Baidu | 搜索 | 否 | 中文内容 |
| Google | 搜索 | 否 | 全球结果 |
| DuckDuckGo | 搜索 | 否 | 隐私优先搜索 |
| Woshipm | RSS | 否 | 中文产品经理社区 |
| PMCAFF | RSS | 否 | 产品管理 |
| TechCrunch | RSS | 否 | 科技新闻 |
| 36Kr | RSS | 否 | 中文科技/创业 |

---

## 完成定义

只有满足以下条件，一次调研才算**完成**：

- [x] 候选集已经生成
- [x] `analysis_input.json` 已生成
- [x] `analysis-result.json` 已生成
- [x] Notion 页面已创建/更新（或明确标注跳过）

---

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

---

## 校验

```bash
# 语法检查
python3 -m py_compile scripts/run_pipeline.py

# 运行测试
python3 -m pytest tests/ -v

# 快速验证
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

---

## 开源协议

本项目采用 **MIT 协议** 开源。详见 [LICENSE](./LICENSE)。
