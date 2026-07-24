#!/usr/bin/env bash
# 第十三道 fail-closed 校验：非结构化知识回流（v3.11.0）
# 规则：
#   1) 报告须含「非结构化知识回流」章节，且含以下任一，否则拦截：
#      a) ≥1 知识条目（分类+路径+溯源标记，如 "邮件洞察"/"source: agent-mail"）；
#      b) 「本报告未摄取外部邮件知识」声明（agent-mail 未开通/无匹配，best-effort 降级）；
#      c) 「本报告不纳入非结构化知识回流」豁免声明；
#   2) 均无 → 拦截。
# 输出 ok:true/false，并以非零退出码拦截。

set -u

FILE="${1:-}"
if [ -z "$FILE" ]; then
  echo "ok:false"
  echo "reason: 未提供报告文件路径"
  exit 1
fi
if [ ! -f "$FILE" ]; then
  echo "ok:false"
  echo "reason: 报告文件不存在: $FILE"
  exit 1
fi

CONTENT="$(cat "$FILE" 2>/dev/null || true)"

has_chapter()  { [[ "$CONTENT" == *"非结构化知识回流"* ]]; }
has_exempt()   { [[ "$CONTENT" == *"本报告不纳入非结构化知识回流"* ]]; }
has_no_mail()  { [[ "$CONTENT" == *"本报告未摄取外部邮件知识"* ]]; }
has_entry()    { [[ "$CONTENT" == *"邮件洞察"* ]] || [[ "$CONTENT" == *"asset-templates"* ]] || [[ "$CONTENT" == *"industry-frameworks"* ]] || [[ "$CONTENT" == *"lessons-learned"* ]] || [[ "$CONTENT" == *"source: agent-mail"* ]] || [[ "$CONTENT" == *"知识卡片"* ]]; }

if has_exempt; then
  echo "ok:true"
  echo "reason: 含豁免声明「本报告不纳入非结构化知识回流」，放行"
  exit 0
fi

if ! has_chapter; then
  echo "ok:false"
  echo "reason: 缺少「非结构化知识回流」章节，且未声明豁免，拦截投递"
  exit 1
fi

# 有章节：检查降级声明或知识条目
if has_no_mail || has_entry; then
  echo "ok:true"
  echo "reason: 第20章含降级声明(未摄取邮件知识)或知识条目(分类+路径+溯源)，通过第十三道校验"
  exit 0
fi

echo "ok:false"
echo "reason: 第20章「非结构化知识回流」内容不全，缺少知识条目或「未摄取邮件知识」/豁免声明，拦截投递"
exit 1
