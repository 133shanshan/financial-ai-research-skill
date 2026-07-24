#!/usr/bin/env bash
# check-output-format.sh — 校验报告文件格式（v3.1.0 基础版）
# 用法：bash check-output-format.sh <报告文件>
# 说明：原 skill 在 report-writer.md 中引用本脚本，但此前未落地，本次补齐。
# 输出：JSON {ok, format}
set -u

FILE="${1:-}"
if [ -z "$FILE" ]; then
  echo '{"ok":false,"error":"usage: check-output-format.sh <file>"}'
  exit 1
fi

case "$FILE" in
  *.docx|*.pdf) echo "{\"ok\":true,\"format\":\"${FILE##*.}\"}" ;;
  *) echo '{"ok":false,"format":"unknown","hint":"报告应为 .docx 或 .pdf"}' ;;
esac
