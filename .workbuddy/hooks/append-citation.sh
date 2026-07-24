#!/usr/bin/env bash
# append-citation.sh — 数据来源四要素校验/补全（v3.1.0：四要素 + 快照锚定占位）
# 用法：bash append-citation.sh <报告底稿.md>
# 行为：若报告含『数据来源』块则校验四要素是否齐全；若完全缺失则追加四要素+快照模板块。
# 输出：JSON 状态，供 report-writer 在交付前读取。
set -u

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo '{"ok":false,"error":"usage: append-citation.sh <file>"}'
  exit 1
fi

# 读取全文到变量，使用 bash 内置匹配，避免 git-bash grep 对 UTF-8 中文文件的编码坑
content=$(cat "$FILE" 2>/dev/null || true)

if [[ "$content" == *"数据来源"* ]]; then
  # 已有来源块，仅校验四要素
  miss=()
  [[ "$content" == *"数据获取时间"* ]] || miss+=("获取时间")
  [[ "$content" == *"口径"* ]] || [[ "$content" == *"定义"* ]] || miss+=("口径/定义")
  [[ "$content" == *"关键假设"* ]] || miss+=("关键假设")
  if [ "${#miss[@]}" -eq 0 ]; then
    echo '{"ok":true,"action":"already_present","missing":[]}'
  else
    printf '{"ok":false,"action":"present_incomplete","missing":['
    first=1
    for m in "${miss[@]}"; do
      [ "$first" -eq 0 ] && printf ','
      printf '"%s"' "$m"
      first=0
    done
    printf ']}'
    echo
  fi
else
  {
    echo ""
    echo "---"
    echo "【数据来源】"
    echo "- 数据来源：[来源名称](URL) — URL 为便利核验链接"
    echo "- 快照索引：provenance/<source_id>.json  # 抓取时存档的不可变副本"
    echo "- 被引片段：{被引用原文} @ [start_char, end_char]  # 锚定到快照字符区间"
    echo "- 数据获取时间：YYYY-MM-DD HH:MM:SS"
    echo "- 数据口径/定义：{指标口径说明，如\"LPR 为贷款市场报价利率，分 1 年期/5 年期以上\"}"
    echo "- 关键假设：{分析所依赖的关键假设，如\"以公报发布日版本为准，不含后续解读\"}"
  } >> "$FILE"
  echo '{"ok":true,"action":"appended","missing":[]}'
fi
