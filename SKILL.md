---
name: 金融AI投研
version: 3.18.0
description: |
  顶级金融AI投研 Agent Teams 框架（多智能体并行架构），整合九大模块：AI投资大师智能体（模块一）、
  AI货币政策语义分析（模块二）、国信AI资配框架（模块三）、
  行业基本面研究（模块四）、宏观数据监控（模块五）、
  市场环境分析（模块六）、市场情绪脉搏（模块七）、
  顶级基金深度分析（模块八）、策略回测引擎（模块九）。
  采用 Agent Teams 多智能体并行架构，覆盖：多智能体A股选股、央行政策文本AI解读、多元周期资产配置、
  行业/竞品/客户结构化研究、每日宏观数据监控推送、
  全球市场环境评估、个股/板块情绪扫描、公募基金/私募基金/ETF深度分析。
  输出格式：PDF（顶级券商研报标准）。v3.1.0 新增「可信层」：来源快照+字符锚定（provenance）、证据→计算→结论推导链、对抗性反方审计（adversarial-auditor）；v3.2.0 新增「自评估质量门」（quality-judge 三维度打分：定性严谨度/定量准确度/可验证性，不达标不送达）；v3.3.0 新增「流程韧性」（子代理/数据失败自动重试≤3次+错误恢复节点+降级矩阵，降级而非崩溃，报告第12章「流程韧性声明」标注曾触发重试/降级）；v3.4.0 新增「可执行推理」（Code Agent 统一变量空间执行 Python 计算/图表，定量主张须映射 variables.json，图表须视觉校验，替代 LLM 裸算，报告第13章「可执行推理与变量空间」交付，第六道 fail-closed 校验 check-code-agent.sh 拦截散文式计算）；v3.5.0 新增「经验沉淀」（每次研究后自动产出可复用知识卡片——避坑清单/标的研判模板/行业框架，写入 experience/ 并回灌下次研究，报告第14章「经验沉淀与复用」，第七道 fail-closed 校验 check-experience-deposition.sh 拦截空洞沉淀，对齐 Agentar 经验→Skills）；v3.6.0 新增「工具治理中心」（MCP 范式，把 AnySearch/AkShare/Bash/Code Agent 等所有外部调用统一收口到治理层做参数校验+调用审计 tool_audit/<task_id>/tool_calls.jsonl+可重现，对齐 AlphaTeam 工具治理中心，报告第15章「工具治理与调用审计」，第八道 fail-closed 校验 check-mcp-governance.sh 拦截未统一审计）；v3.7.0 新增「状态化多轮下钻」（同一会话下钻追问上下文累积不丢，LangGraph checkpoint 思路：session_state/<session_id>.json 持久化+checkpoint 恢复+复用已采 provenance/已算 variables 不重采不重算，报告第16章「多轮下钻与会话状态」，第九道 fail-closed 校验 check-stateful-drilldown.sh 拦截无状态会话）。交付前十三道 fail-closed 校验（provenance/推导链/反方审计/自评估质量门/流程韧性声明/可执行推理/经验沉淀/工具治理/多轮下钻/客观评测基准/自进化闭环/投决会对抗决策/非结构化知识回流），对接真实市场可审计、可重现、可累积、可追溯、可续接。v3.8.0 新增「客观评测基准」（内置 benchmark suite 五维度客观打分，对齐 FinToolBench/iRaB；与 quality-judge 主观自评估双轨并行，第十道 fail-closed 校验 check-evaluation-benchmark.sh 拦截未达标/未声明）。v3.9.0 新增「自进化闭环」（交付后汇总 G8/G5/G4/反方审计质量信号写入 evolution/signals/，提取候选 Skill 补丁受控发布+秒级回滚，对齐 Hermes 五阶段+蚂蚁受控发布；报告第18章「自进化反馈与改进建议」，第十一道 fail-closed 校验 check-self-evolution.sh 拦截未发射信号/未声明）。v3.10.0 新增「投决会对抗决策」（含投资建议的报告交付前跑五委员对抗决策——主持/看涨/看跌/中性/风控，强制交叉质询，形成 investment_committee/<delivery_id>.json 决议并强约束报告综合建议，对齐组织级投决会；报告第19章「投决会对抗决策与决议」，第十二道 fail-closed 校验 check-investment-committee.sh 拦截未跑对抗决策/未声明）。v3.11.0 新增「非结构化知识回流」（经 agent-mail 连接器摄取投研相关邮件——路演纪要/研报推送/客户与内部沟通/会议邀请附件，抽取可复用知识卡片写入 experience/ 并回灌下次研究；agent-mail 未开通/无匹配邮件则降级声明不阻塞，复用 G4 经验沉淀体系；报告第20章「非结构化知识回流」，第十三道 fail-closed 校验 check-knowledge-ingestion.sh 拦截未摄取/未声明）。
  v3.12.0 新增「复杂度分级执行」（references/tiering.md）：按 T1 轻量/T2 标准/T3 完整 分档，仅控制是否拉起反方审计/投决会/benchmark/自进化/知识回流等昂贵 agent 流程，廉价结构校验照常，十三道 fail-closed 门槛不变。v3.12.1 把 G4→OB 经验同步通道升级为多源（对话/其他 skill/全局 self-improve 均可同步），零 LLM 增量去重。v3.13.0 深化省 token：②模块引用惰性加载（methodology 不再随 skill 加载全量注入，执行时按需 Read）③每章节 token 预算+紧模板 ④动态 agent 选择（按 tier+问题域裁剪并行 agent 数）⑤provenance 轻量锚定（T1/T2 仅存被引片段快照）⑥结果缓存复用（同标的/同域近期结论跨会话复用，不重跑 agent）；十三道 fail-closed 门槛一个不降，T3 完整档行为同 v3.12.1。  v3.14.0 去个人化与可移植（config 外置 gitignored，OB_VAULT 配置，详见 config.local.example.json）。v3.15.0 补齐发布工程（README / LICENSE / CI 烟雾测试）。v3.16.0 独立基准验证 D1（fail-closed 攻击召回率 6/6=100%，tests/attack_suite.py，接入 CI）。v3.17.0 独立基准验证 D2（推导链逻辑正确性攻击召回率 4/4=100%，tests/derivation_suite.py，内置 3 题已知答案题集供 LLM 判分，接入 CI）。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Skill
  - Agent
  - TeamCreate
  - TeamDelete
  - TaskCreate
  - TaskUpdate
  - TaskList
  - SendMessage
  - deliver_attachments
  - anysearch
  - Agent
  - TeamCreate
  - TeamDelete
  - TaskCreate
  - TaskUpdate
  - TaskList
  - SendMessage
  - deliver_attachments
