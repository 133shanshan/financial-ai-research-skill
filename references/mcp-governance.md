# 工具治理中心（MCP 范式）规范 — v3.6.0

> 本文件定义「金融AI投研」Skill 的 **工具治理中心（Tool Governance Center）**：把 AnySearch / AkShare / Bash / Code Agent 等所有外部工具与数据源的调用统一收口到治理层，做 **参数校验 + 调用审计 + 可重现**。
> 对标：AlphaTeam 工具治理中心、Anthropic 10 Agents 经 MCP 收口 11 家数据商（穆迪/邓白氏/晨星/标普/FactSet 等）。
> 补齐 G7 差距：原「工具层非统一」——AnySearch + AkShare 各自为政，缺统一调用审计。

---

## 1. 为什么需要工具治理中心

- **问题（G7）**：AnySearch / AkShare / Bash / Code Agent 各自为政，调用参数、时机、结果无人审计，无法重现，且易遗漏来源、重复采数、口径不一。
- **监管驱动**：EU AI Act 高风险条款 2026-08 生效，金融 AI 的「数据从哪来、怎么算的」须可审计；BigFinanceBench 证明「结论对」≠「推导可审计」。
- **目标**：所有外部工具/数据调用统一收口到治理层，落实 **参数校验 → 调用审计 → 可重现** 闭环，与既有 provenance 快照（数据内容锚）配合实现端到端可追溯。

---

## 2. 治理层四大职责

1. **统一入口（Unified Entry）**：所有外部数据/工具调用**必须**经治理层调度，禁止子代理 / Code Agent 绕过治理层直接裸调外部 API / 命令行。
2. **参数校验（Parameter Validation）**：调用前校验必填参数、格式、取值范围（见 §4 白名单）。非法参数拒绝并记录，不发起真实调用。
3. **调用审计（Call Audit）**：每次调用（含重试）写一条 append-only 记录到 `tool_audit/<task_id>/tool_calls.jsonl`（见 §3 schema）。
4. **可重现（Reproducibility）**：每条数据结论须能经 `call_id` → `provenance` 快照 回溯；同一 `task_id` 的审计日志可被复跑核对。

---

## 3. 审计记录 Schema（`tool_audit/<task_id>/tool_calls.jsonl`，每行一个 JSON）

```json
{
  "call_id": "call-001",
  "tool": "anysearch | akshare | bash | code_agent | ...",
  "params": {
    "normalized": { "query": "...", "symbol": "600519", "...": "..." },
    "raw": "原始调用串（便于复现）"
  },
  "timestamp": "2026-07-19T15:30:00+08:00",
  "provenance_ref": "provenance/<source_id>.json @ [s,e]",
  "status": "success | retry | fail | degraded",
  "attempts": 1,
  "duration_ms": 1234,
  "result_hash": "sha256:...",
  "error": null
}
```

- `call_id`：本 task 内自增（call-001, call-002, ...），全局唯一于 `task_id`。
- `provenance_ref`：该调用产生的数据若写入报告，须对应一条 provenance 快照（provenance/<id>.json @ [s,e]）；纯计算无外部数据时为 `null`。
- `status=retry`：本次失败但已触发 resilience 重试（≤3 次指数退避）；最终成功记 `success`，耗尽记 `fail`/`degraded`。
- `status=degraded`：治理层/工具不可用，降级为人工/定性估算，须在报告中登记降级原因。

---

## 4. 参数校验白名单（示例，须随接口扩展维护）

| 工具 | 必填 | 格式/范围约束 | 拒绝示例 |
|------|------|--------------|----------|
| anysearch | `query` | 长度 ≤ 512；含敏感实体须 `domain` 限定 | 空 query、query>512 |
| akshare | `symbol` | 6 位数字 A 股代码 / 合规接口名（白名单） | `symbol="茅台"`（未归一化为 600519）|
| bash | — | 禁用 `rm -rf /`、`mkfs`、`curl` 出域未登记 | 含 `rm -rf` 的删除命令 |
| code_agent | `task_id` | 须指向 `code_workspace/<task_id>/` | 缺 task_id 的裸 Python |

> 校验不通过 → 治理层拒绝调用，记录 `status=fail` + `error="param_invalid"`，回退给调用方修正参数重试；仍失败按 `references/resilience.md` 降级。

---

## 5. 与既有护栏的协同

- 治理层是**「数据采集」的统一前门**；`provenance` 快照是**「数据内容」的锚**；两者配合实现端到端可审计、可重现。
- 治理层记录的 `retry`/`degraded` 事件 **同步** 一条到 `resilience_log`（不重复造事件，治理层 `call_id` 即 resilience 事件 id 来源），由 report-writer 写入第 12 章「流程韧性声明」。
- 治理层**不绕过**既有七道 fail-closed 校验：provenance / 推导链 / 反方审计 / 自评估质量门 / 流程韧性 / 可执行推理 / 经验沉淀。
- 第八道 fail-closed 校验 `check-mcp-governance.sh` 拦截缺失「工具治理与调用审计」章节或章节空洞的报告。

---

## 6. 报告交付（第 15 章）

report-writer 在 **Step 4.9（v3.6.0 强制）** 写第 15 章「工具治理与调用审计」：
- 列本次所有 `call_id` + `tool` + 归一化参数 + `provenance_ref` + `status`（成功/重试/失败/降级计数）。
- 若本次研究**未调用任何外部工具或数据源**（纯定性分析），须显式声明「本报告未调用任何外部工具或数据源」。
- 治理层不可用时的降级声明：「工具治理层不可用，本次调用未统一审计」+ best-effort 补记调用清单。

---

## 7. 降级处置

| 场景 | 处置 |
|------|------|
| 治理层本身不可用 | 子代理仍可采数据，但须在第 15 章标注「工具治理层不可用，本次调用未统一审计」并 best-effort 补记调用清单（不阻塞投递）|
| 单工具被治理层拒绝（参数非法）| 修正参数重试；仍失败标注该数据缺失，按 `references/resilience.md` 降级 |
| 工具调用 fail/超时（重试耗尽）| `status=fail`，按 resilience 降级矩阵处置（替代源 / 定性推断），事件同步 resilience_log |

> 原则：**统一审计优先，降级不绕过既有质量校验**。治理层是「收口」，不是「放行开关」——降级只改变数据获取方式，不改变 provenance / 推导链 / 反方审计 / 自评估质量门 等校验门槛。
