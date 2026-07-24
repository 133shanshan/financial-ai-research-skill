# 复杂度分级执行规范（tiering，v3.12.0 新增）

> 目标：**在不降低任何 fail-closed 门槛的前提下省 token**。
> 机制：按 query 复杂度分三档（T1/T2/T3），仅控制「是否拉起昂贵的 agent 流程」；
> 廉价的结构校验（G1/G2/G4/G5）在所有档位照常跑；被跳过的 gate 由报告写**豁免声明**（check 脚本已接受），不破坏 fail-closed。
> T3 完整档行为与本规范引入前（v3.11.0）完全一致。

---

## 一、分级判定规则（Step 0 由 orchestrator 执行）

判定顺序：先看「用户显式点名」（override），否则按意图分档。

### 0. 用户显式 override（优先级最高）
用户点名某流程 → 该 gate **强制 RUN**，不受 tier 限制。
- "跑一下投决会 / 做对抗审计 / 跑 benchmark / 做自进化 / 摄取邮件知识" 等 → 对应 gate RUN。

### 1. T1 轻量（单点查询，最省 token）
- 特征：单点事实 / 价格 / 指标 / 概念查询；**无投资建议**；无"深度/完整/多维度/Agent Teams"等词；非组合级 / 重大判断。
- 示例："茅台今天跌多少""最新 CPI 是多少""存款准备金率是什么""解释一下北向资金"。
- 预期 agent 开销：仅必要数据采集（若有）+ 报告生成 + 质量门（1 个轻 agent）。**跳过**反方审计、投决会、benchmark、自进化、知识回流。

### 2. T2 标准（单标的 / 单行业研判）
- 特征：单标的或单行业研判，或 1–2 维度分析；**无组合级建议**、无重大决策、无显式"深度"。
- 示例："分析一下宁德时代""半导体行业现状怎么样""美联储这次加息对 A 股影响"。
- 预期 agent 开销：核心分析师（1–3 个）+ 反方审计（1 个）；**跳过**投决会 / benchmark / 自进化 / 知识回流（除非含投资建议或用户点名）。

### 3. T3 完整（组合 / 重大判断 / 显式深度）
- 特征：多维度 / 组合建议 / 重大判断 / 用户显式"深度分析|完整研究|多维度|Agent Teams"，或含具体投资建议需投决会。
- 示例："给我一个 A 股均衡组合建议并说明""深度研究白酒板块并给配置建议"。
- 预期 agent 开销：全部流程（与本规范前完全一致）。

---

## 二、流程矩阵（RUN = 启动 agent + 写完整章节；EXEMPT = 跳过 agent，报告写豁免声明）

| Gate | 内容 | T1 轻量 | T2 标准 | T3 完整 |
|------|------|---------|---------|---------|
| G1 | 来源快照+字符锚定 | RUN（轻模式：被引片段须锚定快照；纯常识/记忆无外部数据则不引 provenance，verify 空过） | RUN | RUN |
| G2 | 证据→计算→结论 推导链 | RUN（单点须标 [证据]/[结论] 依据） | RUN | RUN |
| G3 | 对抗性反方审计 | **EXEMPT**（写豁免声明） | RUN | RUN |
| G4 | 自评估质量门 | RUN | RUN | RUN |
| G5 | 流程韧性声明 | RUN（写"未触发重试或降级"） | RUN | RUN |
| G6 | 可执行推理(Code Agent) | **EXEMPT**（纯定性声明） | RUN（若含定量） | RUN |
| G7 | 经验沉淀 | **EXEMPT**（无新增声明） | RUN | RUN |
| G8 | 工具治理(MCP) | **EXEMPT**（无工具声明） | RUN（若调工具） | RUN |
| G9 | 状态化多轮下钻 | **EXEMPT**（单轮声明） | RUN（若多轮） | RUN |
| G10 | 客观评测基准 | **EXEMPT** | **EXEMPT** | RUN |
| G11 | 自进化闭环 | **EXEMPT** | **EXEMPT** | RUN |
| G12 | 投决会对抗决策 | **EXEMPT**（无建议声明） | **EXEMPT**（除非含投资建议） | RUN |
| G13 | 非结构化知识回流 | **EXEMPT** | **EXEMPT** | RUN |

> 说明：G1/G2/G4/G5 在所有档位 RUN，但它们是**廉价的结构校验**（报告自身内容 + verify 脚本秒级跑），不额外拉 agent，故不影响省 token 目标。真正的 token 大头（投决会 5 委员、反方审计、benchmark、自进化、邮件抓取）在 T1/T2 被跳过。

---

## 三、EXEMPT gate 的精确豁免声明文本（须与 check-*.sh 接受的文本一致）

| Gate | 报告中写入的豁免声明文本 |
|------|--------------------------|
| G3 | `本报告不纳入对抗性审计（轻量模式 T1，依据 references/tiering.md 分级豁免）` |
| G6 | `本报告为定性分析，未含代码执行计算` |
| G7 | `本次无新增可复用经验` |
| G8 | `本报告未调用任何外部工具或数据源` |
| G9 | `本报告为单轮一次性产出，无多轮下钻` |
| G10 | `本报告不纳入客观评测基准` |
| G11 | `本报告不纳入自进化闭环` |
| G12 | `本报告不纳入投决会对抗决策` |
| G13 | `本报告未摄取外部邮件知识`（或 `本报告不纳入非结构化知识回流`） |

> 这些文本已被对应 check 脚本接受为放行条件；写入即视为该 gate 通过，**不降低可信门槛**（仅是"本轮按分级未执行该流程"的透明声明）。

---