references:
  - ${CLAUDE_SKILL_DIR}/references/akshare-api.md
  - ${CLAUDE_SKILL_DIR}/references/agent-teams.md
  - ${CLAUDE_SKILL_DIR}/references/knowledge-base-guide.md
  - ${CLAUDE_SKILL_DIR}/references/common-errors.md
  - ${CLAUDE_SKILL_DIR}/references/disclaimer-sources.md
  - ${CLAUDE_SKILL_DIR}/references/indicators.md
  - ${CLAUDE_SKILL_DIR}/references/report-structure.md
  - ${CLAUDE_SKILL_DIR}/references/resilience.md
  - ${CLAUDE_SKILL_DIR}/references/code-agent.md
  - ${CLAUDE_SKILL_DIR}/references/experience-deposition.md
  - ${CLAUDE_SKILL_DIR}/references/mcp-governance.md
  - ${CLAUDE_SKILL_DIR}/references/stateful-drilldown.md
  - ${CLAUDE_SKILL_DIR}/references/evaluation-benchmark.md
  - ${CLAUDE_SKILL_DIR}/references/self-evolution.md
  - ${CLAUDE_SKILL_DIR}/references/investment-committee.md
  - ${CLAUDE_SKILL_DIR}/references/module-index.md  # 模块索引：methodology 改为按需 Read，不随 skill 加载全量注入
  - ${CLAUDE_SKILL_DIR}/references/execution-rules.md
  - ${CLAUDE_SKILL_DIR}/references/references-list.md
---

## 版本与版本管理（git）

本 skill 使用 **git** 做版本管理，**不使用 `_bak_*` 复制备份**。版本演进链如下：

- git 自 **v3.1.0** 起启用：每次功能升级都对应一个 commit，并打 tag `v3.x.0`。
- **v3.0.0 为 pre-git 基线**：原始文件在制定 v3.1.0 前已存在，未纳入 git；其"原始状态"已无独立快照留存，无法用 git 回退到纯 v3.0.0。
- 当前最新版本：**v3.13.0**（在 v3.12.1 基础上深化省 token：模块引用惰性加载 / 每章节 token 预算+紧模板 / 动态 agent 选择 / provenance 轻量锚定 / 结果缓存复用；十三道 fail-closed 门槛一个不降，T3 完整档行为同 v3.12.1）。

**回退命令**（在 skill 根目录执行）：`git -C <skill根目录> checkout v3.x.0`

**审计要点**：v3.1.0 起的任意版本均可精确重现与回退；十三道 fail-closed 校验闸门保证输出可审计、可重现、可追溯。

## 依赖 Skills

- **AnySearch（强制，实时搜索必须用）**：需要实时行情、新闻、宏观数据、政策公告时，**必须**先调用 AnySearch skill 获取数据，再进行金融分析。**禁止使用 WebSearch/WebFetch 直接搜索**，必须用 AnySearch。
  - 触发场景：查实时股价、基金净值、最新CPI/PMI、央行公告、财经新闻情绪、产业链数据、供应链信息
  - 调用方式：`Skill` 工具，skill 参数填 `anysearch`
  - **大公司产业链分析时**：必须用 AnySearch 搜索各子公司、各供应链环节的详细数据，不能只搜母公司概况
- **akshare-data**：历史行情、财务数据、基金历史净值，优先用 AkShare；实时或当日数据用 AnySearch。
- **hv-analysis**（横纵分析法）：当用户要求**生成深度研究报告**、**对某公司/行业/产品做全面分析**、或金融分析结果需要**更深度的叙事和洞察**时，调用 hv-analysis skill。触发场景：
  - 用户说"出一份研究报告""深度分析""横纵分析""完整研究""对比研究"
  - 金融分析结果需要更完整的纵向叙事（发展历程）和横向对比（竞品/同行）
  - 需要产出 PDF 格式的深度研究报告（而非简短的分析结论）
  - 研究对象是具体公司、产品、或金融概念，需要追时间深度+同期广度
  - **大公司必须做完整产业链分析**：研究对象为NVIDIA/台积电/苹果/谷歌等大型复杂公司时，必须分析到具体子公司、子产业的**完整产业链**，不能只写概况；纵向分析要覆盖关键子公司/事业部的完整发展历程
  - **调用方式**：直接调用 `Skill` 工具，skill 参数填 `hv-analysis`
  - **数据来源要求（强制传入）**：调用时必须向 hv-analysis 明确指定：
    > "数据截止日期必须放在报告封面最显眼位置（红色加粗）；第2页必须设独立数据来源框，按权威程度排序列出所有数据源；所有数据/引述必须标注来源和获取时间；最终必须输出投资建议章节（核心推荐/次级推荐/观望三档），给出精准简洁的买入/持有/观望操作建议。"
