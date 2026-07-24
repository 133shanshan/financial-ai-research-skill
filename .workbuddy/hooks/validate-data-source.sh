#!/usr/bin/env bash
# validate-data-source.sh — 校验数据来源四要素 + 链接可核验 + 快照锚定（v3.1.0）
# 用法：bash validate-data-source.sh <报告底稿.md>
# 输出：JSON {ok, issues[], verifiable, precise}
set -u

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo '{"ok":false,"error":"usage: validate-data-source.sh <file>"}'
  exit 1
fi

# 读取全文到变量，使用 bash 内置匹配，避免 git-bash grep 对 UTF-8 中文文件的编码坑
content=$(cat "$FILE" 2>/dev/null || true)

issues=()
[[ "$content" == *"数据来源"* ]] || issues+=("缺『数据来源』")
[[ "$content" == *"获取时间"* ]] || issues+=("缺『获取时间』")
[[ "$content" == *"口径"* ]] || [[ "$content" == *"定义"* ]] || issues+=("缺『口径/定义』")
[[ "$content" == *"假设"* ]] || issues+=("缺『关键假设』")

# 来源可核验性（软性检查：不阻断交付，仅提示）
if [[ "$content" == *"http"* ]]; then
  verifiable=true
else
  verifiable=false
fi

# 快照锚定（权威核验）：含 provenance/ 引用视为已锚定到不可变副本（更优）
if [[ "$content" == *"provenance/"* ]]; then
  anchored=true
else
  anchored=false
fi

# Text Fragment 锚点（已降级为便利项，仅提示不阻断）
if [[ "$content" == *"#:~:text="* ]]; then
  textfragment=true
else
  textfragment=false
fi

if [ "${#issues[@]}" -eq 0 ]; then
  echo "{\"ok\":true,\"issues\":[],\"verifiable\":$verifiable,\"anchored\":$anchored,\"textfragment\":$textfragment}"
else
  printf '{"ok":false,"issues":['
  first=1
  for i in "${issues[@]}"; do
    [ "$first" -eq 0 ] && printf ','
    printf '"%s"' "$i"
    first=0
  done
  printf '],"verifiable":%s,"anchored":%s,"textfragment":%s}' "$verifiable" "$anchored" "$textfragment"
  echo
fi
