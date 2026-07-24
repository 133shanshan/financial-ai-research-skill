# 自进化闭环（Self-Evolution Loop, v3.9.0）

> 本文件定义「金融AI投研」Skill 的**自进化闭环**（G9）：把单次交付产生的质量信号（G8 客观评测 + G5 主观质量门 + G4 经验沉淀 + 反方审计）回流为 Skill 自身的改进，形成「执行→提炼→沉淀→复用→自省」五阶段闭环，并支持**受控发布 + 秒级回滚**。

## 1. 必要性与差距（G9 问题）

- **G4 经验沉淀（v3.5）是单向写入**：产出经验卡片、回灌下次研究，但经验**不会反哺 Skill 本身**——Skill 的代码/规范/hooks 永远是人工手写升级。
- **G5 质量门（v3.2）、G8 评测基准（v3.8）产出了可量化信号**（quality_gate / benchmark_score），但这些信号**交付后即丢弃**，没有进入"如何改进 Skill"的回路。
- **标杆实践**：
  - **Hermes Agent（国金证券，2026）**：自进化五阶段「执行—提炼—沉淀—复用—自省」，三层记忆（MEMORY.md + USER.md + FTS5）跨会话持久化。
  - **蚂蚁 Agentic Engineering（2026）**：自进化双路径（Training-free 提示词 + Training-based 微调）；"用评测反馈反哺 Skill 升级"，**受控发布 + 秒级回滚**。
  - **东吴证券（2026）**：因子"假设—生成—评测—反馈—沉淀"闭环。
- **结论**：缺 G9，则 G4/G5/G8 的反馈价值被浪费，Skill 永远靠人手工升级。G9 把它们连成闭环，使 Skill 能"用自己产出的评测数据改进自己"。

## 2. 自进化五阶段闭环

```
阶段1 执行（Execute）  → 本次交付（已含 G4/G5/G8 全部质量护栏 + 正文十道校验）
阶段2 提炼（Distill）  → 交付后提取 evolution signals：benchmark_score/verdict、quality 三维度、未回应挑战、经验卡片、用户修正
阶段3 沉淀（Deposit）  → signals 写入 evolution/signals/<delivery_id>.json；若发现可复用的 Skill 级改进，生成 candidate_patch
阶段4 复用（Reuse）    → 下次交付自动加载 evolution/signals/ 历史信号 + 已 approved 的 candidate_patches 作为改进基线
阶段5 自省（Reflect）  → 比对"改进前 vs 改进后"的 benchmark/quality 趋势；若回归则触发回滚
```

## 3. 信号采集 schema（evolution/signals/<delivery_id>.json）

| 字段 | 类型 | 说明 |
|------|------|------|
| delivery_id | string | 本次交付唯一 ID（建议 `YYYYMMDD-HHMM-<seq>`） |
| timestamp | string | ISO8601 |
| benchmark_score | number(0-1) | 来自 G8（无则 `null` + `reason`） |
| benchmark_verdict | string | pass / amber / block / null |
| quality_dims | object | 来自 G5：`qualitative_rigor` / `quantitative_accuracy` / `verifiability` + `weighted_score` + `verdict` |
| unresolved_challenges | array | 反方审计中未完全回应/驳回的 P1+ 挑战摘要 |
| experience_cards | array | 本次 G4 新增卡片（类型 / 名称 / 路径） |
| user_corrections | array | 用户事后修正（若有，人工补录） |
| proposed_patches | array | 本次提取的候选补丁 ID 列表 |

## 4. 候选补丁 pipeline（evolution/candidate_patches/<patch_id>.json）

候选补丁 = 一条**可审计、可回滚**的 Skill 改进提案。

| 字段 | 类型 | 说明 |
|------|------|------|
| patch_id | string | 唯一 ID（建议 `SEV-<YYYYMMDD>-<seq>`） |
| trigger | string | 触发信号（如"benchmark 反方审计回应率连续偏低" / "某模块推导链缺失高频"） |
| affected_files | array | 受影响文件（`SKILL.md` / `references/*.md` / `hooks/*.sh`） |
| diff_summary | string | 改动摘要（自然语言 + 关键行） |
| rationale | string | 为什么要改、预期提升哪个维度 |
| status | enum | `proposed` → `approved` → `applied` → `rolled_back` |
| regression_guard | object | 回归守卫：受影响任务类型 + 不达标阈值（`benchmark_score < 0.60` 即回滚） |

**状态机**：
- `proposed`：由自进化协调员（Evolution Coordinator）提取，待人工 review（HITL）
- `approved`：人工确认，准备受控发布
- `applied`：写入 Skill 文件 + `git commit` + `git tag v3.x.1`（受控发布候选）；**立即跑 regression_guard**（重跑受影响的 benchmark 任务）
- `rolled_back`：若 regression_guard 不达标 → `git checkout v3.x.0` 秒级回滚 + 状态置 `rolled_back`

⚠️ **受控发布与回滚复用 git tag 机制**（与 v3.1.0 起版本管理一致）：每个 candidate_patch 的 `applied` 态对应一个增量 tag（如 `v3.9.1`），回滚即 `git -C <skill根> checkout <上一稳定 tag>`。这与既有十道校验的回退能力完全对齐，不引入新基础设施。

## 5. 与既有护栏协同

- **输入信号来自**：G8（benchmark_score / verdict）、G5（quality_dims）、G4（experience_cards）、反方审计（unresolved_challenges）。
- **高价值经验卡片 → 候选补丁**：G4 中标记 `reusable_skill: true` 的卡片，经自进化协调员评估后生成 candidate_patch（也可经 `SkillManage` 提升为正式 Skill，见 G4）。
- **降级不绕过既有校验**：自进化是**交付后元流程**，不修改正文校验门槛；它只新增第18章与 `evolution/` 落盘。
- **HITL**：candidate_patch 从 `proposed → applied` 必须人工确认（避免自动改 Skill 引入风险）。

## 6. 报告第18章「自进化反馈与改进建议」（v3.9.0 强制）

每份标准评测任务报告须含第18章，结构：
- **信号摘要**：benchmark_score + verdict、quality 三维度、本次经验卡片数、未回应挑战数（须含 `信号摘要` 或 `benchmark_score` 标记）
- **改进建议**：≥1 条（每条：观察到的问题 / 候选改进 / 建议状态 `proposed|已采纳|暂缓`），或显式声明「本次无新增改进建议」
- **SkillManage 提升建议**（可选）：列出可提升为正式 Skill 的高价值经验卡片

非标准任务：须显式声明「本报告不纳入自进化闭环」。

## 7. 降级处置

- 自进化基础设施不可用（`evolution/` 写入失败 / 信号采集脚本缺失 / 沙箱受限）→ best-effort，不阻塞投递；在第18章（或声明处）标注「自进化基础设施不可用，本次未发射 evolution signals」；不触发第十一道拦截但须明确声明。
- candidate_patch 的 regression_guard 执行失败 → 视为不达标，自动 `rolled_back`。

## 8. 第十一道 fail-closed 校验（check-self-evolution.sh）

- 报告含「自进化反馈与改进建议」章节，且须**同时包含**：
  - **信号摘要**（含 `信号摘要` 或 `benchmark_score` 标记），以及
  - **改进建议条目**（≥1 条含「改进建议」或显式声明「本次无新增改进建议」）
  - 否则拦截。
- 或报告含「本报告不纳入自进化闭环」豁免声明 → 放行。
- 既无章节又无声明 → 拦截。

> 设计对齐 G8 第十道校验的稳健双条件逻辑，避免仅标题被误判放行。详见 `.workbuddy/hooks/check-self-evolution.sh`。