- **ima-skills**（浑水调研知识库）：需要**行业深度研究、公司调研、外资研报观点**时，先调用 ima-skills 搜索浑水调研知识库（KB ID: `7297249738490228`）。触发场景：
  - 用户说"查一下浑水有没有关于XX的研究""浑水调研""外资研报"
  - 行业研究（模块四）需要高质量电话会总结和外资行观点
  - 公司深度分析需要产业专家交流和卖方电话会记录
  - 需要华为韬定律、半导体产业链、AI算力等专题解读
  - **调用方式**：先调用 `Skill` 工具，skill 参数填 `ima-skills`，然后在对话中指定搜索浑水调研知识库（KB ID: `7297249738490228`）

---
## 输出格式规范

- **默认输出**：PDF（顶级券商研报标准），仅用户明确要求时用 Markdown
- **生成后**：必须使用 `deliver_attachments` 送达用户
- **⚠️ 数据截止日期（强制，必须放在最显眼位置）**：
  - 报告封面：数据截止日期用**红色加粗**标注（>=14pt），紧接标题下方
  - 第2页（封面后第一页）：独立"数据来源框"，列出所有数据源（按权威程度排序），格式为红色标题 + 编号列表
  - 数据来源优先级：官方财报/电话会议实录（审计数据，法律约束） > Jensen Huang等高管公开发言（一手信息） > SemiAnalysis等顶级独立研报（深度分析，第三方推断） > 权威财经媒体（报道和二次加工） > 社交平台讨论
  - 报告中每一处数据/引述，必须在就近位置标注"📊 数据来源：XXX，获取时间：YYYY-MM-DD HH:MM"
- **PDF 生成方式**：先用 python-docx 生成 .docx，再用 LibreOffice 或 docx2pdf 转为 PDF
  - Windows: `pip install docx2pdf` + `from docx2pdf import convert; convert("input.docx", "output.pdf")`
  - 如 docx2pdf 不可用，先生成 .docx，标注"PDF转换失败，暂提供 .docx 版本"
- **投资建议输出（强制）**：报告末尾必须设"最终投资建议"章节，分三档输出：
  - 🎯 核心推荐（立即买入）：列出标的+评级+目标价+上行空间，用表格呈现
  - 📈 次级推荐（逢低布局）：列出标的+逻辑，用列表呈现
  - ⏳ 观望/暂不推荐：列出标的+原因
- **详细格式**：参见 `references/report-structure.md`
- **示例报告**：参见 `references/examples/` 目录（7个模块示例）

---


## Agent Teams 编排执行（核心架构）

本 Skill 采用 **Agent Teams 多智能体并行架构**。当用户请求涉及多维度分析时，必须由 orchestrator（主智能体）启动多个子代理并行执行。

### 触发条件（满足任一条即触发 Agent Teams）

1. 用户请求包含 >=2 个分析维度（如"宏观+行业""政策+情绪""选股+资配"）
2. 用户明确说"深度分析""完整研究""多维度""Agent Teams"
3. 用户请求分析的对象需要多源数据（如"分析茅台股票"→ 需要财报+行业+宏观）
4. 单模块请求但数据量大（如"分析所有A股电网设备公司"）

### Orchestrator 执行流程（必须严格遵守）

**Step 0：复杂度分级（v3.12.0 新增，省 token 核心）**
- 在启动团队/子代理前，先按 `references/tiering.md` 的「分级判定规则」判定本轮 tier（**T1 轻量 / T2 标准 / T3 完整**）。
- 判定后查 `references/tiering.md` 的「流程矩阵」：标 **RUN** 的步骤照常启动 agent / 写完整章节；标 **EXEMPT** 的步骤**跳过对应 agent 启动**，转由 report-writer 在报告中写对应「豁免声明」（check 脚本已接受，见 tiering.md 声明文本）。
- 仅在 T1/T2 显著省 token：跳过反方审计 agent、投决会 5 委员、benchmark、自进化、知识回流邮件抓取等重流程；G1/G2/G4/G5 等廉价结构校验照常。
- 若用户显式点名某流程（如"跑投决会""做对抗审计"），该 gate 强制 RUN，不受 tier 限制。
- 本步骤不改变任何 fail-closed 门槛：被跳过的 gate 由报告写豁免声明，check 脚本据此放行；**T3 完整档行为与本规范引入前（v3.11.0）完全一致**。

**Step 1：创建团队**
```
调用 TeamCreate：
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  description: "金融AI投研多维度分析"
```
→ 自动创建任务列表（Task List）

**Step 2：创建任务（TaskCreate）**
```
根据分析维度创建任务：
  - 政策分析 → Task #1
  - 宏观分析 → Task #2
  - 行业分析 → Task #3
  - 市场分析 → Task #4
  - 情绪分析 → Task #5
  - 报告生成 → Task #6（所有分析完成后）
```

**Step 3：并行启动子代理（关键！必须在同一条消息里调用多次 Agent 工具）**

