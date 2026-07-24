# Agent Teams 协作规范

> 本文件定义「金融AI投研」Skill中多智能体协作的规范与流程。
> 基于「经管AI智能体设计方法论」的 Agent Teams 架构。

---

## 团队架构

当需要多智能体协作时，按以下角色分工：

| 角色 | 对应文件 | 职责 | 使用场景 |
|------|---------|------|----------|
| **政策分析师** | `agent-prompts/policy-analyst.md` | 货币政策语义分析、政策取向判断 | 模块二 |
| **行业分析师** | `agent-prompts/industry-analyst.md` | 行业基本面研究、竞争格局分析 | 模块四 |
| **宏观分析师** | `agent-prompts/macro-analyst.md` | 宏观数据监控、经济指标解读 | 模块五 |
| **市场分析师** | `agent-prompts/market-analyst.md` | 市场环境分析、全球市场联动 | 模块六 |
| **情绪分析师** | `agent-prompts/sentiment-analyst.md` | 市场情绪扫描、情绪评分 | 模块七 |
| **报告撰写者** | `agent-prompts/report-writer.md` | 整合各分析师输出，生成最终报告 | 所有模块 |
| **对抗审计者** | `agent-prompts/adversarial-auditor.md` | 反方审计，挑战核心论断/数据/推导链，输出 challenges[] | 所有模块（报告交付前置） |
| **质量裁判者** | `agent-prompts/quality-judge.md` | 自评估质量门，三维度打分（定性严谨度/定量准确度/可验证性），输出 quality_gate | 所有模块（报告交付前置，审计之后） |
| **代码执行 Agent（Code Agent）** | `references/code-agent.md` | 统一变量空间执行 Python 计算/图表，登记变量与代码路径，替代 LLM 裸算 | 所有含定量计算/图表的模块（分析阶段+报告阶段） |
| **会话状态管理器（State Manager）** | `references/stateful-drilldown.md` | 跨轮会话状态持久化（session_state）、checkpoint 恢复、多轮下钻复用（已采 provenance/variable 不重采） | 多轮下钻会话（同一 session_id 追问；单轮可省略） |
| **评测基准裁判（Benchmark Judge）** | `references/evaluation-benchmark.md` | 跑内置 benchmark suite 对报告终稿做客观五维度打分（工具调用正确性/数字复算一致性/推导链完整性/来源可追溯性/反方审计回应率），输出 benchmark_score 与 verdict | 所有模块（报告交付前置，质量门之后、经验沉淀之前） |
| **自进化协调员（Evolution Coordinator）** | `references/self-evolution.md` | 交付后汇总质量信号（G8/G5/G4/反方审计）写入 evolution/signals/，提取候选 Skill 补丁（candidate_patches，受控发布+回滚），驱动自进化闭环 | 所有模块（交付后元流程，经验沉淀之后） |
| **投决会主持委员（IC Chair）** | `references/investment-committee.md` | 含投资建议的报告交付前编排五委员（主持/看涨/看跌/中性/风控）对抗决策，强制交叉质询，形成 investment_committee/<delivery_id>.json 决议，决议强约束报告综合建议 | 所有含投资建议的模块（报告交付前置，自进化之前） |

---

## 协作流程

### 标准流程（6步）

