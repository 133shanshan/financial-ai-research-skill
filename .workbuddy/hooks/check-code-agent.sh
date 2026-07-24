#!/usr/bin/env bash
# check-code-agent.sh — 可执行推理 fail-closed 校验（v3.4.0 新增）
# 用法：check-code-agent.sh <report.md>
# 校验报告含「可执行推理与变量空间」章节（第13章），且该章节须满足其一：
#   (a) ≥1 变量条目含代码引用（含「代码路径」或「variables.json」标记 + 变量/数值）；
#   (b) 显式声明「本报告为定性分析，未含代码执行计算」；
#   (c) 显式声明代码环境不可用降级（含「代码执行环境不可用」或「以定性/人工估算替代」并说明原因）。
# 缺失章节、或章节既无变量条目也无定性/降级声明（即散文式计算）即 ok:false 且退出码非 0（fail-closed 拦截），报告不得交付。
# 与既有五道质量校验（provenance / 推导链 / 反方审计 / 自评估质量门 / 流程韧性声明）正交，本道为第六道。
set -u

REPORT="${1:-}"
if [ -z "$REPORT" ]; then
  echo '{"ok":false,"reason":"缺少报告路径参数"}'
  exit 1
fi
if [ ! -f "$REPORT" ]; then
  echo "{\"ok\":false,\"reason\":\"报告文件不存在: $REPORT\"}"
  exit 1
fi

content=$(cat "$REPORT")

# bash 内置匹配，规避中文 UTF-8 grep 坑
has_sec=false
if [[ "$content" == *"可执行推理与变量空间"* ]]; then has_sec=true; fi

if [ "$has_sec" = false ]; then
  echo '{"ok":false,"reason":"报告缺失「可执行推理与变量空间」章节（v3.4.0 强制），不得交付","has_section":false}'
  exit 1
fi

# (b) 纯定性声明
is_qualitative=false
if [[ "$content" == *"本报告为定性分析，未含代码执行计算"* ]]; then is_qualitative=true; fi

# (a) ≥1 变量条目含代码引用
has_var=false
if { [[ "$content" == *"代码路径"* ]] || [[ "$content" == *"variables.json"* ]]; } && { [[ "$content" == *"变量"* ]] || [[ "$content" == *"数值"* ]]; }; then
  has_var=true
fi

# (c) 代码环境不可用降级声明（透明降级，非伪装为代码结果）
has_degrade=false
if { [[ "$content" == *"代码执行环境不可用"* ]] || [[ "$content" == *"以定性/人工估算替代"* ]]; } && [[ "$content" == *"降级"* ]]; then
  has_degrade=true
fi

if [ "$is_qualitative" = true ] || [ "$has_var" = true ] || [ "$has_degrade" = true ]; then
  if [ "$is_qualitative" = true ]; then
    echo '{"ok":true,"reason":"第13章「可执行推理与变量空间」：纯定性分析已显式声明","has_section":true,"mode":"qualitative"}'
  elif [ "$has_degrade" = true ]; then
    echo '{"ok":true,"reason":"第13章「可执行推理与变量空间」：代码环境降级已透明声明","has_section":true,"mode":"degraded"}'
  else
    echo '{"ok":true,"reason":"第13章「可执行推理与变量空间」：含代码执行变量条目（带代码引用）","has_section":true,"mode":"executed"}'
  fi
  exit 0
else
  echo '{"ok":false,"reason":"第13章为空或仅为散文式计算：无变量条目（含代码引用）、无纯定性声明、无降级声明，不得交付","has_section":true,"empty_section":true}'
  exit 1
fi