> **动态 agent 选择（v3.13.0，省 token 核心）**：先按 `references/tiering.md` §五.五「动态 agent 选择矩阵」判定本轮所需 agent——仅拉与问题域相关、且 tier 矩阵为 RUN 的分析师；**不恒拉 9 模块分析师**。
> - T1 且纯常识/记忆可答：不启动任何子代理，orchestrator 直接生成报告并仅跑质量门（1 个轻 agent）。
> - T2：仅拉 1–3 个相关分析师（如纯宏观问题只拉 macro-analyst）。
> - T3：按问题域全量启动对应分析师（行为同 v3.12.1）。
> - 模块 methodology 文件（module1–9）**执行对应维度时按需 Read**，不随 skill 加载全量注入。
> - 用户显式点名 agent/流程 → 强制启动，覆盖矩阵。

> **流程韧性（v3.3.0，强制）**：每个子代理调用须支持自动重试 ≤3 次（指数退避 2s/4s/8s），重试耗尽仍失败则按 `references/resilience.md` 降级矩阵处置（降级而非中断整体流程）。数据获取（AnySearch/AkShare/Bash）同样适用。详见 `references/resilience.md`。
>
> **可执行推理（v3.4.0，强制）**：任何定量计算与图表**必须**由 Code Agent 在 `code_workspace/<task_id>/` 统一变量空间执行 Python，结果登记到 `variables.json`（变量名/值/单位/来源/代码路径）；禁止 LLM 直接"心算"输出数值。图表生成后须做视觉校验并标注「（图表已视觉校验：…）」。详见 `references/code-agent.md`。
>
> **工具治理（v3.6.0，强制）**：所有外部工具/数据调用（AnySearch / AkShare / Bash / Code Agent）**必须**经工具治理层统一收口——调用前参数校验（必填/格式/取值白名单），每次调用写一条审计记录到 `tool_audit/<task_id>/tool_calls.jsonl`（call_id/tool/params/provenance_ref/status），禁止子代理裸调外部 API / 命令行；retry/fail/degraded 事件同步 resilience_log。详见 `references/mcp-governance.md`。
>
> **状态化多轮下钻（v3.7.0，强制）**：同一会话（session_id）下钻追问须维护 `session_state/<session_id>.json`——每轮 append turns[]（含 parent_turn + reused 复用标记），更新 drill_tree 与 cumulative_conclusion，报告投递后写 checkpoint 支持崩溃恢复；下钻轮**复用**历史 provenance/variables 不重采不重算，仅对新增范围增量执行。详见 `references/stateful-drilldown.md`。
>
> **客观评测基准（v3.8.0，强制）**：所有标准评测任务交付前须跑内置 benchmark suite，对报告终稿做客观五维度打分（工具调用正确性/数字复算一致性/推导链完整性/来源可追溯性/反方审计回应率），输出 benchmark_score 与 verdict；与 quality-judge 主观自评估双轨并行，任一 block 即拦截。详见 `references/evaluation-benchmark.md`。
> **自进化闭环（v3.9.0，强制）**：每次交付后须汇总质量信号（G8 benchmark_score/verdict、G5 quality 三维度、G4 经验卡片、反方审计未回应挑战）写入 `evolution/signals/<delivery_id>.json`，报告第18章「自进化反馈与改进建议」列信号摘要+（≥1 改进建议 或 「本次无新增改进建议」声明）；非标准任务声明「本报告不纳入自进化闭环」。候选补丁经 git tag 受控发布、回归不达标秒级回滚。详见 `references/self-evolution.md`。
> **投决会对抗决策（v3.10.0，强制）**：含投资建议的报告交付前须跑五委员对抗决策（主持/看涨/看跌/中性/风控），强制交叉质询，形成决议（verdict+consensus+分歧点+风险预案）并强约束报告综合建议；与 G3 反方审计协同、决议共识度进入 G9 信号。详见 `references/investment-committee.md`。
>
> **非结构化知识回流（v3.11.0，强制）**：经 agent-mail 连接器摄取投研相关邮件（路演纪要/研报推送/客户与内部沟通/会议邀请附件），抽取可复用知识卡片写入 `experience/` 并回灌下次研究；agent-mail 未开通/无匹配邮件则降级声明不阻塞。与 G4 经验沉淀协同（复用同一 `experience/` 体系）、新卡片进入 G9 信号。详见 `references/g11-knowledge-ingestion.md`。

```
Agent 工具调用1：
  name: "policy-analyst"
  subagent_type: "general-purpose"
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  prompt: "你是政策分析师，读取 references/agent-prompts/policy-analyst.md，分析最新货币政策取向，输出JSON结果后通过 SendMessage 发回给 orchestrator。"
  run_in_background: true

Agent 工具调用2：
  name: "macro-analyst"
  subagent_type: "general-purpose"
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  prompt: "你是宏观分析师，读取 references/agent-prompts/macro-analyst.md，拉取最新宏观数据，输出JSON结果后通过 SendMessage 发回给 orchestrator。"
  run_in_background: true

Agent 工具调用3：
  name: "industry-analyst"
  subagent_type: "general-purpose"
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  prompt: "你是行业分析师，读取 references/agent-prompts/industry-analyst.md，分析{行业名称}，输出JSON结果后通过 SendMessage 发回给 orchestrator。"
  run_in_background: true

Agent 工具调用4：
  name: "sentiment-analyst"
  subagent_type: "general-purpose"
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  prompt: "你是情绪分析师，读取 references/agent-prompts/sentiment-analyst.md，分析{板块/股票}市场情绪，输出JSON结果后通过 SendMessage 发回给 orchestrator。"
  run_in_background: true
```

