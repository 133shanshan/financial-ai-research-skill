# investment_committee/ — 投决会对抗决策信号目录（v3.10.0）

本目录存放 G10 投决会对抗决策闭环的产出物。每次含投资建议的交付，须在此写入一份决议信号文件。

## 目录结构

```
investment_committee/
├── README.md
└── <delivery_id>.json      # 投决会决议信号（schema 见 references/investment-committee.md §5）
```

## 决议信号文件字段（摘要）

- `delivery_id`：交付唯一 ID
- `topic`：待决议题（标的 / 配置 / 时机 / 仓位）
- `members`：五委员角色列表
- `positions`：各委员立场与论据（含 provenance 引用）
- `cross_examination`：交叉质询交锋记录
- `resolution`：`verdict` / `consensus` / `key_divergences` / `risk_plan` / `dissent`
- `timestamp`：决议时间

## 与 G9 协同

`resolution.consensus` / `resolution.verdict` 作为新的质量信号维度，由自进化协调员汇总进 `evolution/signals/<delivery_id>.json`。

## 降级

投决会基础设施不可用时，本目录可不写入，但报告须在第 19 章（或声明处）标注「投决会基础设施不可用，本次未跑对抗决策」。
