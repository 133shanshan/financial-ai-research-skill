#!/usr/bin/env bash
# check-resilience-declaration.sh — 流程韧性声明 fail-closed 校验（v3.3.0 新增）
# 用法：check-resilience-declaration.sh <report.md>
# 校验报告含「流程韧性声明」章节，且该章节须含事件明细（事件类型/模块/重试次数/处置/对结论影响）
#   或声明「本次研究全流程未触发重试或降级」；缺失章节或空章节即 ok:false 且退出码非 0（fail-closed 拦截），报告不得交付。
# 与四道既有质量校验（provenance / 推导链 / 反方审计 / 自评估质量门）正交，本道为第五道。
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
if [[ "$content" == *"流程韧性声明"* ]]; then has_sec=true; fi

if [ "$has_sec" = false ]; then
  echo '{"ok":false,"reason":"报告缺失「流程韧性声明」章节（v3.3.0 强制），不得交付","has_section":false}'
  exit 1
fi

# 章节需含事件明细字段，或显式声明全流程无失败
has_detail=false
if [[ "$content" == *"事件类型"* ]] || [[ "$content" == *"模块"* ]] || [[ "$content" == *"重试次数"* ]] || [[ "$content" == *"处置"* ]] || [[ "$content" == *"对结论影响"* ]]; then
  has_detail=true
fi

has_clean=false
if [[ "$content" == *"未触发重试或降级"* ]]; then has_clean=true; fi

if [ "$has_detail" = true ] || [ "$has_clean" = true ]; then
  echo '{"ok":true,"reason":"「流程韧性声明」章节齐全（含事件明细或全流程无失败声明）","has_section":true}'
  exit 0
else
  echo '{"ok":false,"reason":"「流程韧性声明」章节为空：既无事件明细也无「未触发重试或降级」声明，不得交付","has_section":true,"empty_section":true}'
  exit 1
fi
