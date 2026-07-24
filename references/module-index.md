# 模块索引（执行前必读）

> **执行规范**：每个模块执行前，**必须先读取**对应的 methodology 文件，
> 获取该模块的方法论、回测数据、参数建议、常见错误案例，再执行分析。

> **惰性加载（v3.13.0，省 token）**：methodology 文件（module1–9）**不再随 skill 加载全量注入**，须在执行对应维度时**按需 Read**（路径见下表「方法论文件」列）。skill 加载时仅注入本索引；agent 读本索引后按触发词自行 Read 对应 methodology，避免一次性占用上下文 token。
> 历史相似案例检索：先读取 `${CLAUDE_SKILL_DIR}/references/knowledge-base/cases/` 目录，
> 用关键词搜索（Grep）相似历史案例，作为分析参考。

| 模块 | 触发词 | 方法论文件 | Agent Prompts |
|------|--------|-----------|---------------|
| 一：AI投资大师智能体 | `AI选股` `投资大师` `巴菲特` | module1-investment-master.md | — |
| 二：货币政策语义分析 | `货币政策` `政策语义` `LPR` `MLF` | module2-monetary-policy.md | policy-analyst.md |
| 三：国信AI资配框架 | `资产配置` `股债强弱` `美林时钟` | module3-asset-allocation.md | — |
| 四：行业基本面研究 | `行业研究` `竞品分析` `市场调研` | module4-industry-research.md | industry-analyst.md |
| 五：宏观数据监控 | `宏观数据` `经济指标` `CPI` `PPI` `PMI` | module5-macro-monitor.md | macro-analyst.md |
| 六：市场环境分析 | `市场环境` `全球市场` `风险情绪` | module6-market-environment.md | market-analyst.md |
| 七：市场情绪脉搏 | `市场情绪` `情绪评分` `新闻情绪` `资金流向` | module7-sentiment-pulse.md | sentiment-analyst.md |
| 八：顶级基金深度分析 | `基金分析` `基金深度` `基金经理` `基金业绩` | module8-fund-analysis.md | fund-analyst.md |
| 九：策略回测引擎 | `回测策略` `策略回测` `策略验证` `backtest` | module9-backtest.md | backtest-analyst.md |
