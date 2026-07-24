# 知识库使用指南

> 本文件为「金融AI投研」Skill的知识库使用规范。
> 知识库分为三大类：methodology（方法论）、cases（历史案例）、industry-graph（行业图谱）。

---

## 知识库目录结构

```
references/knowledge-base/
├── methodology/              # 七大模块的方法论文档
│   ├── module1-investment-master.md
│   ├── module2-monetary-policy.md
│   ├── module3-asset-allocation.md
│   ├── module4-industry-research.md
│   ├── module5-macro-monitor.md
│   ├── module6-market-environment.md
│   └── module7-sentiment-pulse.md
├── cases/                   # 历史分析案例库
│   ├── 025856_电网设备ETF_2026-05-10.md
│   └── ...（按板块/股票代码存储）
└── industry-graph/         # 行业知识图谱
    └── power-grid-equipment.md
```

---

## 使用规范

### 1. 执行前必读（强制执行）

**每个模块执行前，必须先读取对应的 methodology 文件！**

```python
# 伪代码示例
def execute_module(module_id, user_query):
    # Step 0: 读取方法论
    methodology = read_file(f"references/knowledge-base/methodology/module{module_id}-*.md")
    
    # Step 1: 搜索历史案例
    cases = grep_search("cases/", keywords=user_query.keywords)
    
    # Step 2: 执行分析（基于methodology + cases）
    result = analyze(methodology, cases, user_query)
    
    return result
```

### 2. 历史案例检索

**检索流程**：
1. 从用户查询中提取关键词（股票代码、板块名称、行业名称）
2. 在 `cases/` 目录搜索相关案例
3. 如果有相似案例，读取并作为分析参考
4. 在输出中标注："参考历史案例：{案例名称}"

**案例文件命名规范**：
```
{股票代码}_{板块名称}_{YYYY-MM-DD}.md
```
示例：`025856_电网设备ETF_2026-05-10.md`

### 3. 分析后存盘

**每次分析完成后，必须将关键结论存入知识库！**

存盘内容：
- 分析结论（买入/持有/卖出，置信度）
- 关键数据（财务数据、情绪评分、政策取向…）
- 分析逻辑（用到了哪些指标、为什么得出此结论）
- 后续观察点（需要持续跟踪的指标）

存盘路径：`references/knowledge-base/cases/{股票代码}_{板块名称}_{YYYY-MM-DD}.md`

---

## 行业知识图谱

`industry-graph/` 目录存储行业层面的结构化知识：
- 产业链上下游关系
- 关键指标定义（如电网设备ETF的"特高压投资完成额"）
- 行业特有的分析框架

**使用方法**：
1. 用户提到某个行业时，先检查 `industry-graph/` 是否有对应文件
2. 如果有，读取并作为分析背景
3. 如果没有，分析完成后创建该文件，存入行业知识

---

## 知识库维护

### 定期审查（建议每月）
- 删除过时案例（超过6个月且不再适用的）
- 更新 methodology 文件（如发现新的有效指标）
- 补充 industry-graph（覆盖更多行业）

### 版本控制
- 重大更新在文件末尾添加"更新日志"
- 保留历史版本的关键结论，用于回溯测试

---

## 搜索示例

### 示例1：用户查询"分析一下贵州茅台"
```python
# 提取关键词：600519（股票代码）、贵州茅台、白酒
# 搜索 cases/600519*.md 或 cases/*茅台*.md
# 如果找到历史案例，读取并参考
```

### 示例2：用户查询"电网设备板块还行吗"
```python
# 提取关键词：电网设备、特高压、电网设备ETF
# 搜索 cases/*电网设备*.md
# 找到 025856_电网设备ETF_2026-05-10.md
# 读取并对比最新数据，给出"延续/反转/新结论"
```

---

## 知识库质量检查

- [ ] methodology 文件是否为最新版本（检查更新日期）
- [ ] cases 文件是否标注了数据获取时间
- [ ] 行业图谱是否覆盖了用户常查的行业
- [ ] 是否有重复案例（同一股票多个文件，需合并）

---

*知识库是本Skill的核心资产，质量决定分析质量。每次分析都是一次知识积累。*