```
Step 1: 任务分解
  主Agent接收用户请求
  → 判断需要哪些分析师角色
  → 创建子任务列表
    ↓
Step 2: 并行派发
  同时派发任务给相关分析师Agent
  （政策+宏观 或 行业+市场+情绪）
    ↓
Step 2.5: 会话状态加载（v3.7.0 强制，多轮下钻）
  若用户带入 session_id（追问/下钻场景），读取 session_state/<session_id>.json：
  → 获得历史 turns[] / drill_tree / cumulative_conclusion / checkpoint
  → 比对本次 focus，去重已覆盖模块，标记 reused（复用 provenance/variable 不重采不重算）
  → 从 checkpoint.last_completed_turn 续做，不重做已完成轮次
  → 若无 session_id / 文件损坏：视为新 session，创建 session_state，标注「无历史会话状态」
    ↓
Step 3: 独立分析
  各分析师Agent并行工作
  → 读取对应 methodology 文件
  → 调用 AkShare 获取数据
  → 生成结构化分析结果
    ↓
Step 3.2: 工具治理（v3.6.0 强制，数据采集统一收口）
  所有外部工具/数据调用（AnySearch / AkShare / Bash / Code Agent 等）**必须**经工具治理层统一收口
  → 调用前做参数校验（必填/格式/取值白名单，见 references/mcp-governance.md §4）
  → 每次调用写一条审计记录到 tool_audit/<task_id>/tool_calls.jsonl（call_id/tool/params/provenance_ref/status）
  → 禁止子代理绕过治理层裸调外部 API / 命令行
  → retry/fail/degraded 事件同步一条到 resilience_log，随报告第 12 章交付
  → 治理层不可用则降级采数，并在报告第 15 章标注「工具治理层不可用，本次调用未统一审计」
    ↓
Step 3.5: 可执行推理（v3.4.0 强制，计算/图表必经）
  任何定量计算与图表须由 Code Agent 执行，禁止 LLM 直接"心算"输出数值
  → 在 code_workspace/<task_id>/ 下用统一变量空间运行 Python
  → 所有中间/最终结果登记到 variables.json（变量名/值/单位/来源/代码路径）
  → 图表生成后做视觉校验，标注「（图表已视觉校验：…）」
  → 失败可重试≤3 次；环境不可用则降级为人工/定性估算并登记降级原因
  → 所有变量/代码路径随报告「可执行推理与变量空间」章节交付
    ↓
Step 4: 结果汇总
  主Agent收集所有分析师的输出
  → 检查完整性
  → 解决冲突（如政策取向 vs 市场情绪矛盾）
    ↓
Step 5: 报告生成（草稿）
  调用 report-writer Agent
  → 整合所有分析结果
  → 生成 .docx 草稿并完成 Step 1–4（含 provenance / 推导链校验）
    ↓
Step 5.5: 对抗性审计（v3.1.0 强制）
  调用 adversarial-auditor Agent 对报告草稿发起反方审计
  → 回传 challenges[] 给 report-writer
  → report-writer 完成「对抗性审计与回应」章节（P0/P1 必须修正或回应）
  → verdict=block（存在 P0 且无法回应）时不得进入 Step 6
    ↓
Step 5.7: 自评估质量门（v3.2.0 强制）
  调用 quality-judge Agent 对终稿做三维度打分
  → 回传 quality_gate（qualitative_rigor / quantitative_accuracy / verifiability 各 0-10，weighted_score，verdict）
  → report-writer 完成「自评估质量门」章节
  → verdict=pass 进入 Step 6；verdict=amber 须修订弱项后进入 Step 6；verdict=block 不得进入 Step 6（回炉或人工裁决）
    ↓
Step 5.8: 客观评测基准（v3.8.0 强制）
  调用「评测基准裁判（Benchmark Judge）」对终稿跑 benchmark suite
  → 读取 benchmark/tasks/*.json 的 golden，做客观五维度打分，输出 benchmark_score（0–1）+ verdict（pass/amber/block）
  → report-writer 完成「客观评测与基准得分」章节（第 17 章）；无对应 golden 任务则声明「本报告不纳入客观评测基准」
  → verdict=pass 进入 Step 6；verdict=amber 修订弱项后进入 Step 6；verdict=block 不得进入 Step 6（回炉或人工裁决）
    ↓
Step 5.9: 自进化闭环（v3.9.0 强制，交付后元流程）
  调用「自进化协调员（Evolution Coordinator）」汇总本次交付质量信号
  → 提取 G8 benchmark_score/verdict、G5 quality 三维度、G4 经验卡片、反方审计未回应挑战，写入 evolution/signals/<delivery_id>.json
  → 若发现可复用的 Skill 级缺陷/优化点，生成 evolution/candidate_patches/<patch_id>.json（status=proposed，待人工 review）
  → report-writer 完成「自进化反馈与改进建议」章节（第 18 章）；非标准任务声明「本报告不纳入自进化闭环」
  → 候选补丁从 proposed→applied 须人工确认（HITL），受控发布走 git tag、回归不达标秒级回滚
    ↓
Step 5.10: 投决会对抗决策（v3.10.0 强制，含投资建议时）
  调用「投决会主持委员（IC Chair）」编排五委员对抗决策
  → 看涨/看跌出立场+论据（≥3 条，含 provenance 引用），中性列证据缺口，风控给合规/风险结论
  → 强制交叉质询（看跌逐条回应看涨证据），形成 investment_committee/<delivery_id>.json 决议（verdict+consensus+分歧点+风险预案+dissent）
  → report-writer 完成「投决会对抗决策与决议」章节（第 19 章）；纯研究/无投资建议声明「本报告不纳入投决会对抗决策」
  → 决议 verdict∈{否决,谨慎} 与报告综合建议冲突则升级 orchestrator 人工裁决（HITL）
    ↓
**错误恢复节点（v3.3.0）**：每个 Step 设 checkpoint；任一步失败回退到最近 checkpoint 重做该步（团队损坏则 TeamCreate 重建），不从头。所有重试/降级事件记入 resilience_log，随报告「流程韧性声明」章节交付。详见 `references/resilience.md`。
    ↓
Step 6: Human-in-the-Loop
  展示报告给用户输入
  → 等待用户确认
  → 根据用户反馈调整（如需）
    ↓
Step 6.5: 经验沉淀（v3.5.0 强制，交付后动作）
  本次研究 deliver 后，将可复用经验具体化为三类卡片（对齐 Agentar 经验→Skills）
  → 避坑清单：append 到 experience/lessons-learned.md
  → 标的研判模板：写 experience/asset-templates/<标的>.md
  → 行业框架：写 experience/industry-frameworks/<行业>.md
  → 报告须含第 14 章「经验沉淀与复用」（列卡片或声明「本次无新增可复用经验」）
  → 写入失败降级为 best-effort，标注于第 14 章，不阻塞投递
  → 经验卡片供下次「知识库加载/历史案例检索」回灌复用
```

