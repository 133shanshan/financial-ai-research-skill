#!/usr/bin/env bash
# 第十二道 fail-closed 校验：投决会对抗决策（v3.10.0）
# 规则：
#   1) 报告须含「投决会对抗决策与决议」章节，且含 决议条目（verdict/共识度 标记）
#      +（≥1 委员立场 或 「无委员立场记录」声明），否则拦截；
#   2) 或含「本报告不纳入投决会对抗决策」豁免声明，则放行；
#   3) 均无 → 拦截。
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

has_chapter() { [[ "$CONTENT" == *"投决会对抗决策与决议"* ]]; }
has_exempt()  { [[ "$CONTENT" == *"本报告不纳入投决会对抗决策"* ]]; }
has_verdict() { [[ "$CONTENT" == *"verdict"* ]] || [[ "$CONTENT" == *"最终决议"* ]] || [[ "$CONTENT" == *"决议："* ]]; }
has_consensus(){ [[ "$CONTENT" == *"共识度"* ]]; }
has_member()  { [[ "$CONTENT" == *"看涨委员"* ]] || [[ "$CONTENT" == *"看跌委员"* ]] || [[ "$CONTENT" == *"中性委员"* ]] || [[ "$CONTENT" == *"风控委员"* ]] || [[ "$CONTENT" == *"委员立场"* ]] || [[ "$CONTENT" == *"无委员立场记录"* ]]; }

if has_exempt; then
  echo "ok:true"
  echo "reason: 含豁免声明「本报告不纳入投决会对抗决策」，放行"
  exit 0
fi

if ! has_chapter; then
  echo "ok:false"
  echo "reason: 缺少「投决会对抗决策与决议」章节，且未声明豁免，拦截投递"
  exit 1
fi

# 有章节：检查决议条目 + 委员立场
if has_verdict && has_consensus && has_member; then
  echo "ok:true"
  echo "reason: 第19章含决议（verdict/共识度）+ 委员立场，通过第十二道校验"
  exit 0
fi

# 章节存在但内容不全
missing=""
if ! has_verdict || ! has_consensus; then missing="${missing} 决议条目(verdict/共识度)"; fi
if ! has_member; then missing="${missing} 委员立场/无委员立场记录声明"; fi
echo "ok:false"
echo "reason: 第19章「投决会对抗决策与决议」内容不全，缺少:${missing}，拦截投递"
exit 1
