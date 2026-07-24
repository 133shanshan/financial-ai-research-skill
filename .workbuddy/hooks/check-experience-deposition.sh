#!/usr/bin/env bash
# check-experience-deposition.sh — 经验沉淀 fail-closed 校验（v3.5.0 新增）
# 用法：check-experience-deposition.sh <report.md>
# 校验报告含「经验沉淀与复用」章节（第14章），且该章节须满足其一：
#   (a) ≥1 经验条目（含「避坑清单」/「标的研判模板」/「行业框架」任一标记或其 experience/ 路径）；
#   (b) 显式声明「本次无新增可复用经验」。
# 缺失章节、或章节既无经验条目也无「无新增」声明（即空洞沉淀）即 ok:false 且退出码非 0（fail-closed 拦截），报告不得交付。
# 与既有六道质量校验（provenance / 推导链 / 反方审计 / 自评估质量门 / 流程韧性声明 / 可执行推理）正交，本道为第七道。
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
if [[ "$content" == *"经验沉淀与复用"* ]]; then has_sec=true; fi

if [ "$has_sec" = false ]; then
  echo '{"ok":false,"reason":"报告缺失「经验沉淀与复用」章节（v3.5.0 强制），不得交付","has_section":false}'
  exit 1
fi

# (b) 本次无新增可复用经验声明
has_none=false
if [[ "$content" == *"本次无新增可复用经验"* ]]; then has_none=true; fi

# (a) ≥1 经验条目（三类卡片标记或其路径）
has_entry=false
if [[ "$content" == *"避坑清单"* ]] || [[ "$content" == *"lessons-learned"* ]] || \
   [[ "$content" == *"标的研判模板"* ]] || [[ "$content" == *"asset-templates"* ]] || \
   [[ "$content" == *"行业框架"* ]] || [[ "$content" == *"industry-frameworks"* ]]; then
  has_entry=true
fi

if [ "$has_none" = true ] || [ "$has_entry" = true ]; then
  if [ "$has_none" = true ]; then
    echo '{"ok":true,"reason":"第14章「经验沉淀与复用」：已显式声明本次无新增可复用经验","has_section":true,"mode":"none"}'
  else
    echo '{"ok":true,"reason":"第14章「经验沉淀与复用」：含可复用经验条目（避坑/标的模板/行业框架）","has_section":true,"mode":"deposited"}'
  fi
  exit 0
else
  echo '{"ok":false,"reason":"第14章为空洞沉淀：无经验条目（避坑/标的模板/行业框架）也无「本次无新增可复用经验」声明，不得交付","has_section":true,"empty_section":true}'
  exit 1
fi