**Step 4：等待子代理结果**

> 收到结果后先解析；若某子代理超时/失败（重试已耗尽），**不要中断整体流程**——按 `references/resilience.md` 降级矩阵将该维度标注为「分析降级/数据缺失」后跳过，继续汇总其余维度。所有降级事件记入 resilience_log（字段见 resilience.md 第四节）。
```
收到 SendMessage 消息后：
  1. 解析 JSON 结果
  2. 调用 TaskList 确认所有任务完成
  3. 如有 HITL 节点（hitl_required=true），暂停并展示给用户确认
  4. 按 agent-teams.md 中的冲突解决规则处理矛盾结论
```

**Step 4.5：对抗性审计（v3.1.0 强制，交付前置）**
```
调用 Agent 工具启动 adversarial-auditor：
  name: "adversarial-auditor"
  subagent_type: "general-purpose"
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  prompt: "你是对抗审计者，读取 references/agent-prompts/adversarial-auditor.md，对 report-writer 生成的报告草稿发起反方审计，输出 challenges[] 通过 SendMessage 回传 orchestrator。"
  run_in_background: false
```
收到 challenges[] 后回传 report-writer（Step 4.5）：P0 且无法回应 → 拦截交付、请求人工裁决；P1 → 补充反向证据/下调置信度；P2/P3 → 标注提示。报告须含「对抗性审计与回应」章节。详见 `references/agent-prompts/adversarial-auditor.md`。

**Step 4.6：自评估质量门（v3.2.0 强制，交付前置）**
```
调用 Agent 工具启动 quality-judge：
  name: "quality-judge"
  subagent_type: "general-purpose"
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  prompt: "你是质量裁判者，读取 references/agent-prompts/quality-judge.md，对 report-writer 的终稿做三维度打分（定性严谨度/定量准确度/可验证性），输出 quality_gate 通过 SendMessage 回传 orchestrator。"
  run_in_background: false
```
收到 quality_gate 后回传 report-writer（Step 4.6）：verdict=pass → 写入「自评估质量门」章节并进入 Step 5 投递；verdict=amber → 按 remediation 修订弱项后投递；verdict=block → 拦截交付、回炉重写或请求人工裁决。报告须含「自评估质量门」章节。详见 `references/agent-prompts/quality-judge.md`。

**Step 5：生成最终报告**
```
调用 Agent 工具启动 report-writer：
  name: "report-writer"
  subagent_type: "general-purpose"
  team_name: "financial-research-{YYYYMMDD-HHMM}"
  prompt: "你是报告撰写者，读取 references/agent-prompts/report-writer.md，整合所有子代理的JSON结果，生成最终 PDF 报告。"
  run_in_background: false  # 等它完成
```

**Step 6：清理团队**
```
报告生成并通过 deliver_attachments 送达用户后，调用 TeamDelete 清理团队资源。
```

### 冲突解决规则（必须遵守）

当不同子代理的结论冲突时，按以下优先级处理：

| 优先级 | 冲突类型 | 处理方式 |
|--------|----------|----------|
| P0 | 政策取向 vs 市场情绪矛盾 | 以**政策取向**为准（A股政策市特征） |
| P1 | 宏观数据 vs 行业数据矛盾 | 以**宏观数据**为准（自上而下原则） |
| P2 | 短期情绪 vs 长期趋势矛盾 | 标注矛盾，提示用户关注 |
| P3 | 不同数据源差异 | 标注差异，提供多源对比 |

**对抗审计严重度（adversarial-auditor）**：复用 P0–P3 分级——P0 必须修正结论/移除推荐并拦截交付，P1 必须补反向证据/下调置信度，P2/P3 标注提示；挑战记录随报告「对抗性审计与回应」章节交付。

**自评估质量门裁决（quality-judge）**：对终稿三维度打分（定性严谨度 / 定量准确度 / 可验证性，权重 0.34/0.33/0.33）。verdict=pass（三维度均≥8 且加权≥8）→ 直接送达；verdict=amber（存在维度 5–7 或加权 6–8，无 block 条件）→ 修订弱项后送达；verdict=block（任一维度<5 或 可验证性<7 或 审计 P0 未回应）→ 拦截交付、回炉或人工裁决。评分随报告「自评估质量门」章节交付。

**流程韧性降级裁决（resilience，v3.3.0）**：子代理/数据失败经重试耗尽后，按 `references/resilience.md` 降级矩阵处置（单维度缺失标注跳过 / 全失败降级单智能体 / 数据缺失用替代源或显式标注「推断」），所有事件记入 resilience_log 并由 report-writer 写入报告第12章「流程韧性声明」；第五道 fail-closed 校验 `check-resilience-declaration.sh` 拦截缺失该章节的报告。降级不改变四道既有质量校验门槛（provenance / 推导链 / 反方审计 / 自评估质量门照常拦截）。

**可执行推理裁决（code-agent，v3.4.0）**：报告中每一项定量主张必须能映射到 `code_workspace/<task_id>/variables.json` 一项（变量名+数值+代码引用），否则视为「散文式计算」不准交付；每张图表须有「（图表已视觉校验：…）」标注。纯定性任务须显式声明「本报告为定性分析，未含代码执行计算」并跳过变量空间章节。代码环境不可用则降级为人工/定性估算并在第13章登记降级原因，**降级不绕过**第六道 fail-closed 校验 `check-code-agent.sh`。详见 `references/code-agent.md`。

