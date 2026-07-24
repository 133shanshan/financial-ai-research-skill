# 流程韧性规范（Flow Resilience, v3.3.0）

> 本文件定义「金融AI投研」Skill 在子代理调用与数据获取失败时的重试、错误恢复与降级策略。
> 核心原则：降级而非崩溃（Degrade, don't crash）——任何单点失败都不得中断整体研究流程。
> 对标：mcp-finance-agent（LangGraph + Guardrails）的错误重试 ≤3 次 + LLM-as-Judge 护栏节点设计（调研方案 G2 / 标杆表）。

---

## 一、重试策略（Retry Policy）

适用于以下易失败操作，统一上限 ≤3 次，指数退避（2s / 4s / 8s；PDF 转换仅退避 1 次）：

| 操作 | 失败判定 | 重试上限 |
|------|----------|----------|
| 子代理调用（Agent / SendMessage 回传） | 超时、异常抛出、返回空 JSON、缺必需字段、hitl_required 未处理 | 3 次 |
| 数据获取（AnySearch / AkShare / Bash 执行） | 网络错误、空结果、接口 4xx/5xx、解析失败 | 3 次 |
| PDF 转换（docx2pdf / LibreOffice） | 转换异常、返回非 PDF | 1 次 |
| 审计 / 质量门子代理 | 同子代理调用 | 3 次 |

退避规则：第 1 次重试前等待 2s，第 2 次 4s，第 3 次 8s；每次重试须更换参数或换备用数据源（如 AkShare 失败改用 AnySearch）。

---

## 二、错误恢复节点（Checkpoint / Recovery Node）

编排流程每步设 checkpoint，失败可回退到最近 checkpoint 重做该步，而非从头开始：

    Step1 团队创建 ─┐
    Step2 任务分解  │ checkpoint
    Step3 子代理派发 ─┤（失败回退到此重派，不重建团队）
    Step4 结果汇总   │
    Step4.5 审计     ├─ checkpoint（失败回退重跑，不重做前序分析）
    Step4.6 质量门   │
    Step5 报告生成   ┘

- 若 TeamCreate 损坏（团队丢失），优先 TeamCreate 重建再续跑后续步；已完成的子代理结果若存于临时文件 / JSON，可读取复用，避免重复计算。
- 每次重试 / 回退都记入 resilience_log（见第四节）。

---

## 三、降级策略矩阵（Degradation Matrix）

重试耗尽后仍失败，按以下矩阵降级完成而非崩溃：

| 失败场景 | 降级处置 | 报告标注 |
|----------|----------|----------|
| 单个分析师子代理全失败 | 该维度标注「分析降级 / 数据缺失」，跳过该维度继续 | 第 12 章「流程韧性声明」 |
| 多个 / 全部子代理失败 | 降级为 orchestrator 单智能体串行执行（按各 methodology 自做） | 标注「Agent Teams 子代理失败，已降级为单智能体模式」 |
| Agent Teams 启动失败 | 直接单智能体模式 | 同上 |
| 数据获取失败 | 标注「数据缺失」，用可得替代源（须显式标注来源）或定性推断（须显式标注「推断，非数据」） | 第 12 章 + 数据来源框 |
| 审计 / 质量门子代理失败 | 降级为 orchestrator 自审（严格按 adversarial-auditor.md / quality-judge.md 规则自评） | 标注「自动审计 / 质量门降级为自审」 |
| PDF 转换失败 | 投递 .docx，标注原因 | 封面 / 交付说明 |

降级红线：降级只改变完成方式，不得降低四道 fail-closed 校验门槛——provenance / 推导链 / 反方审计 / 自评估质量门照常拦截。降级后更应强化来源标注（数据缺失须显式声明，不得伪装为已验证数据）。

---

## 四、resilience_log 与报告「流程韧性声明」章节

- orchestrator 维护 resilience_log（列表），每项：

    - event: 子代理超时 / 数据缺失 / PDF转换失败 / 审计降级
    - module: 宏观 / 行业 / ...（或 N/A）
    - retry_count: 0
    - final_disposition: 重试成功 / 降级跳过 / 单智能体模式 / 自审
    - impact_on_conclusion: 无影响 / 某维度缺失，推荐置信度下调至 X / ...

- report-writer 在 Step 4.7 接收 resilience_log，写入报告第 12 章「流程韧性声明」：
  - 有事件 → 逐条列出上表字段；
  - 无事件 → 声明「本次研究全流程未触发重试或降级」。
- check-resilience-declaration.sh 为第五道 fail-closed 校验：报告必须含「流程韧性声明」章节，否则拦截投递。

---

## 五、与既有护栏的协同

流程韧性是执行层保障，既有的「可信层」（快照锚定 / 推导链 / 反方审计 / 自评估质量门）是质量层保障，二者正交：
- 重试 / 降级不绕过任何质量校验；
- 降级场景下若某维度数据缺失，反而要在报告中更显式地声明不确定性，避免用缺失数据得出强结论。

详细标杆与规划依据见 技能优化方案 / 金融AI投研Skill优化方案_2026趋势调研.md G2 与 P1-5。