## 四、orchestrator 执行指引
1. 进入标准流程先跑 Step 0：判定 tier（T1/T2/T3），并记下。
2. 对每个 gate，查本规范第二节矩阵：
   - 标 **RUN** → 照常启动对应 agent / 执行流程，report-writer 写完整章节。
   - 标 **EXEMPT** → **不启动**对应 agent，转交 report-writer 在报告中写第三节对应的豁免声明。
3. 用户显式点名某流程 → 该 gate 强制 RUN（覆盖矩阵）。
4. T3 完整档：矩阵全为 RUN，行为同 v3.11.0，无需特殊对待。

## 五、report-writer 执行指引
- 报告开局先判定 tier（同 Step 0），对 EXEMPT gate 直接写第三节的豁免声明文本，不等待任何 agent 结果。
- 对 RUN gate 照常写完整章节并跑对应 check-*.sh。
- 本规范不改变任何章节的"必含字段"——只是把"跳过流程"显式声明出来，check 脚本据此放行。

## 五.五、动态 agent 选择矩阵（v3.13.0 新增，省 token）

按 tier + 问题域裁剪并行 agent 数量，**不恒拉 9 模块分析师**：

| 问题域（触发词） | T1 轻量 | T2 标准 | T3 完整 |
|------------------|---------|---------|---------|
| 单一事实/价格/指标查询 | 0 agent（orchestrator 直答 + 质量门） | 0–1 agent | 按需 1–3 |
| 货币政策/政策语义 | policy-analyst | policy-analyst + adversarial-auditor | 全量 |
| 宏观数据/经济指标 | macro-analyst | macro-analyst(+adversarial) | 全量 |
| 行业/竞品研究 | industry-analyst | industry-analyst(+adversarial) | 全量 |
| 市场环境/全球 | market-analyst | market-analyst(+adversarial) | 全量 |
| 情绪/资金流向 | sentiment-analyst | sentiment-analyst(+adversarial) | 全量 |
| 基金深度分析 | fund-analyst | fund-analyst(+adversarial) | 全量 |
| 回测策略 | backtest-analyst | backtest-analyst | 全量 |
| 组合/多维度/含投资建议 | — | 核心 2–3 agent + 投决会(若有建议) | 全量 + 投决会 |

规则：
- T1 且纯常识/记忆可答 → 不启动任何子代理，orchestrator 直接生成报告并仅跑质量门（1 个轻 agent）。
- T2 仅拉与问题域相关的 1–3 个分析师；跨域问题才拉多个。
- 模块 methodology 文件（module1–9）**执行时按需 Read**，不随 skill 加载注入（见 module-index.md）。
- 用户显式点名 agent / 流程 → 强制启动，覆盖矩阵。

## 五.六、输出体积（token 预算）与 G1 轻量锚定（v3.13.0 新增，省 token）

### 输出体积分级（配合 report-structure.md 每章 token 预算）
- T1：极致精简——仅「核心结论 + 关键数据 + 来源」，省略分析过程散文（报告正文 ≤800 token）。
- T2：标准精简——结论 + 数据 + 要点式分析（报告正文 ≤2500 token）。
- T3：完整——全章节（同 v3.12.1 规范）。
- report-writer 须按 tier 套用 `references/report-structure.md` 的「紧模板」与「token 预算上限」，超出预算须压缩，不得用散文填充。

### G1 provenance 轻量锚定（T1/T2）
- T3：抓取即存**全文**快照 `provenance/<id>.json`（`snapshot_text`=全文），报告用 `（快照：provenance/<id>.json @ [s,e]）`，verify-provenance.py 全文比对。
- T1/T2：允许**轻量锚定**——`provenance/<id>.json` 仅存被引片段：`{mode:"light", url, title, snapshot_text:<被引片段原文>, quoted_spans:[{start,end,text}]}`；报告仍用 `（快照：provenance/<id>.json @ [s,e]）` 格式（区间相对片段本身）。verify-provenance.py 照常比对区间（片段内有效即通过），**fail-closed 门槛不变**。
- 纯常识/记忆无外部数据：不引 provenance，verify 空过（与原规则一致）。

## 五.七、结果缓存复用（v3.13.0 新增，省 token）

对「同标的 + 同问题域 + 近期」的研究结果做缓存复用，避免重复拉 agent：
- 检索：`cache/<topic_hash>.json`（topic_hash = 标的/问题域关键词的 sha1 前 12 位）。
- 命中条件：存在且 `updated_at` 距现在 ≤ 失效阈值（默认 24h；或该标的有新公告/财报/行情突变则失效）。
- 命中且有效：直接复用缓存中的结论 + provenance 引用 + variables，跳过对应 agent 重跑；报告标注「（结论复用缓存：cache/<hash>，更新于 <时间>）」。
- 未命中/失效：正常执行本轮分析，结束后写入 `cache/<topic_hash>.json`（含结论摘要 + provenance 引用 + updated_at + 失效依据）。
- 缓存仅优化效率，**不降低任何 fail-closed 门槛**：复用结论仍须带来源声明，G1/G2/G4/G5 等结构校验照常；若缓存结论含定量主张，仍须可映射到 variables（缓存中携带）。
- 用户显式要求"重新分析/刷新" → 忽略缓存，强制重跑。

## 六、版本与回退
- 本规范 v3.12.0 引入，v3.13.0 扩展（新增 §五.五 动态 agent 选择矩阵、§五.六 输出体积与 G1 轻量锚定、§五.七 结果缓存复用）；纯增量、向后兼容（T3 = 旧行为）。
- 若需回退：删除本文件 + 撤销 SKILL.md Step 0 + report-writer 分级小节 + check-adversarial-audit.sh 豁免分支即可，`git checkout v3.11.0` 亦可直接整包回退。
