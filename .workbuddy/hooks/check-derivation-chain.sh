#!/usr/bin/env bash
# check-derivation-chain.sh — 交付前拦截缺「证据→计算→结论」三段链的报告（v3.1.0）
# 用法：bash check-derivation-chain.sh <报告底稿.md>
# 启发式：若文档含结论性表述但未见任一推导链标记（[证据]/[计算]/[结论]/推导链），则判定缺失。
# 输出：JSON {ok, missing[]}
# 注意：使用 bash 内置字符串匹配，规避 MinGW grep 对中文 UTF-8 的编码坑。
set -u

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo '{"ok":false,"error":"usage: check-derivation-chain.sh <file>"}'
  exit 1
fi

content=$(cat "$FILE" 2>/dev/null)
if [ -z "$content" ]; then
  echo '{"ok":false,"missing":["文件为空"]}'
  exit 0
fi

missing=()

# 检测 1：是否有结论性表述
has_conclusion=false
for kw in "结论" "推荐" "判断" "取向" "配置建议" "信号"; do
  if [[ "$content" == *"$kw"* ]]; then
    has_conclusion=true
    break
  fi
done

# 检测 2：是否有推导链标记（[证据]/[计算]/[结论] 或 "推导链" 关键词）
has_chain=false
for kw in "[证据]" "[计算]" "[结论]" "推导链" "证据→计算→结论"; do
  if [[ "$content" == *"$kw"* ]]; then
    has_chain=true
    break
  fi
done

# 检测 3：同时包含"证据""计算""结论"三个关键词（粒度更粗的兜底）
has_all_three=false
if [[ "$content" == *"证据"* ]] && [[ "$content" == *"计算"* ]] && [[ "$content" == *"结论"* ]]; then
  has_all_three=true
fi

# 判定逻辑
if $has_conclusion && ! $has_chain && ! $has_all_three; then
  missing+=("文档含结论性表述但未见推导链标记（[证据]/[计算]/[结论] 或『推导链』关键词）")
fi

if [ "${#missing[@]}" -eq 0 ]; then
  echo '{"ok":true,"missing":[]}'
else
  printf '{"ok":false,"missing":['
  first=1
  for m in "${missing[@]}"; do
    [ "$first" -eq 0 ] && printf ','
    printf '"%s"' "$m"
    first=0
  done
  printf ']}\n'
fi
