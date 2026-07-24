#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase D — fail-closed 攻击召回率测试套件（独立基准验证）

目的：把"自称顶级可信层"变成"可证顶级"。构造一批带错误的攻击样本，
统计校验脚本是否真实拦截，产出可量化的召回率与误杀率。

不依赖任何本地配置（config.local.json），零隐私、可进 CI。

用法：
  python tests/attack_suite.py
退出码：全部符合预期 → 0；存在误判 → 1
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent / ".workbuddy" / "hooks"
PY = sys.executable


def run_verify(report: Path, prov_dir: Path) -> object:
    r = subprocess.run(
        [PY, str(HOOKS / "verify-provenance.py"),
         "--report", str(report), "--provenance-dir", str(prov_dir)],
        capture_output=True, text=True)
    try:
        return json.loads(r.stdout).get("ok")
    except Exception:
        return None


def run_bash_check(script: str, report: Path) -> object:
    r = subprocess.run(
        ["bash", str(HOOKS / script), str(report)],
        capture_output=True, text=True)
    try:
        return json.loads(r.stdout).get("ok")
    except Exception:
        return None


def build_workspace(root: Path) -> Path:
    prov = root / "provenance"
    prov.mkdir(parents=True, exist_ok=True)
    # 合法快照：snapshot_text 长度 23
    (prov / "ok.json").write_text(json.dumps({
        "mode": "full", "url": "https://example.com/src1", "title": "示例来源",
        "snapshot_text": "某白酒龙头2025年营收增长15%且毛利率提升",
        "quoted_spans": [{"start": 0, "end": 5, "text": "某白酒龙头"}]
    }, ensure_ascii=False), encoding="utf-8")
    # 越界 quoted_spans（snapshot_text 仅 3 字符）
    (prov / "oob_span.json").write_text(json.dumps({
        "snapshot_text": "短文本",
        "quoted_spans": [{"start": 0, "end": 999, "text": "x"}]
    }, ensure_ascii=False), encoding="utf-8")
    # 字节与声明不符
    (prov / "mismatch.json").write_text(json.dumps({
        "snapshot_text": "短文本",
        "quoted_spans": [{"start": 0, "end": 2, "text": "XY"}]
    }, ensure_ascii=False), encoding="utf-8")
    # nope.json 故意不创建（模拟缺失快照）
    return prov


def main():
    tmp = Path(tempfile.mkdtemp(prefix="attack_"))
    prov = build_workspace(tmp)

    cases = []
    # 基线：合法报告应放行（ok=True）
    good = tmp / "good.md"
    good.write_text("结论：某白酒龙头表现稳健（快照：provenance/ok.json @ [0,6]）",
                    encoding="utf-8")
    cases.append(("baseline_合法应放行", run_verify(good, prov), True, "verify"))

    # 攻击A：引用不存在的快照
    a = tmp / "a_missing.md"
    a.write_text("结论：X（快照：provenance/nope.json @ [0,6]）", encoding="utf-8")
    cases.append(("A_快照缺失应拦截", run_verify(a, prov), False, "verify"))

    # 攻击B：快照内部 quoted_spans 越界
    b = tmp / "b_oobspan.md"
    b.write_text("结论：X（快照：provenance/oob_span.json @ [0,6]）", encoding="utf-8")
    cases.append(("B_快照内区间越界应拦截", run_verify(b, prov), False, "verify"))

    # 攻击C：快照字节与声明不符
    c = tmp / "c_mismatch.md"
    c.write_text("结论：X（快照：provenance/mismatch.json @ [0,2]）", encoding="utf-8")
    cases.append(("C_快照字节与声明不符应拦截", run_verify(c, prov), False, "verify"))

    # 攻击D：报告声明区间在快照中越界
    d = tmp / "d_oobref.md"
    d.write_text("结论：X（快照：provenance/ok.json @ [0,999]）", encoding="utf-8")
    cases.append(("D_报告声明区间越界应拦截", run_verify(d, prov), False, "verify"))

    # 攻击E：有结论性表述但无推导链标记
    e = tmp / "e_nochain.md"
    e.write_text("结论：推荐买入该标的。", encoding="utf-8")
    cases.append(("E_结论无推导链应拦截",
                  run_bash_check("check-derivation-chain.sh", e), False, "derivation"))

    # 攻击F：缺第13章「可执行推理与变量空间」
    f = tmp / "f_nocode.md"
    f.write_text("## 第一章\n一些定性描述。结论：中性。", encoding="utf-8")
    cases.append(("F_缺可执行推理章节应拦截",
                  run_bash_check("check-code-agent.sh", f), False, "codeagent"))

    # 不误杀G：引用区间未登记但快照该区间确有内容 → 应放行（warning 不 issue）
    g = tmp / "g_tolerant.md"
    g.write_text("结论：某白酒龙头（快照：provenance/ok.json @ [7,13]）", encoding="utf-8")
    cases.append(("G_未登记但快照有内容应放行", run_verify(g, prov), True, "verify"))

    total = len(cases)
    correct = sum(1 for (_, got, exp, _) in cases if got == exp)
    attacks = [c for c in cases if c[2] is False]
    atk_total = len(attacks)
    atk_blocked = sum(1 for (_, got, exp, _) in attacks if got == exp)
    fn = [n for (n, got, exp, _) in attacks if got != exp]
    fp = [n for (n, got, exp, _) in cases if got != exp and exp is True]

    summary = {
        "total_cases": total,
        "all_correct": correct,
        "attack_recall": f"{atk_blocked}/{atk_total}",
        "attack_recall_rate": round(atk_blocked / atk_total, 4) if atk_total else None,
        "false_negatives": fn,
        "false_positives": fp,
        "details": [{"case": n, "got": got, "expected": exp, "match": got == exp}
                    for (n, got, exp, _) in cases],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if correct == total else 1)


if __name__ == "__main__":
    main()
