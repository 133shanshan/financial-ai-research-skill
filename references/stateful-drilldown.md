# 状态化多轮下钻（Stateful Drilldown，v3.7.0）

> 本规范对应调研方案 **G6「一次性报告」** 差距：原 Skill 每轮对话都从零开始，用户追问「把宏观部分展开」「对比下竞品」时上下文丢失、重复采数、推导链断裂。
> 标杆：**LangGraph Postgres checkpoint**——会话状态持久化、可恢复、上下文累积不丢。
> 核心原则：**同一会话（session）下钻追问，状态跨轮累积；已采数据/已算变量/已检索经验复用不重采，仅对新增范围增量执行。**

---

## 1. 为什么需要状态化多轮下钻

| 痛点（G6） | 状态化方案 |
|-----------|-----------|
| 追问「展开宏观」时重做全报告，浪费 token/时间 | 加载 `session_state`，仅对宏观模块增量下钻 |
| 前轮已采 provenance/已算 variables 在追问中丢失 | 状态文件持久化，下钻轮直接引用（`reused` 字段） |
| 多轮结论散落，无法呈现完整问题链 | `drill_tree` 记录父子轮次，报告第16章呈现完整追问链 |
| 崩溃/超时后只能从头来 | checkpoint 协议：每轮结束写快照，重启从最近 checkpoint 续做 |
| 同一会话重复调用 AnySearch/AkShare | 治理层审计含 `session_id`，复用调用不重复计费 |

---

## 2. 会话状态 Schema（`session_state/<session_id>.json`）

每次新研究创建独立 session；同会话后续追问复用同一文件。**目录脚手架** `session_state/` 已随 v3.7.0 纳入版本管理（含 `.gitkeep`）。

```json
{
  "schema_version": "1.0",
  "session_id": "finres-20260719-1430-a1b2",
  "created_at": "2026-07-19T14:30:00+08:00",
  "updated_at": "2026-07-19T15:10:00+08:00",
  "task_id": "financial-research-20260719-1430",
  "topic": "贵州茅台（600519）投资研判",
  "turns": [
    {
      "turn": 1,
      "user_query": "分析贵州茅台投资价值",
      "focus": "全维度初始研判（政策/宏观/行业/情绪/财务）",
      "modules_activated": ["policy","macro","industry","sentiment","fund"],
      "provenance_refs": ["prov_001","prov_002"],
      "variable_refs": ["var_roe","var_pe_ttm"],
      "tool_audit_ref": "tool_audit/financial-research-20260719-1430/tool_calls.jsonl",
      "experience_refs": ["exp_maotai_template"],
      "conclusion_delta": "茅台护城河稳固，当前估值合理偏低，给予核心推荐",
      "deliverable": "reports/茅台投研报告_20260719.pdf",
      "status": "done"
    },
    {
      "turn": 2,
      "parent_turn": 1,
      "drill_type": "module_expand",
      "user_query": "把宏观部分展开，重点看白酒消费景气度",
      "focus": "宏观模块下钻：白酒消费景气 + 居民杠杆",
      "modules_activated": ["macro"],
      "reused": {
        "provenance_refs": ["prov_001","prov_002"],
        "variable_refs": ["var_roe","var_pe_ttm"],
        "tool_audit_ref": "tool_audit/financial-research-20260719-1430/tool_calls.jsonl"
      },
      "provenance_refs": ["prov_007"],
      "variable_refs": ["var_consumption_growth"],
      "conclusion_delta": "白酒消费景气边际走弱但龙头份额提升，对茅台量价影响可控",
      "deliverable": "reports/茅台投研报告_宏观下钻_20260719.pdf",
      "status": "done"
    }
  ],
  "drill_tree": {
    "root": {
      "turn": 1,
      "children": [
        {"turn": 2, "children": []}
      ]
    }
  },
  "cumulative_conclusion": "茅台长期护城河稳固；宏观下钻显示短期消费景气偏弱但龙头抗风险强，维持核心推荐，关注中秋动销验证。",
  "checkpoint": {
    "last_completed_turn": 2,
    "last_completed_step": "report_delivered",
    "recoverable": true,
    "snapshot_at": "2026-07-19T15:10:00+08:00"
  }
}
```

**字段说明**
- `session_id`：会话唯一标识，追问时由用户/系统带入；新建时生成 `finres-{YYYYMMDD-HHMM}-xxxx`
- `turns[]`：每轮对话一条记录，`reused` 字段显式标记**复用自前轮**的资源（不重采/不重算/不计费）
- `drill_tree`：轮次父子关系，用于报告第16章呈现完整追问链
- `cumulative_conclusion`：跨轮累积结论，避免多轮结论互相打架
- `checkpoint`：崩溃恢复锚点

---

## 3. Checkpoint 恢复协议（对齐 LangGraph checkpoint）

