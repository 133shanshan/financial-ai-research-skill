# 客观评测基准集（Benchmark Suite，v3.8.0）

本目录存放金融AI投研 Skill 的客观评测任务集，供第十道 fail-closed 校验（check-evaluation-benchmark.sh）与「评测基准裁判（Benchmark Judge）」角色使用。

## 结构
- `tasks/<task_id>.json`：单个评测任务，含 `prompt`（任务描述）、`golden`（标准答案：正确工具调用/关键数值/推导链/来源要求/审计预期）、`scoring`（维度权重）。
- 运行：由 Benchmark Judge 角色读取本报告 + golden 比对，输出五维度分与 `benchmark_score`；或由 `run_benchmark.py` 半自动执行。

## 任务来源
1. 历史 deliver 报告提炼的标准任务（脱敏）
2. 行业公开真实投研场景（对齐 FinToolBench / iRaB）

## 当前状态
- 示例任务 `tasks/example_task.json` 已提供，完整任务集待后续版本（G8.1）填充。
- 评测集为空或运行环境不可用时，报告可显式声明「本报告不纳入客观评测基准」豁免（第十道校验放行）。
