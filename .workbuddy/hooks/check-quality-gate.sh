#!/usr/bin/env bash
# check-quality-gate.sh — 自评估质量门 fail-closed 校验（v3.2.0 新增）
# 用法：check-quality-gate.sh <report.md>
# 校验报告含「自评估质量门」章节 + 三维度标签（定性严谨度/定量准确度/可验证性）+ verdict 字段且非 block；
# 缺失结构或 verdict=block 即 ok:false 且退出码非 0（fail-closed 拦截），报告不得交付。
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
has_qg=false
if [[ "$content" == *"自评估质量门"* ]]; then has_qg=true; fi

has_d1=false
if [[ "$content" == *"定性严谨度"* ]]; then has_d1=true; fi

has_d2=false
if [[ "$content" == *"定量准确度"* ]]; then has_d2=true; fi

has_d3=false
if [[ "$content" == *"可验证性"* ]]; then has_d3=true; fi

has_verdict=false
if [[ "$content" == *"verdict"* ]] || [[ "$content" == *"pass"* ]] || [[ "$content" == *"amber"* ]] || [[ "$content" == *"block"* ]]; then
  has_verdict=true
fi

# 检测 verdict=block（verdict 标记出现在 block 之前，覆盖 JSON "verdict":"block" 与 prose）
is_block=false
if [[ "$content" == *"verdict"*"block"* ]]; then is_block=true; fi

if [ "$has_qg" = true ] && [ "$has_d1" = true ] && [ "$has_d2" = true ] && [ "$has_d3" = true ] && [ "$has_verdict" = true ]; then
  if [ "$is_block" = true ]; then
    echo '{"ok":false,"reason":"自评估 verdict=block，报告未达质量门，拦截交付","has_qg_section":true,"three_dimensions":true,"verdict":"block"}'
    exit 1
  fi
  echo '{"ok":true,"reason":"自评估质量门章节与三维度评分齐全且 verdict 非 block","has_qg_section":true,"three_dimensions":true}'
  exit 0
else
  missing=""
  [ "$has_qg" = false ] && missing="${missing}缺失自评估质量门章节;"
  [ "$has_d1" = false ] && missing="${missing}缺失维度[定性严谨度];"
  [ "$has_d2" = false ] && missing="${missing}缺失维度[定量准确度];"
  [ "$has_d3" = false ] && missing="${missing}缺失维度[可验证性];"
  [ "$has_verdict" = false ] && missing="${missing}缺失verdict字段;"
  echo "{\"ok\":false,\"reason\":\"${missing}报告未经自评估质量门不得交付\",\"has_qg_section\":$has_qg,\"three_dimensions\":$([ "$has_d1" = true ] && [ "$has_d2" = true ] && [ "$has_d3" = true ] && echo true || echo false)}"
  exit 1
fi
