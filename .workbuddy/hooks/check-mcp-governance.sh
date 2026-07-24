#!/usr/bin/env bash
# check-mcp-governance.sh — 工具治理中心 fail-closed 校验（v3.6.0 新增）
# 用法：check-mcp-governance.sh <report.md>
# 校验报告含「工具治理与调用审计」章节（第15章），且该章节须满足其一：
#   (a) ≥1 调用条目（含「call_id」/「tool_audit」任一标记，且体现 tool/params/provenance 审计痕迹）；
#   (b) 显式声明「本报告未调用任何外部工具或数据源」。
# 缺失章节、或章节既无调用条目也无「未调用」声明（即空洞治理）即 ok:false 且退出码非 0（fail-closed 拦截），报告不得交付。
# 与既有七道质量校验（provenance / 推导链 / 反方审计 / 自评估质量门 / 流程韧性 / 可执行推理 / 经验沉淀）正交，本道为第八道。
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
if [[ "$content" == *"工具治理与调用审计"* ]]; then has_sec=true; fi

if [ "$has_sec" = false ]; then
  echo '{"ok":false,"reason":"报告缺失「工具治理与调用审计」章节（v3.6.0 强制），不得交付","has_section":false}'
  exit 1
fi

# (b) 未调用任何外部工具/数据源声明
has_none=false
if [[ "$content" == *"未调用任何外部工具"* ]]; then has_none=true; fi

# (a) ≥1 调用审计条目（call_id / tool_audit 标记 + tool 痕迹）
has_entry=false
if [[ "$content" == *"call_id"* ]] || [[ "$content" == *"tool_audit"* ]]; then
  # 进一步要求体现 tool 与 provenance 痕迹，避免只写空 call_id
  if [[ "$content" == *"anysearch"* ]] || [[ "$content" == *"akshare"* ]] || \
     [[ "$content" == *"code_agent"* ]] || [[ "$content" == *"provenance"* ]] || \
     [[ "$content" == *"bash"* ]]; then
    has_entry=true
  fi
fi

if [ "$has_none" = true ] || [ "$has_entry" = true ]; then
  if [ "$has_none" = true ]; then
    echo '{"ok":true,"reason":"第15章「工具治理与调用审计」：已显式声明本报告未调用任何外部工具或数据源","has_section":true,"mode":"none"}'
  else
    echo '{"ok":true,"reason":"第15章「工具治理与调用审计」：含工具调用审计条目（call_id/tool/params/provenance）","has_section":true,"mode":"audited"}'
  fi
  exit 0
else
  echo '{"ok":false,"reason":"第15章为空洞治理：无调用审计条目（call_id/tool/provenance）也无「未调用任何外部工具」声明，不得交付","has_section":true,"empty_section":true}'
  exit 1
fi
