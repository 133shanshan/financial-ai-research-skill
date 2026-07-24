# evolution/ — 自进化闭环数据目录（v3.9.0）

本目录承载「金融AI投研」Skill 的自进化闭环（G9）落盘数据，由 `references/self-evolution.md` 规范。

## 目录结构

```
evolution/
├── README.md                      # 本说明
├── signals/                       # 每次交付的 evolution signals 包
│   └── <delivery_id>.json         # 信号摘要（benchmark_score/quality_dims/经验卡片/未回应挑战…）
└── candidate_patches/             # 候选 Skill 改进补丁
    └── <patch_id>.json            # 候选补丁（trigger/affected_files/diff_summary/status/regression_guard）
```

## signals/<delivery_id>.json 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| delivery_id | string | 本次交付唯一 ID（`YYYYMMDD-HHMM-<seq>`） |
| timestamp | string | ISO8601 |
| benchmark_score | number(0-1) | 来自 G8（无则 null + reason） |
| benchmark_verdict | string | pass/amber/block/null |
| quality_dims | object | 来自 G5：qualitative_rigor/quantitative_accuracy/verifiability + weighted_score + verdict |
| unresolved_challenges | array | 反方审计未完全回应/驳回的 P1+ 挑战摘要 |
| experience_cards | array | 本次 G4 新增卡片（类型/名称/路径） |
| user_corrections | array | 用户事后修正（人工补录） |
| proposed_patches | array | 本次提取的候选补丁 ID 列表 |

示例：
```json
{
  "delivery_id": "20260719-1835-001",
  "timestamp": "2026-07-19T18:35:00+08:00",
  "benchmark_score": 0.82,
  "benchmark_verdict": "pass",
  "quality_dims": {
    "qualitative_rigor": 8.5,
    "quantitative_accuracy": 9.0,
    "verifiability": 8.0,
    "weighted_score": 8.5,
    "verdict": "pass"
  },
  "unresolved_challenges": [],
  "experience_cards": [
    {"type": "asset-template", "name": "宁德时代研判模板", "path": "experience/asset-templates/宁德时代.md"}
  ],
  "user_corrections": [],
  "proposed_patches": ["SEV-20260719-001"]
}
```

## candidate_patches/<patch_id>.json 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| patch_id | string | 唯一 ID（`SEV-<YYYYMMDD>-<seq>`） |
| trigger | string | 触发信号 |
| affected_files | array | 受影响文件 |
| diff_summary | string | 改动摘要 |
| rationale | string | 改动的理由与预期收益 |
| status | enum | proposed → approved → applied → rolled_back |
| regression_guard | object | 回归守卫（受影响任务类型 + 不达标阈值） |

> 受控发布与回滚复用 git tag：每个 `applied` 态补丁对应增量 tag（如 `v3.9.1`），回滚即 `git -C <skill根> checkout <上一稳定 tag>`。

## 数据保留

- `signals/` 历史信号用于"改进前 vs 改进后"趋势比对（自省阶段），建议长期保留。
- `candidate_patches/` 仅保留终态（`applied` / `rolled_back`）补丁作为审计留痕；`proposed` 态补丁待人工 review 后转出。
