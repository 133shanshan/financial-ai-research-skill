#!/usr/bin/env bash
# 第九道 fail-closed 校验（v3.7.0）：状态化多轮下钻（stateful-drilldown）
# 规则：
#   多轮会话（含「多轮下钻与会话状态」章节）→ 须含问题树/迭代条目（turn/轮次/焦点/增量结论 任一），否则拦截
#   单轮会话 → 须显式声明「单轮一次性产出，无多轮下钻」，否则拦截
#   既无多轮章节又无单轮声明 → 拦截
# 用 bash 内置 [[ ]] 模糊匹配规避中文 UTF-8 失配（grep 在部分环境下不稳定）
set -uo pipefail

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo '{"ok":false,"reason":"usage: check-stateful-drilldown.sh <report.md>"}'
  exit 1
fi

content=$(cat "$FILE" 2>/dev/null)
if [ -z "$content" ]; then
  echo '{"ok":false,"reason":"报告文件为空，无法校验会话状态"}'
  exit 1
fi

# 1) 多轮会话：含「多轮下钻与会话状态」章节
if [[ "$content" == *"多轮下钻与会话状态"* ]]; then
  # 章节须含问题树/迭代条目（turn/轮次/T1/焦点/增量结论 任一）
  if [[ "$content" == *"turn"* || "$content" == *"轮次"* || "$content" == *"T1"* || "$content" == *"焦点"* || "$content" == *"增量结论"* ]]; then
    echo '{"ok":true,"reason":"多轮会话含「多轮下钻与会话状态」章节且含问题树/迭代条目"}'
    exit 0
  fi
  # 章节存在但无多轮标记 → 继续检查单轮豁免声明（不在这一步退出）
fi

# 2) 单轮会话：显式豁免声明
if [[ "$content" == *"单轮一次性产出，无多轮下钻"* ]]; then
  echo '{"ok":true,"reason":"单轮会话显式声明无多轮下钻"}'
  exit 0
fi

# 3) 既无多轮章节又无单轮声明 → 无法确定会话状态，拦截
echo '{"ok":false,"reason":"未检测到「多轮下钻与会话状态」章节，也未声明「单轮一次性产出，无多轮下钻」，无法确定会话状态"}'
exit 1
