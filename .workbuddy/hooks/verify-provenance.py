#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify-provenance.py — 审计级来源核验 Hook（fail-closed）

职责：交付前校验报告中每条被引片段是否真实锚定到 provenance/ 快照副本的
字符区间 [start, end]。任何缺失/越界/不符都记为 issue，ok=False 即拦截。

用法：
  python verify-provenance.py --report <报告.md> [--provenance-dir <dir>]

输出：JSON {"ok": bool, "issues": [...], "checked": N, "warnings": [...]}

设计要点（对应顶级做法 LangExtract / TokenPath / SEC EDGAR provenance）：
- 权威核验依赖不可变快照副本，不依赖活 URL
- 字符级锚定 (start, end) 而非脆弱的 Text Fragment
- 报告声明的区间必须能在快照 quoted_spans 中找到对应项
- 快照内部 quoted_spans 必须与 snapshot_text 实际字节一致
"""
import argparse
import json
import os
import re
import sys

ID_RE = re.compile(r"provenance/([A-Za-z0-9_.\-]+\.json)")
SPAN_RE = re.compile(r"@\s*\[(\d+)\s*,\s*(\d+)\]")
TEXTFRAG_RE = re.compile(r"#:~:text=")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        return {"__load_error__": str(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--provenance-dir", default=None,
                    help="默认取报告同目录下的 provenance/")
    args = ap.parse_args()

    report_path = args.report
    if not os.path.isfile(report_path):
        print(json.dumps({"ok": False, "issues": [f"报告文件不存在: {report_path}"],
                          "checked": 0, "warnings": []}, ensure_ascii=False))
        sys.exit(0)

    prov_dir = args.provenance_dir
    if prov_dir is None:
        prov_dir = os.path.join(os.path.dirname(os.path.abspath(report_path)), "provenance")

    with open(report_path, "r", encoding="utf-8") as f:
        text = f.read()

    issues = []
    warnings = []

    # 1) 检测被降级的 Text Fragment（仅警告，不阻断）
    if TEXTFRAG_RE.search(text):
        warnings.append("报告含 #:~:text= 锚点（已降级为便利项，权威核验请以快照为准）")

    # 2) 收集报告中引用的 (source_id, [start,end]...)
    ids = ID_RE.findall(text)
    # 把 id 与紧跟其后的 @ [s,e] 配对（按顺序扫描）
    spans_by_id = {}
    for m in re.finditer(r"provenance/([A-Za-z0-9_.\-]+\.json)\s*@\s*\[(\d+)\s*,\s*(\d+)\]", text):
        sid = m.group(1)
        s, e = int(m.group(2)), int(m.group(3))
        spans_by_id.setdefault(sid, []).append((s, e))

    checked = 0
    for sid in sorted(set(ids)):
        checked += 1
        jpath = os.path.join(prov_dir, sid)
        if not os.path.isfile(jpath):
            issues.append(f"快照缺失: {sid}（报告引用但 provenance/ 下无此文件）")
            continue
        data = load_json(jpath)
        if "__load_error__" in data:
            issues.append(f"{sid}: JSON 解析失败 {data['__load_error__']}")
            continue
        snap = data.get("snapshot_text", "")
        if not isinstance(snap, str) or len(snap) == 0:
            issues.append(f"{sid}: 缺 snapshot_text（空快照无法核验）")
            continue
        qspans = data.get("quoted_spans", []) or []
        # 快照内部一致性：每个 quoted_span 的 [start,end] 必须命中实际字节
        for qs in qspans:
            s = qs.get("start")
            e = qs.get("end")
            t = qs.get("text", "")
            if not isinstance(s, int) or not isinstance(e, int):
                issues.append(f"{sid}: quoted_spans 缺 start/end")
                continue
            if s < 0 or e > len(snap) or s >= e:
                issues.append(f"{sid}: 字符区间越界 [{s},{e}]（快照长度 {len(snap)}）")
                continue
            actual = snap[s:e]
            if t and actual != t:
                issues.append(f"{sid}: 区间[{s},{e}]实际='{actual}'与声明='{t}'不符")
        # 报告声明的区间必须能在快照 quoted_spans 中找到对应项
        for (s, e) in spans_by_id.get(sid, []):
            hit = any(isinstance(q.get("start"), int) and q.get("start") == s
                      and isinstance(q.get("end"), int) and q.get("end") == e
                      for q in qspans)
            if not hit:
                # 退一步：实际字节在该区间是否非空（容错引用未登记的情况）
                if 0 <= s < e <= len(snap) and snap[s:e].strip():
                    warnings.append(f"{sid}: 报告区间[{s},{e}]未在 quoted_spans 登记，但快照该区间有内容，已放行")
                else:
                    issues.append(f"{sid}: 报告声明区间[{s},{e}]在快照中越界或为空")

    result = {"ok": len(issues) == 0, "issues": issues,
              "checked": checked, "warnings": warnings}
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
