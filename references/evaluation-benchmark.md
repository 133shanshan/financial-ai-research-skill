# 客观评测基准（Evaluation Benchmark，v3.8.0）

> 本规范对应后续优化项 **G8「主观自评估无客观标尺」** 差距：原 Skill 仅有 quality-judge（v3.2）主观三维度自评估，缺外部客观评测基准；2026 前沿（FinToolBench arXiv 2603.08262、iRaB 投研评测体系、蚂蚁 Agentic Engineering L1–L3 评测）均强调「可度量、可比较、可迭代」是金融 Agent 从 Demo 走向生产的关键门槛。
> 标杆：**FinToolBench / iRaB**——用源于真实投研场景的评测集对 Agent 做客观打分，推动能力从主观判断走向可度量。
> 核心原则：**客观基准（benchmark）与主观自评估（quality-judge）双轨并行**；benchmark 提供可复现、可比较、可迭代的客观分数，作为 skill 持续进化（G9 自进化）的度量前提——没有客观标尺就无法知道变好还是变差。

---

## 1. 为什么需要客观评测基准

| 痛点（G8） | 客观基准方案 |
|-----------|-------------|
| quality-judge 仅主观打分，无法横向比较不同版本/不同任务的真实质量 | 内置 benchmark suite，对每篇报告跑客观五维度打分，分数可跨任务/跨版本比较 |
| 无法证明 skill 升级后「真的变好」 | benchmark_score 随版本记录，v3.7.0→v3.8.0 可量化对比 |
| 缺标准答案核验（数字对不对、工具调没调对） | 评测集含 golden 标准（正确数值/正确工具调用/正确推导链），自动比对 |
| 无法驱动后续自进化（G9） | benchmark 分数是自进化的反馈信号（对齐蚂蚁自进化双路径） |

---

## 2. 评测维度（客观五维度，对齐 FinToolBench / iRaB）

每维度评分 0–1，独立可复算：

| 维度 | 含义 | 对齐来源 | 评测方法 |
|------|------|---------|---------|
| ① 工具调用正确性 Tool Correctness | 治理层调用是否命中正确工具+正确参数（intent/timeliness/regulatory 对齐） | FinToolBench | 比对 `tool_audit` 调用记录与 golden 工具/参数 |
| ② 数字复算一致性 Numeric Reproducibility | 报告关键数值能否被 Code Agent 变量空间复算一致 | LangAlpha PTC / v3.4 | 重跑 `variables.json` 对应计算，比对数值误差 ≤ ε |
| ③ 推导链完整性 Derivation Completeness | 证据→计算→结论三段链齐全且闭合 | v3.1 推导链 | 解析报告推导链，比对 golden 链节点 |
| ④ 来源可追溯性 Source Traceability | 每条关键结论有 provenance 快照锚定 | v3.1 provenance | 比对结论与 provenance 区间覆盖率 |
| ⑤ 反方审计回应率 Adversarial Resolution | challenges[] 是否全部有处置 | v3.1 审计 | 比对 challenge 数与处置数，要求 100% 回应 |

---

## 3. 评测集（benchmark suite）

目录脚手架 `benchmark/` 随 v3.8.0 纳入版本管理（含 `.gitkeep` 与示例任务）。

- **来源**：①历史 deliver 报告提炼的标准任务（脱敏）②行业公开真实投研场景（对齐 FinToolBench / iRaB 公开任务）
- **结构**：每个任务 `benchmark/tasks/<task_id>.json` 含 `prompt`（任务描述）、`golden`（标准答案：正确工具调用/关键数值/推导链/来源要求/审计预期）、`scoring`（维度权重）。
- **运行**：由「评测基准裁判（Benchmark Judge）」角色读取本报告 + golden 比对，输出五维度分与 `benchmark_score`；亦可由 `benchmark/run_benchmark.py` 半自动执行。
- **权重**：默认 ①0.25 ②0.25 ③0.20 ④0.20 ⑤0.10（任务级 golden 可覆盖）。

---

## 4. 评分规则与达标阈值

- `benchmark_score` = Σ(维度分 × 权重)
- **verdict**：
  - `pass`：benchmark_score ≥ 0.80 → 进入交付
  - `amber`：0.60 ≤ score < 0.80 → 修订弱项后可交付（带提示）
  - `block`：score < 0.60 → 拦截交付，回炉或人工裁决
- 与主观 quality-judge 独立：二者任一 `block` 即拦截（双轨 fail-closed）。

---

## 5. 与 quality-judge 的关系（双轨）

- quality-judge（v3.2，主观）：定性严谨度 / 定量准确度 / 可验证性，三维度 0–10，verdict 三档。
- benchmark（v3.8，客观）：上述五维度 0–1，verdict 三档。
- 二者**并行独立**，报告须同时含第 11 章（主观）与第 17 章（客观）；任一 block 拦截。
- benchmark 是 G9 自进化的反馈信号：版本间 benchmark_score 对比驱动经验沉淀升级。

---

## 6. 报告交付：第 17 章「客观评测与基准得分」

- **标准评测任务**：报告须含第 17 章，列：
  - `benchmark_score`（加权 0–1）+ 各维度分（①–⑤）+ 权重 + verdict（pass/amber/block）
  - 评测集任务引用（task_id）+ 与 golden 的差异说明
- **非标准任务豁免**：若本报告为纯探索性 / 用户未要求 benchmark / 无对应 golden 任务，须显式声明「本报告不纳入客观评测基准」，放行。
- 第十道 fail-closed 校验 `check-evaluation-benchmark.sh` 据此拦截（见第 8 节）。

---

## 7. 降级处置

- benchmark 运行环境不可用（脚本缺失 / 无 golden 任务 / 沙箱受限）→ best-effort，不阻塞投递；报告第 17 章（或声明处）标注「评测基准运行环境不可用，本次未跑客观评测」，不触发第十道拦截（但须在声明中明确）。
- 评测集为空（无对应任务）→ 可声明豁免（同第 6 节非标准任务）。

---

## 8. 第十道 fail-closed 校验（check-evaluation-benchmark.sh）

脚本逻辑（skill 与 workspace 双副本，chmod +x）：

1. 报告含「客观评测与基准得分」章节 → 须含评测条目（维度 / 得分 / 阈值 任一），否则 `ok:false` 拦截。
2. 报告显式声明「本报告不纳入客观评测基准」→ 放行。
3. 既无章节又无声明 → `ok:false` 拦截。
4. 空章节（有标题无条目）→ `ok:false` 拦截。

> 与前九道一致：强制章节 + 豁免声明，fail-closed 不投递。