---

## 冲突解决规则

当不同分析师的结论冲突时，按以下优先级处理：

| 优先级 | 冲突类型 | 处理方式 |
|--------|----------|----------|
| P0 | 政策取向 vs 市场情绪矛盾 | 以**政策取向**为准（A股政策市特征） |
| P1 | 宏观数据 vs 行业数据矛盾 | 以**宏观数据**为准（自上而下原则） |
| P2 | 短期情绪 vs 长期趋势矛盾 | 标注矛盾，提示用户关注 |
| P3 | 不同数据源差异 | 标注差异，提供多源对比 |

**示例**：
- 政策取向：宽松（+0.5）
- 市场情绪：恐慌（-0.6）
- **结论**：政策底已现，但市场情绪尚未修复，建议观望等待情绪触底反弹信号。

**对抗审计（adversarial-auditor）严重度处置**：复用上述 P0–P3 分级——P0 必须修正结论或移除推荐并拦截交付；P1 必须补充反向证据或下调置信度；P2/P3 标注提示用户。挑战记录随报告「对抗性审计与回应」章节交付。详见 `agent-prompts/adversarial-auditor.md` 与 `report-writer.md` Step 4.5。

**自评估质量门（quality-judge）放行裁决**：对终稿做三维度打分（定性严谨度 / 定量准确度 / 可验证性，权重 0.34/0.33/0.33）。`verdict=pass`（三维度均≥8 且加权≥8）→ deliver；`verdict=amber`（存在维度 5–7 或加权 6–8，无 block 条件）→ revise 修订弱项后 deliver；`verdict=block`（任一维度<5 或 可验证性<7 或 审计 P0 未回应）→ hold 不得送达，回炉或人工裁决。评分随报告「自评估质量门」章节交付。详见 `agent-prompts/quality-judge.md` 与 `report-writer.md` Step 4.6。

