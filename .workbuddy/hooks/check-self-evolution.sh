#!/usr/bin/env bash
# 第十一道 fail-closed 校验（v3.9.0）：自进化闭环（self-evolution）
# 规则：
#   标准任务（含「自进化反馈与改进建议」章节）→ 须含信号摘要（信号摘要/benchmark_score）+（≥1 改进建议 或 「本次无新增改进建议」），否则拦截
#   非标准任务 → 须显式声明「不纳入自进化闭环」（兼容任意前缀），否则拦截
#   既无章节又无声明 → 拦截
# 用 bash 内置 [[ ]] 模糊匹配规避中文 UTF-8 失配（grep 在部分环境下不稳定）
set -uo pipefail

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo '{"ok":false,"reason":"usage: check-self-evolution.sh <report.md>"}'
  exit 1
fi

content=$(cat "$FILE" 2>/dev/null)
if [ -z "$content" ]; then
  echo '{"ok":false,"reason":"报告文件为空，无法校验自进化闭环"}'
  exit 1
fi

# 1) 标准任务：含「自进化反馈与改进建议」章节
if [[ "$content" == *"自进化反馈与改进建议"* ]]; then
  # 须含信号摘要（信号摘要 / benchmark_score）
  has_signal=0
  if [[ "$content" == *"信号摘要"* || "$content" == *"benchmark_score"* ]]; then
    has_signal=1
  fi
  # 须含改进建议条目（改进建议）或显式无建议声明
  has_suggestion=0
  if [[ "$content" == *"改进建议"* || "$content" == *"本次无新增改进建议"* ]]; then
    has_suggestion=1
  fi
  if [[ "$has_signal" == "1" && "$has_suggestion" == "1" ]]; then
    echo '{"ok":true,"reason":"报告含「自进化反馈与改进建议」章节且含信号摘要+改进建议/无建议声明"}'
    exit 0
  else
    echo '{"ok":false,"reason":"「自进化反馈与改进建议」章节不完整，缺少信号摘要或改进建议条目（须含「信号摘要」/「benchmark_score」+「改进建议」/「本次无新增改进建议」）"}'
    exit 1
  fi
fi

# 2) 非标准任务：显式豁免声明（接受「不纳入自进化闭环」任意前缀）
if [[ "$content" == *"不纳入自进化闭环"* ]]; then
  echo '{"ok":true,"reason":"报告显式声明不纳入自进化闭环"}'
  exit 0
fi

# 3) 既无章节又无声明 → 无法确定自进化状态，拦截
echo '{"ok":false,"reason":"未检测到「自进化反馈与改进建议」章节，也未声明「不纳入自进化闭环」，无法确定自进化状态"}'
exit 1
