# 金融AI投研 Skill

> 一个面向 A 股 / 固收 / 基金的 multi-agent 投研框架，强调**可审计、可重现、可追溯**——每一条结论都能回推到来源快照与字符锚点。

## 特性（均为可验证机制）

- **13 道 fail-closed 交付前校验**：provenance 锚定、推导链、对抗性反方审计、自评估质量门、流程韧性声明、可执行推理、经验沉淀、工具治理、多轮下钻、客观评测基准、自进化闭环、投决会对抗决策、非结构化知识回流。任一道未过即拦截交付，不降级放行。
- **来源快照 + 字符锚定（provenance）**：抓取即存 `provenance/<id>.json` 全文 / 片段快照，报告用 `（快照：provenance/<id>.json @ [s,e]）` 引用，`verify-provenance.py` 比对字符区间，越界即拦。
- **复杂度分级（T1 / T2 / T3）**：仅控制是否拉起昂贵的 agent 流程（反方审计 / 投决会 / benchmark / 自进化 / 知识回流），廉价结构校验照常，门槛不降。
- **省 token 机制（v3.13.0+）**：模块引用惰性加载、每章节 token 预算 + 紧模板、动态 agent 选择、provenance 轻量锚定、结果缓存复用。
- **多轮下钻**：同一 `session_id` 下追问复用已采 provenance / 已算 variables，不重采不重算。
- **经验回流**：研究后自动产出可复用知识卡片（避坑 / 标的模板 / 行业框架），可选同步至 Obsidian 知识库。

## 快速开始

本 skill 为 WorkBuddy 用户级 skill，放入 `~/.workbuddy/skills/金融AI投研/` 即被自动匹配加载。

直接提问即可触发，例如：

- “分析某白酒龙头的投资价值”（→ 自动走 T2 标准）
- “做一份科创债投研框架”
- “现在是不是 Risk-On 环境？”
- “对比半导体和新能源板块”

分级控制（省 token）：

- 简单单点问题 → 自动 **T1**（正文 ≤800 token，跳过反方审计 / 投决会）
- 想要完整深度 → 说“**深度分析**”或“**按 T3 跑**”，拉满 13 道闸门
- 想最省 → 说“**快速回答**”锁定 T1

> 注：以上示例标的均为脱敏占位，实际使用时替换为真实代码 / 名称。

## 安装

```bash
git clone <your-repo-url> ~/.workbuddy/skills/金融AI投研
```

## 依赖（均优雅降级，缺失不崩）

| 依赖 | 用途 | 缺失时 |
| --- | --- | --- |
| AnySearch skill | 联网检索与页面提取 | 提示需安装，不阻塞本地分析 |
| AkShare | A 股 / 基金行情与财务数据 | 提示需安装，可手动提供数据 |
| Obsidian CLI（可选） | 经验回流至 OB 知识库 | 跳过同步，不影响研究 |

## 配置（个人化，不入仓库）

经验同步至 Obsidian 需要指定 vault 路径，按以下任一方式提供（优先级从高到低）：

1. 环境变量 `OB_VAULT`
2. 本地配置文件 `config.local.json`（已加入 `.gitignore`，不进仓库）
3. 命令行 `--ob-target <路径>`

复制模板后填写你自己的路径：

```bash
cp config.local.example.json config.local.json
# 编辑 config.local.json，把 ob_vault 改成你的 Obsidian vault 下 AI投研知识库目录
```

三者皆未提供时，脚本会明确报错退出（fail-closed），绝不静默写错位置。

## 目录结构

```
金融AI投研/
├── SKILL.md                      # 入口与编排
├── references/                   # 方法论、分级、报告结构、agent 提示词
│   ├── tiering.md                # T1/T2/T3 分级规范
│   ├── report-structure.md       # 每章节 token 预算与紧模板
│   ├── module-index.md           # 模块索引（按需 Read，不随 skill 全量注入）
│   └── agent-prompts/            # 9 类分析师 + 反方审计 + 质量门 + report-writer
├── scripts/
│   ├── sync_experience_to_obsidian.py  # 经验回流至 OB（需配置 OB_VAULT）
│   └── backtest_engine.py        # 回测引擎
├── config.local.example.json     # 配置模板（复制为 config.local.json 填写）
├── .gitignore
└── .workbuddy/hooks/             # 13 道 fail-closed 校验脚本 + verify-provenance.py
```

## 验证

交付前由 13 个 hook 脚本（`references/agent-prompts` 对应流程触发）+ `verify-provenance.py` 执行 fail-closed 校验。本地可手动跑：

```bash
python .workbuddy/hooks/verify-provenance.py <报告目录>
```

## 独立基准验证（Phase D）

为防止「自我评分」自嗨，本 skill 内置可机器复现的攻击测试套件 `tests/attack_suite.py`：构造缺失快照 / 越界区间 / 字节不符 / 结论无推导链 / 缺第13章 等攻击样本，统计校验脚本拦截率。

最近一次运行结果（可 `python tests/attack_suite.py` 复现）：

| 指标 | 结果 |
| --- | --- |
| 攻击拦截召回率（D1：格式/锚定/章节） | 6/6 = 100% |
| 误杀（合法报告被拦） | 0 |
| 误放（攻击样本被放过） | 0 |

**D2 — 推导链逻辑正确性**（`tests/derivation_suite.py`）：在 D1 之上补验 G2 的"证据→计算→结论"是否真的成立，构造跳跃推导 / 计算与结论数值不符 / 证据造假 等攻击样本。

| 指标 | 结果 |
| --- | --- |
| 攻击拦截召回率（D2：推导逻辑） | 4/4 = 100% |
| 误杀 | 0 |
| 误放 | 0 |
| 内置已知答案题集（供 LLM 判分） | 3 题 |

**D3 — 历史回测吻合度 + 禁未来函数**（`tests/backtest_suite.py`）：构造信号引用 t+1 收盘价 / 前向窗口归一化 / 全样本归一化 / 训练测试重叠 等未来函数攻击样本，验证 `check_no_lookahead` 拦截率；并用固定 seed 合成历史价 + 严格只用历史的动量策略，验证净值/夏普/最大回撤两次运行完全一致（吻合度可复现，无随机污染）。

| 指标 | 结果 |
| --- | --- |
| 攻击拦截召回率（D3：禁未来函数） | 4/4 = 100% |
| 误杀 | 0 |
| 误放 | 0 |
| 历史回测吻合度可复现（两次运行一致） | 是 |

> 三套测试（D1/D2/D3）均不依赖任何本地配置、不调用外部网络，已接入 CI 持续复证 fail-closed、推导逻辑正确性与禁未来函数并非空谈。真实 AkShare 数据回测（禁未来函数 + 真实 P&L 验证）归入 Phase C 之后的实战战绩场景。

## 版本

逐版叠加可信层：v3.0.0 起至 v3.11.0 完成 13 道闸门；v3.12.0 加 tiering 分级；v3.12.1 G4→OB 多源同步；v3.13.0 省 token 深化；v3.14.0 去个人化与可移植（config 外置）；v3.15.0 补齐发布工程（README / LICENSE / CI）；v3.16.0 Phase D1 攻击召回率测试；v3.17.0 Phase D2 推导链逻辑测试；v3.18.0 Phase D3 禁未来函数+回测吻合度。完整说明见 `SKILL.md` 头部 description。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。

## 免责声明

本 skill 输出为 AI 生成的研究辅助内容，**不构成任何投资建议**。投资决策须自行判断并自担风险。