**流程韧性声明（resilience，v3.3.0）**：orchestrator 维护 resilience_log（记录本次研究所有触发重试/降级事件）。报告须含第 12 章「流程韧性声明」，逐条列出事件类型/模块/重试次数/最终处置/对结论影响；若全程无失败，声明「全流程未触发重试或降级」。降级只是「换方式完成」，**不绕过**四道 fail-closed 校验（provenance / 推导链 / 反方审计 / 自评估质量门）。详见 `references/resilience.md` 与 `report-writer.md` Step 4.7。

**可执行推理裁决（code-agent，v3.4.0）**：报告中的每一项定量主张（收益率/估值/占比/指标值等）必须能映射到 `code_workspace/<task_id>/variables.json` 一项（变量名+数值+代码引用），否则视为「散文式计算」不准交付；每张图表须有「（图表已视觉校验：…）」标注。若任务为纯定性分析（无定量计算），报告须显式声明「本报告为定性分析，未含代码执行计算」且跳过变量空间章节。执行环境不可用则降级为人工/定性估算并在第 13 章登记降级原因，**降级不绕过**第六道 fail-closed 校验（check-code-agent.sh）。详见 `references/code-agent.md` 与 `report-writer.md` Step 4.4 / 第 13 章。

**经验沉淀裁决（experience，v3.5.0）**：每次研究交付后须沉淀可复用经验——避坑清单（append `experience/lessons-learned.md`）、标的研判模板（`experience/asset-templates/<标的>.md`）、行业框架（`experience/industry-frameworks/<行业>.md`），并在报告第 14 章「经验沉淀与复用」列卡片或声明「本次无新增可复用经验」；缺失第 14 章或章节为空触发第七道 fail-closed 校验（check-experience-deposition.sh）拦截。经验卡片供下次「知识库加载/历史案例检索」回灌复用，高价值者经 `SkillManage` 提升为正式 Skill。写入失败降级为 best-effort（第 14 章标注），不阻塞投递。详见 `references/experience-deposition.md` 与 `report-writer.md` Step 4.8 / 第 14 章。

**工具治理裁决（mcp-governance，v3.6.0）**：所有外部工具/数据调用（AnySearch / AkShare / Bash / Code Agent）必须经工具治理层统一收口（参数校验 + 调用审计到 `tool_audit/<task_id>/tool_calls.jsonl`），禁止裸调；报告第 15 章「工具治理与调用审计」须列全部 call_id + tool + 归一化参数 + provenance 引用 + status，或显式声明「本报告未调用任何外部工具或数据源」。治理层不可用则降级采数并在第 15 章标注「工具治理层不可用，本次调用未统一审计」+ best-effort 补记调用清单，**降级不绕过**第八道 fail-closed 校验（check-mcp-governance.sh）。治理层 retry/fail/degraded 事件同步 resilience_log，不重复造事件。详见 `references/mcp-governance.md` 与 `report-writer.md` Step 4.9 / 第 15 章。

**会话状态裁决（stateful-drilldown，v3.7.0）**：多轮下钻会话（同一 session_id 追问）须维护 `session_state/<session_id>.json`——每轮 append turns[]（带 parent_turn + reused 复用标记）、更新 drill_tree 与 cumulative_conclusion，报告投递后写 checkpoint（last_completed_turn/step）以支持崩溃恢复。报告第 16 章「多轮下钻与会话状态」须列 session_id、问题树、每轮焦点+增量结论+复用清单、跨轮累积结论；**单轮会话**须显式声明「本报告为单轮一次性产出，无多轮下钻」。缺失对应章节/声明触发第九道 fail-closed 校验（check-stateful-drilldown.sh）拦截。会话状态文件不可用则降级为 best-effort（本轮按单轮处理并在第 16 章标注），不阻塞投递。详见 `references/stateful-drilldown.md` 与 `report-writer.md` Step 4.10 / 第 16 章。