1. **写时机**：每个 turn 报告投递成功后，更新 `session_state` 的 `updated_at` 与 `checkpoint.last_completed_turn/step`。
2. **读时机**：新 turn 启动时，orchestrator **先读** `session_state/<session_id>.json`：
   - 存在且 `checkpoint.recoverable=true` → 从 `last_completed_turn` 续做，**不重做已完成轮次**
   - 不存在/损坏 → 视为新 session（创建新 `session_id`），并在本轮标注「无历史会话状态」
3. **崩溃重启**：无需从头执行，加载 `session_state` 复用已采 provenance、已算 variables、已审经验，仅重跑失败的那一步。
4. **状态隔离**：不同 `task_id` 不共享状态；同一 `session_id` 跨多次 `deliver_attachments` 累积。

---

## 4. 多轮下钻追问协议（orchestrator 执行）

识别下钻意图（用户追问含「展开/深入/对比竞品/为什么/再看看XX/把XX部分展开/下钻」等）：

```
Step D1 加载会话：读取 session_state[session_id]，获得 turns[] / drill_tree / cumulative_conclusion
Step D2 判定范围：解析本轮 focus（新增模块/子问题），与历史 turns 比对去重
Step D3 复用不重采：
   - 历史 provenance_refs 覆盖的数据 → 直接引用，不重新 AnySearch/AkShare
   - 历史 variable_refs 覆盖的计算 → 直接引用 variables.json，不重算
   - 历史 experience_refs → 回灌本轮分析
Step D4 增量执行：仅对新增范围走标准流程（采数→推导链→反方审计→质量门→可执行推理→工具治理）
Step D5 挂树+累积：append turns[]（带 parent_turn + reused），更新 drill_tree 与 cumulative_conclusion
Step D6 续写报告：终稿反映完整问题链（见第5节第16章）
```

**关键约束**：下钻轮**不得**推翻前轮已通过质量门的结论，除非新证据触发反方审计 P0；若需修正，须在报告「对抗性审计与回应」章节标注修正依据。

---

## 5. 报告交付：第16章「多轮下钻与会话状态」

- **仅多轮会话强制**（turns.length > 1）：报告须含第16章，列：
  - `session_id` 与总轮次
  - **问题树（drill_tree）**：文本化父子轮次，如「T1 全维度研判 → T2 宏观下钻（白酒景气）」
  - 每轮：焦点（focus）+ 增量结论（conclusion_delta）+ 复用清单（reused：哪些 provenance/variable 被复用未重采）
  - 跨轮累积结论（cumulative_conclusion）
- **单轮会话豁免**：报告须显式声明「本报告为单轮一次性产出，无多轮下钻」，放行。
- 第九道 fail-closed 校验 `check-stateful-drilldown.sh` 据此拦截（见下）。

---

## 6. 与既有八道护栏协同（不绕过、可累积）

| 护栏 | 多轮下钻中的处理 |
|------|----------------|
| ① provenance 快照 | 下钻**新采**数据仍须快照锚定；复用旧 provenance 不重采、不重存 |
| ② 推导链 | 续链：新轮引用前轮 `variable_refs`，不重算；新增计算须独立成链 |
| ③ 反方审计 | 每轮终稿均过；修正前轮结论须触发 P0 回应 |
| ④ 自评估质量门 | 每轮终稿均过 |
| ⑤ 流程韧性 | 下钻的 retry/fail/degraded 同步 `resilience_log`（不重复造事件） |
| ⑥ 可执行推理 | 下钻**新增**定量计算须走 Code Agent；复用旧 `variables.json` 不重算 |
| ⑦ 经验沉淀 | 每轮均可沉淀，回灌 `experience/` 与下轮 `experience_refs` |
| ⑧ 工具治理 | 下钻**新调用**经治理层审计（`session_id` 写入 `tool_calls.jsonl`）；复用调用不重复计费 |

**降级处置**：`session_state` 文件不可用/损坏 → best-effort，不阻塞投递；本轮按单轮处理，并在第16章（或单轮声明处）标注「会话状态文件不可用，无法续接历史上下文，本轮按单轮处理」。状态文件写入失败不触发任何 fail-closed 拦截。

---

## 7. 第九道 fail-closed 校验（check-stateful-drilldown.sh）

脚本逻辑（skill 与 workspace 双副本，chmod +x）：

1. 判定是否多轮：报告含「第16章 多轮下钻与会话状态」「多轮下钻」「下钻追问」「第N轮」等标记，或 frontmatter `session_turns>1`。
2. **多轮** → 须含「多轮下钻与会话状态」章节且 ≥1 问题树/迭代条目（含 turn 编号 + 焦点 + 增量结论），否则 `ok:false` 拦截。
3. **单轮** → 须显式含「单轮一次性产出，无多轮下钻」声明，否则 `ok:false` 拦截。
4. 空章节（有标题无内容）→ `ok:false` 拦截。

> 与前八道一致：强制章节 + 单轮豁免声明，fail-closed 不投递。