**经验沉淀裁决（experience，v3.5.0）**：每次研究交付后须沉淀可复用经验——避坑清单（append `experience/lessons-learned.md`）、标的研判模板（`experience/asset-templates/<标的>.md`）、行业框架（`experience/industry-frameworks/<行业>.md`），并在报告第14章「经验沉淀与复用」列卡片或声明「本次无新增可复用经验」；缺失第14章或章节为空触发第七道 fail-closed 校验 `check-experience-deposition.sh` 拦截。经验卡片供下次「知识库加载/历史案例检索」回灌复用，高价值者经 `SkillManage` 提升为正式 Skill；写入失败降级为 best-effort（第14章标注），不阻塞投递。详见 `references/experience-deposition.md`。

**工具治理裁决（mcp-governance，v3.6.0）**：所有外部工具/数据调用（AnySearch / AkShare / Bash / Code Agent）必须经工具治理层统一收口（参数校验 + 调用审计到 `tool_audit/<task_id>/tool_calls.jsonl`），禁止裸调；报告第15章「工具治理与调用审计」须列全部 call_id + tool + 归一化参数 + provenance 引用 + status，或显式声明「本报告未调用任何外部工具或数据源」。治理层不可用则降级采数并在第15章标注「工具治理层不可用，本次调用未统一审计」+ best-effort 补记调用清单，**降级不绕过**第八道 fail-closed 校验 `check-mcp-governance.sh`。治理层 retry/fail/degraded 事件同步 resilience_log（不重复造事件）。详见 `references/mcp-governance.md`。

**会话状态裁决（stateful-drilldown，v3.7.0）**：多轮下钻会话（同一 session_id 追问）须维护 `session_state/<session_id>.json`——每轮 append turns[]（带 parent_turn + reused 复用标记）、更新 drill_tree 与 cumulative_conclusion，报告投递后写 checkpoint（last_completed_turn/step）支持崩溃恢复；下钻轮复用历史 provenance/variables 不重采不重算。报告第16章「多轮下钻与会话状态」须列 session_id、问题树、每轮焦点+增量结论+复用清单、跨轮累积结论；**单轮会话**须显式声明「本报告为单轮一次性产出，无多轮下钻」。缺对应章节/声明触发第九道 fail-closed 校验 `check-stateful-drilldown.sh` 拦截。状态文件不可用则降级为 best-effort（本轮按单轮处理并标注），不阻塞投递。详见 `references/stateful-drilldown.md`。

**评测基准裁决（evaluation-benchmark，v3.8.0）**：所有标准评测任务交付前须跑客观五维度基准（工具调用正确性/数字复算一致性/推导链完整性/来源可追溯性/反方审计回应率），输出 `benchmark_score`（0–1）与 verdict。verdict=pass（≥0.80）→ 写第17章「客观评测与基准得分」并送达；verdict=amber（0.60–0.80）→ 修订弱项后送达；verdict=block（<0.60）→ 拦截交付、回炉或人工裁决。报告第17章须列 benchmark_score+五维度分+权重+verdict+任务引用，或显式声明「本报告不纳入客观评测基准」；缺第17章或空章节触发第十道 fail-closed 校验 `check-evaluation-benchmark.sh` 拦截。无对应 golden 任务/运行环境不可用则降级为 best-effort（第17章声明），不阻塞投递。详见 `references/evaluation-benchmark.md`。

**自进化裁决（self-evolution，v3.9.0）**：每次标准评测任务交付后须发射 evolution signals 并写入 `evolution/signals/<delivery_id>.json`，报告第18章「自进化反馈与改进建议」须列信号摘要（benchmark_score+verdict、quality 三维度、经验卡片数、未回应挑战数）+（≥1 改进建议条目，或显式声明「本次无新增改进建议」）；非标准任务须显式声明「本报告不纳入自进化闭环」。缺失第18章或章节为空触发第十一道 fail-closed 校验 `check-self-evolution.sh` 拦截。候选补丁（candidate_patches）须经人工 review（proposed→approved→applied），受控发布走 git tag、regression_guard 不达标（benchmark_score<0.60）即 `git checkout` 秒级回滚；自进化是交付后元流程，不修改正文十道校验门槛。详见 `references/self-evolution.md`。

**投决会裁决（investment-committee，v3.10.0）**：含投资建议的报告交付前须跑投决会对抗决策——五委员（主持/看涨/看跌/中性/风控）对抗，强制交叉质询，形成决议（verdict∈{强力推荐/推荐/中性/谨慎/否决}+consensus 0–1+主要分歧点+风险预案+dissent）。verdict=强力推荐/推荐 → 写第 19 章「投决会对抗决策与决议」并作为报告综合建议的强约束；verdict=中性 → 写入并说明；verdict=谨慎/否决 → 与报告综合建议冲突须复核或升级 HITL。报告第 19 章须列委员立场+决议（verdict+共识度）+（风险预案 或 「无委员立场记录」声明）；纯研究/无投资建议须显式声明「本报告不纳入投决会对抗决策」；缺失第 19 章或空章节触发第十二道 fail-closed 校验（`check-investment-committee.sh`）拦截。决议 consensus/verdict 作为新质量信号维度进入 G9 evolution signals。详见 `references/investment-committee.md` §7 / `references/report-structure.md`。

