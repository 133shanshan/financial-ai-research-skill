#!/usr/bin/env bash
# 第十道 fail-closed 校验（v3.8.0）：客观评测基准（evaluation-benchmark）
# 规则：
#   标准评测任务（含「客观评测与基准得分」章节）→ 须含具体评测条目（benchmark_score/verdict/五维度 任一），否则拦截
#   非标准任务 → 须显式声明「不纳入客观评测基准」（兼容任意前缀），否则拦截
#   既无章节又无声明 → 拦截
# 用 bash 内置 [[ ]] 模糊匹配规避中文 UTF-8 失配（grep 在部分环境下不稳定）
set -uo pipefail

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo '{"ok":false,"reason":"usage: check-evaluation-benchmark.sh <report.md>"}'
  exit 1
fi

content=$(cat "$FILE" 2>/dev/null)
if [ -z "$content" ]; then
  echo '{"ok":false,"reason":"报告文件为空，无法校验评测基准"}'
  exit 1
fi

# 1) 标准评测任务：含「客观评测与基准得分」章节
if [[ "$content" == *"客观评测与基准得分"* ]]; then
  # 章节须含具体评测条目（benchmark_score / verdict / 五维度任一），避免仅标题被误判
  if [[ "$content" == *"benchmark_score"* || "$content" == *"verdict"* || "$content" == *"工具调用正确性"* || "$content" == *"数字复算一致性"* || "$content" == *"推导链完整性"* || "$content" == *"来源可追溯性"* || "$content" == *"反方审计回应率"* ]]; then
    echo '{"ok":true,"reason":"报告含「客观评测与基准得分」章节且含具体评测条目"}'
    exit 0
  else
    echo '{"ok":false,"reason":"「客观评测与基准得分」章节为空，缺少评测条目（benchmark_score/verdict/五维度）"}'
    exit 1
  fi
fi

# 2) 非标准任务：显式豁免声明（接受「不纳入客观评测基准」任意前缀）
if [[ "$content" == *"不纳入客观评测基准"* ]]; then
  echo '{"ok":true,"reason":"报告显式声明不纳入客观评测基准"}'
  exit 0
fi

# 3) 既无章节又无声明 → 无法确定评测状态，拦截
echo '{"ok":false,"reason":"未检测到「客观评测与基准得分」章节，也未声明「不纳入客观评测基准」，无法确定评测状态"}'
exit 1