**评测基准裁决（evaluation-benchmark，v3.8.0）**：所有标准评测任务交付前须跑客观五维度基准——工具调用正确性 / 数字复算一致性 / 推导链完整性 / 来源可追溯性 / 反方审计回应率，输出 `benchmark_score`（0–1）与 verdict。`verdict=pass`（≥0.80）→ 写入报告第 17 章「客观评测与基准得分」并送达；`verdict=amber`（0.60–0.80，无 block 条件）→ 修订弱项后写入第 17 章并送达；`verdict=block`（<0.60）→ 拦截交付、回炉或人工裁决。报告第 17 章须列 benchmark_score + 五维度分 + 权重 + verdict + 任务引用，或显式声明「本报告不纳入客观评测基准」；缺失第 17 章或章节为空触发第十道 fail-closed 校验（check-evaluation-benchmark.sh）拦截。无对应 golden 任务/运行环境不可用则降级为 best-effort（第 17 章声明），不阻塞投递。详见 `references/evaluation-benchmark.md` 与 `report-writer.md` Step 4.11 / 第 17 章。

**自进化裁决（self-evolution，v3.9.0）**：每次标准评测任务交付后须发射 evolution signals 并写入 `evolution/signals/<delivery_id>.json`，报告第 18 章「自进化反馈与改进建议」须列信号摘要（benchmark_score+verdict、quality 三维度、经验卡片数、未回应挑战数）+（≥1 改进建议条目，或显式声明「本次无新增改进建议」）；非标准任务须显式声明「本报告不纳入自进化闭环」。缺失第 18 章或章节为空触发第十一道 fail-closed 校验（check-self-evolution.sh）拦截。候选补丁（candidate_patches）须经人工 review（proposed→approved→applied），受控发布走 git tag、regression_guard 不达标（benchmark_score<0.60）即 `git checkout` 秒级回滚；自进化是交付后元流程，不修改正文十道校验门槛。详见 `references/self-evolution.md` 与 `report-writer.md` Step 4.12 / 第 18 章。

**投决会裁决（investment-committee，v3.10.0）**：含投资建议的报告交付前须跑投决会对抗决策——五委员（主持/看涨/看跌/中性/风控）对抗，强制交叉质询，形成决议（verdict∈{强力推荐/推荐/中性/谨慎/否决}+consensus 0–1+主要分歧点+风险预案+dissent）。verdict=强力推荐/推荐 → 写第 19 章「投决会对抗决策与决议」并作为报告综合建议的强约束；verdict=中性 → 写入并说明；verdict=谨慎/否决 → 与报告综合建议冲突须复核或升级 HITL。报告第 19 章须列委员立场+决议（verdict+共识度）+（风险预案 或 「无委员立场记录」声明）；纯研究/无投资建议须显式声明「本报告不纳入投决会对抗决策」；缺失第 19 章或空章节触发第十二道 fail-closed 校验（check-investment-committee.sh）拦截。决议 consensus/verdict 作为新质量信号维度进入 G9 evolution signals。详见 `references/investment-committee.md` 与 `report-writer.md` Step 4.13 / 第 19 章。

---

## 任务派发模板

### 派发给政策分析师
```
角色：政策分析师
任务：分析 YYYY年MM月 货币政策取向
输入：
  - 中央政治局公报（如有）
  - 货币政策委员会例会通告
  - 最新LPR报价
输出要求：
  - 语义分：-1.0 ~ +1.0
  - 关键词提取（宽松/中性/收紧）
  - 对A股影响分析（1-2段）
```

### 派发给行业分析师
```
角色：行业分析师
任务：分析 {行业名称} 基本面
输入：
  - 行业ETF代码（如有）
  - 重点公司列表
输出要求：
  - TAM/SAM/SOM 测算
  - 竞争格局（CR4/CR8）
  - 波特五力分析
  - 投资建议（买入/持有/卖出）
```