**知识回流裁决（knowledge-ingestion，v3.11.0）**：含外部邮件来源信息或用户显式触发时，须经 agent-mail 摄取投研相关邮件知识——`GetMe` 确认权限 → `SearchMessages` 检索候选 → `GetMessage` 读正文 → `ListAttachments`/`DownloadAttachment` 取附件（仅 PDF/Excel/Word/CSV）→ 抽取可复用知识归类写入 `experience/`（带 `source: agent-mail:<message_id>` 溯源）。报告第 20 章「非结构化知识回流」须列摄取状态+相关邮件清单（脱敏）+知识卡片列表（分类+路径+溯源），或显式声明「本报告未摄取外部邮件知识」（agent-mail 未开通/无匹配，best-effort 不阻塞）/「本报告不纳入非结构化知识回流」；缺失第 20 章或空章节触发第十三道 fail-closed 校验（`check-knowledge-ingestion.sh`）拦截。新卡片数作为知识增量进入 G9 evolution signals。详见 `references/g11-knowledge-ingestion.md` §6 / `references/report-structure.md`。

### 单模块请求处理（不触发 Agent Teams）

当用户只请求单一模块（如只说"查一下茅台的巴菲特评分"），则：
1. 读取对应 methodology 文件
2. 直接执行分析（不需要启动子代理）
3. 生成 PDF 报告
4. 通过 deliver_attachments 送达用户

---

## 工作流程

本 Skill 支持与其他 Skills 联合应用，详见 `references/skill-combination-cases.md`（课程答辩重点）。

**标准流程**：**复杂度分级（Step 0，见 references/tiering.md）→ 触发识别 → 判断是否需要 Agent Teams → 结果缓存检索（v3.13.0：先查 cache/ 同标的/同域近期结论，命中且未过期则复用不重跑 agent，见 references/tiering.md §五.七）→ 会话状态加载（多轮下钻 v3.7.0：带入 session_id 则读 session_state 复用历史 provenance/variables 不重采，否则创建新会话）→ 知识库加载（含 experience/ 经验卡片回灌）→ 历史案例检索 → 数据采集（经工具治理层统一收口 v3.6.0：参数校验+调用审计）→ 分析执行 → HITL节点 → 报告生成（含第16章多轮下钻与会话状态/单轮豁免声明 v3.7.0）→ 客观评测基准（v3.8.0 强制：跑 benchmark suite，写第17章「客观评测与基准得分」或声明「本报告不纳入客观评测基准」）→ 经验沉淀（v3.5.0 强制：产出可复用知识卡片，写入 experience/ 并写入报告第14章）→ 自进化反馈收集（v3.9.0 强制：发射 evolution signals 到 evolution/signals/，写第18章「自进化反馈与改进建议」或声明「本报告不纳入自进化闭环」）→ 会话 checkpoint 落盘（v3.7.0：写 session_state 的 updated_at/checkpoint 支持崩溃恢复）→ 投决会对抗决策（v3.10.0 强制：含投资建议时跑五委员对抗决策，写第19章「投决会对抗决策与决议」或声明「本报告不纳入投决会对抗决策」）→ 非结构化知识回流（v3.11.0 强制：经 agent-mail 摄取投研相关邮件知识，写入 experience/ 并写第20章「非结构化知识回流」或声明「本报告未摄取外部邮件知识」/「本报告不纳入非结构化知识回流」）**。

### 分析深度判断

在触发识别后、正式分析前，先判断用户需要的分析深度：

- **深度研究报告** → 调用 `hv-analysis` skill（横纵分析法），产出 PDF 格式深度报告
  - 触发词："深度分析""研究报告""横纵分析""完整研究""对比研究"
  - 对象：具体公司、产品、金融概念、投资策略
  - **大公司完整产业链分析规则（强制执行）**：
    - 研究对象为NVIDIA/台积电/苹果/谷歌/微软等大型复杂公司时，**必须做深法**，分析到具体子公司、子产业的完整产业链
    - 必须覆盖：所有核心子公司/事业部（如NVIDIA的Mellanox/Cumulus/DOCA等）、完整产业链图谱（芯片设计→代工→存储→封装→供应链→生态伙伴）、各子公司的竞争定位
    - 纵向分析不限制字数，以完整覆盖为目标；横向对比必须覆盖所有主要竞品（不只1-3个）
  - 输出：10,000-30,000字 PDF 报告（纵向叙事 + 横向对比 + 横纵交汇洞察 + **投资建议章节**）


**产业链/供应链分析请求** → 先做深法分析完整产业链（子公司+子产业）→ 输出美股核心标的（最多10只）→ 映射对应A股核心标的（最多10只）→ 生成投资建议表格

示例3（产业链）：`分析NVIDIA产业链和投资建议` → 做减法聚焦核心供应链 → 输出10只美股+10只A股 → 精准投资建议（核心推荐/次级推荐/观望）

### 可用策略列表

| 策略名称 | 函数名 | 参数 | 信号逻辑 |
|----------|--------|------|----------|
| MA 均线交叉 | `ma_cross_strategy` | `fast_period=5, slow_period=20` | MA5 上穿 MA20 → 买入；下穿 → 卖出 |
| MACD | `macd_strategy` | `fast_period=12, slow_period=26, signal_period=9` | DIF 上穿 DEA → 买入；下穿 → 卖出 |
| RSI | `rsi_strategy` | `period=14, oversold=30, overbought=70` | RSI < 30 → 买入；RSI > 70 → 卖出 |
| 布林带 | `bollinger_strategy` | `period=20, std_dev=2.0` | 价格触及下轨 → 买入；触及上轨 → 卖出 |

### 使用方法

