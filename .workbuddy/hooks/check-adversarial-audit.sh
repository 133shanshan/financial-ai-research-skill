#!/usr/bin/env bash
# check-adversarial-audit.sh — 对抗性审计章节 fail-closed 校验（v3.1.0 新增）
# 用法：check-adversarial-audit.sh <report.md>
# 校验报告含「对抗性审计/反方审计」章节且至少含一条挑战记录；
# 缺失即 ok:false 且退出码非 0（fail-closed 拦截），报告不得交付。
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

# 分级豁免（v3.12.0）：T1 轻量档经 references/tiering.md 判定跳过反方审计时，
# 报告写入豁免声明即视为通过（与 G10/G11/G12/G13 豁免机制一致），不阻断投递。
if [[ "$content" == *"本报告不纳入对抗性审计"* ]]; then
  echo '{"ok":true,"reason":"反方审计按 tiering.md 分级豁免（含豁免声明），放行","skipped":true}'
  exit 0
fi

# 检测「对抗性审计」或「反方审计」章节标题（bash 内置匹配，规避中文 UTF-8 grep 坑）
has_audit_section=false
if [[ "$content" == *"对抗性审计"* ]] || [[ "$content" == *"反方审计"* ]]; then
  has_audit_section=true
fi

# 检测至少一条挑战记录
has_challenge=false
if [[ "$content" == *"挑战#"* ]] || [[ "$content" == *"挑战："* ]] || [[ "$content" == *"CH-"* ]] || [[ "$content" == *"challenges"* ]]; then
  has_challenge=true
fi

if [ "$has_audit_section" = true ] && [ "$has_challenge" = true ]; then
  echo '{"ok":true,"reason":"对抗性审计章节与至少一条挑战记录齐全","has_audit_section":true,"has_challenge":true}'
  exit 0
else
  missing=""
  [ "$has_audit_section" = false ] && missing="${missing}缺失对抗性审计章节;"
  [ "$has_challenge" = false ] && missing="${missing}缺失挑战记录;"
  echo "{\"ok\":false,\"reason\":\"${missing}报告未经对抗审计不得交付\",\"has_audit_section\":$has_audit_section,\"has_challenge\":$has_challenge}"
  exit 1
fi