### 派发给报告撰写者
```
角色：报告撰写者
任务：整合分析结果，生成 {报告名称}
输入：
  - 各分析师的输出文件
  - 用户原始需求
输出要求：
  - .docx 格式
  - 按照输出格式规范（标题层级、表格样式）
  - 附免责声明
```

---

## 性能优化

### 并行执行原则
- **可并行**：政策分析 + 宏观分析、行业分析 + 市场分析
- **必须串行**：数据获取 → 分析 → 报告生成

### Token 优化
- 各分析师输出**只返回结构化摘要**（不超过500字）
- 详细分析存到临时文件，由报告撰写者读取
- 避免在大模型之间传递大量原始数据

---

## 错误处理（流程韧性，v3.3.0）

> 核心原则：**降级而非崩溃（Degrade, don't crash）**。任何单点失败不得中断整体研究流程。详见 `references/resilience.md`。

| 错误类型 | 重试策略（≤3 次，指数退避） | 降级处置 |
|----------|------------------------------|----------|
| 分析师Agent超时/异常/空结果 | 重试≤3 次（2s/4s/8s），仍失败 | 该维度标注"分析降级"跳过，或降级为单智能体串行执行 |
| 数据获取失败（AnySearch/AkShare） | 重试≤3 次，仍失败 | 标注"数据缺失"，用可得替代源（须显式标注）或定性推断，继续其他维度 |
| 子代理派发失败 | 重建 Agent 重试≤3 次 | 降级为 orchestrator 单智能体模式 |
| 审计/质量门子代理失败 | 重试≤3 次，仍失败 | 降级为 orchestrator 自审（按 adversarial-auditor/quality-judge 规则自评），标注"自动审计/质量门降级为自审" |
| 输出格式错误 | 主Agent负责格式化（不计入重试） | 主Agent修正，不要求分析师重出 |
| PDF 转换失败 | 重试≤1 次，仍失败 | 投递 .docx，标注原因 |
| 代码执行环境失败（Python 缺失/沙箱受限/包未装） | 重试≤3 次（2s/4s/8s），仍失败 | 降级为人工/定性估算，在第 13 章登记降级原因；不得伪装为代码执行结果 |
| 经验卡片写入失败（无权限/磁盘满/沙箱限制） | 不重试（best-effort） | 不阻塞投递；在第 14 章标注「经验卡片文件写入失败，已留文本记录于本报告」 |
| 工具治理层不可用（无法统一收口审计） | 不重试（降级采数） | 子代理仍可采数据，第 15 章标注「工具治理层不可用，本次调用未统一审计」+ best-effort 补记调用清单；不阻塞投递 |
| 会话状态文件不可用/损坏（session_state 读取/写入失败） | 不重试（best-effort） | 本轮按单轮处理，第 16 章（或单轮声明处）标注「会话状态文件不可用，无法续接历史上下文，本轮按单轮处理」；不阻塞投递 |
| 客观评测基准运行环境不可用（脚本缺失/无 golden 任务/沙箱受限） | 不重试（best-effort） | 第 17 章（或声明处）标注「评测基准运行环境不可用，本次未跑客观评测」；不触发第十道拦截但须明确声明 |
| 自进化基础设施不可用（evolution/ 写入失败/信号采集脚本缺失/沙箱受限） | 不重试（best-effort） | 第 18 章（或声明处）标注「自进化基础设施不可用，本次未发射 evolution signals」；不触发第十一道拦截但须明确声明 |
| 投决会基础设施不可用（角色代理失败/编排超时/沙箱受限） | 不重试（best-effort） | 第 19 章（或声明处）标注「投决会基础设施不可用，本次未跑对抗决策」；不触发第十二道拦截但须明确声明 |

---

*本文件为 Agent Teams 协作的顶层规范，具体每个角色的 prompt 详见 `agent-prompts/` 目录。*