```python
from strategies.ma_cross import ma_cross_strategy
from backtest_engine import run_backtest, calculate_metrics, generate_backtest_report

# 加载策略
strategy_func = ma_cross_strategy  # 或 macd_strategy, rsi_strategy, bollinger_strategy

# 执行回测
portfolio, trades, cash_history, position_history = run_backtest(
    strategy_func, df, initial_cash=1000000
)

# 计算性能指标
metrics = calculate_metrics(portfolio, df)

# 生成报告（PDF格式）
generate_backtest_report(
    strategy_name="MA均线策略",
    symbol="600519",
    start_date="2025-01-01",
    end_date="2025-09-30",
    portfolio=portfolio,
    trades=trades,
    metrics=metrics,
    output_path="reports/MA均线策略_回测报告.pdf",
    net_value_img="reports/net_value_curve.png",
    drawdown_img="reports/drawdown_curve.png"
)
```

### 扩展自定义策略

1. 在 `scripts/strategies/` 目录下创建新文件（如 `my_strategy.py`）
2. 定义策略函数，签名为 `def my_strategy(row, history, **kwargs):`
3. 函数必须返回 `"BUY"` / `"SELL"` / `"HOLD"`
4. 在 `strategy_loader.py` 中注册新策略

---

## Gotchas（常见错误）

> **详细错误案例**：参见各模块methodology文件末尾的"常见错误案例"部分

- AkShare/子代理/数据获取失败 → 按 `references/resilience.md` 重试 ≤3 次（指数退避 2s/4s/8s），耗尽则降级而非崩溃；所有降级记入 resilience_log 并写入报告第12章「流程韧性声明」
- 定量计算/图表 → 必须走 Code Agent 统一变量空间执行（见 `references/code-agent.md`），禁止 LLM 裸算；结果登记 variables.json，图表须视觉校验；缺「可执行推理与变量空间」章节或纯定性未声明者触发第六道校验拦截
- 经验沉淀 → 每次研究交付后须产出可复用知识卡片（避坑清单/标的模板/行业框架）写入 `experience/` 并写入报告第14章「经验沉淀与复用」；缺章节或空洞（无条目且无「本次无新增可复用经验」声明）触发第七道校验 `check-experience-deposition.sh` 拦截
- 工具治理 → 所有外部工具/数据调用（AnySearch/AkShare/Bash/Code Agent）须经工具治理层统一收口（参数校验+调用审计，写入 `tool_audit/<task_id>/tool_calls.jsonl`），禁止裸调；报告须含第15章「工具治理与调用审计」并列全部 call_id+tool+参数+provenance+status，或显式声明「本报告未调用任何外部工具或数据源」；缺章节或空洞触发第八道校验 `check-mcp-governance.sh` 拦截
- 状态化多轮下钻 → 同一会话下钻追问须维护 `session_state/<session_id>.json`（每轮 append turns[]+reused 复用标记、写 checkpoint 支持崩溃恢复）；多轮报告须含第16章「多轮下钻与会话状态」（session_id+问题树+每轮焦点/增量结论/复用清单+累积结论），单轮须显式声明「本报告为单轮一次性产出，无多轮下钻」；缺章节或声明触发第九道校验 `check-stateful-drilldown.sh` 拦截；状态文件不可用 best-effort 不阻塞
  - 客观评测基准 → 所有标准评测任务交付前须跑 benchmark suite（读取 benchmark/tasks/*.json 的 golden），客观五维度打分写报告第17章「客观评测与基准得分」（benchmark_score+五维度分+权重+verdict），或显式声明「本报告不纳入客观评测基准」；缺第17章或空章节触发第十道校验 `check-evaluation-benchmark.sh` 拦截；运行环境不可用 best-effort 不阻塞（须声明）
- 自进化闭环 → 每次交付后须发射 evolution signals（benchmark_score/quality_dims/experience_cards/unresolved_challenges）到 evolution/signals/<delivery_id>.json，并在报告第18章「自进化反馈与改进建议」列信号摘要+（≥1 改进建议 或 「本次无新增改进建议」声明），或显式声明「本报告不纳入自进化闭环」；缺第18章或空章节触发第十一道校验 `check-self-evolution.sh` 拦截；候选补丁经 git tag 受控发布、回归 guard 不达标秒级回滚
- 投决会对抗决策 → 含投资建议的报告交付前须跑五委员对抗决策（主持/看涨/看跌/中性/风控），强制交叉质询，形成 investment_committee/<delivery_id>.json 决议（verdict+consensus+分歧点+风险预案+dissent）并强约束报告综合建议；报告第19章「投决会对抗决策与决议」须列委员立场+决议（verdict+共识度）+（风险预案 或 「无委员立场记录」声明），或显式声明「本报告不纳入投决会对抗决策」；缺第19章或空章节触发第十二道校验 `check-investment-committee.sh` 拦截；投决会基础设施不可用 best-effort 不阻塞（须声明）
- 货币政策语义分析边界案例 → 添加HITL节点人工复核
- 报告缺少数据来源标注 → 强制执行`references/disclaimer-sources.md`
- PDF 生成失败 → 先生成 .docx，标注"PDF转换失败，暂提供 .docx 版本"
- Agent Teams 子代理启动失败 → 降级为单智能体串行执行，标注"Agent Teams 启动失败，已降级为单智能体模式"

---

*本 Skill 为顶级 Agent Teams 架构设计，SKILL.md 为入口索引，详细内容存于 `${CLAUDE_SKILL_DIR}/references/` 目录。*
*完整参考资料列表：参见 `references/references-list.md`*
