#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase D — 推导链逻辑正确性测试套件（独立基准验证 · D2）

D1 验证的是"格式/锚定/章节完整性"（G1 + G2 存在性 + G6）。
本套件补上 G2 的"逻辑正确性"维度：推导链是否真的成立——
证据 → 计算 → 结论 三环是否自洽、有无跳跃/数值矛盾/证据造假。

设计：构造一批带逻辑缺陷的攻击样本，用轻量 checker 统计真实拦截率。
与 D1 同构，可机器复现、不依赖本地配置（config.local.json），零隐私、可进 CI。

可选重负载：KNOWN_ANSWER_QUESTIONS 内置"已知答案题集"（标准推导+标准答案），
供 LLM 判分使用（grade_known_answer 接口）。CI 默认不跑该项（避免依赖外部模型）。

用法：
  python tests/derivation_suite.py
退出码：全部符合预期 → 0；存在误判 → 1
"""
import json
import re
import sys
import tempfile
from pathlib import Path

PY = sys.executable


# ---------------------------------------------------------------------------
# 推导链 checker：机器可验证的逻辑正确性检查
# ---------------------------------------------------------------------------
def check_derivation(text: str, prov_ids: set) -> bool:
    """返回 True=放行（推导链自洽或无需推导链），False=拦截（存在逻辑缺陷）。

    规则（保守、稳健，避免误杀）：
      1. 既无「计算:」也无「结论:」→ 视为定性报告，不要求推导链 → 放行
      2. 有「结论:」但无「计算:」→ 跳跃推导（缺计算步骤）→ 拦截
      3. 有「计算:」→ 提取计算结果数值，结论中必须出现该数值 → 否则拦截
      4. 引用 [E#] 但未在「证据:」段声明且不在 provenance → 证据造假 → 拦截
    """
    has_calc = bool(re.search(r'计算\s*[:：]', text))
    has_conclusion = bool(re.search(r'结论\s*[:：]', text))

    # 1. 无推导链意图 → 放行（不误杀定性报告）
    if not has_calc and not has_conclusion:
        return True

    # 2. 有结论但无计算 → 跳跃推导
    if has_conclusion and not has_calc:
        return False

    # 3. 有计算 → 提取结果数值，结论须包含它
    calc_val = None
    m = re.search(r'计算\s*[:：][^\n]*?=\s*([\d.]+)\s*%?', text)
    if m:
        calc_val = float(m.group(1))
    if calc_val is not None:
        concl_part = text.split('结论', 1)[1]
        concl_nums = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)', concl_part)]
        if not any(abs(n - calc_val) < 0.01 for n in concl_nums):
            return False  # 计算与结论数值不符 → 拦截

    # 4. 证据造假：[E#] 引用须已声明或在 provenance
    refs = set(int(x) for x in re.findall(r'\[E(\d+)\]', text))
    declared = set(int(x) for x in re.findall(r'证据\s*[:：]\s*E(\d+)', text))
    if refs - declared and not (refs - declared).issubset(prov_ids):
        return False  # 引用未声明且不在 provenance → 拦截

    return True


# ---------------------------------------------------------------------------
# 已知答案题集（供 LLM 判分，不进 CI）
# ---------------------------------------------------------------------------
KNOWN_ANSWER_QUESTIONS = [
    {
        "id": "ka_bond_price",
        "question": "某债券面值100元、票面利率5%、每年付息、剩余期限2年、市场YTM=6%，求其理论价格。",
        "standard_derivation": "P = 5/(1.06) + 105/(1.06)^2 = 4.717 + 93.448 = 98.165 元",
        "expected_answer": 98.165,
        "tolerance": 0.5,
    },
    {
        "id": "ka_pe_ratio",
        "question": "某公司股价30元、每股收益2元，求市盈率(PE)。",
        "standard_derivation": "PE = 股价 / EPS = 30 / 2 = 15 倍",
        "expected_answer": 15.0,
        "tolerance": 0.1,
    },
    {
        "id": "ka_bayes",
        "question": "某事件先验概率10%；若事件发生时某指标出现概率90%，不发生时出现概率20%。现指标出现，求事件发生后验概率。",
        "standard_derivation": "P(A|B)=P(B|A)P(A)/(P(B|A)P(A)+P(B|¬A)P(¬A))=0.9*0.1/(0.9*0.1+0.2*0.9)=0.09/0.27=1/3≈33.3%",
        "expected_answer": 33.3,
        "tolerance": 1.0,
    },
]


def grade_known_answer(question: dict, report_text: str) -> dict:
    """LLM 判分接口（占位）。真实环境应由 LLM 读取 report_text，
    提取其最终数值结论并与 expected_answer ± tolerance 比对。
    此处仅做数值正则提取的初级判分，供离线冒烟；CI 不调用本函数。"""
    nums = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)', report_text)]
    exp = question["expected_answer"]
    tol = question["tolerance"]
    hit = any(abs(n - exp) <= tol for n in nums)
    return {"id": question["id"], "expected": exp, "tolerance": tol,
            "extracted_nums": nums[:5], "pass": hit}


# ---------------------------------------------------------------------------
# 攻击样本与基线
# ---------------------------------------------------------------------------
def main():
    tmp = Path(tempfile.mkdtemp(prefix="deriv_"))
    # provenance 中存在的快照 id（对应合法证据 E1）
    prov_ids = {"1"}

    cases = []

    # 基线1：合法推导链应放行（证据 E1 + 计算 15% + 结论含 15%）
    ok = tmp / "ok.md"
    ok.write_text(
        "## 推导链\n证据 E1: provenance/ok.json 显示营收100→115\n"
        "计算: 营收增长率 = (115-100)/100 = 15%\n结论: 营收增长15%，表现稳健。",
        encoding="utf-8")
    cases.append(("baseline_合法推导链应放行",
                  check_derivation(ok.read_text(encoding="utf-8"), prov_ids),
                  True))

    # 基线2：纯定性报告（无计算无结论）→ 不要求推导链 → 放行（不误杀）
    qual = tmp / "qual.md"
    qual.write_text("宏观环境整体偏中性，流动性合理充裕，需关注后续政策节奏。",
                    encoding="utf-8")
    cases.append(("baseline_定性报告应放行",
                  check_derivation(qual.read_text(encoding="utf-8"), prov_ids),
                  True))

    # 攻击A：跳跃推导（有结论无计算）
    a = tmp / "a_jump.md"
    a.write_text("## 推导链\n证据 E1: provenance/ok.json\n结论: 营收增长25%，强烈推荐买入。",
                 encoding="utf-8")
    cases.append(("A_跳跃推导应拦截",
                  check_derivation(a.read_text(encoding="utf-8"), prov_ids),
                  False))

    # 攻击B：计算与结论数值不符（计算15%但结论写25%）
    b = tmp / "b_mismatch.md"
    b.write_text(
        "## 推导链\n证据 E1: provenance/ok.json 营收100→115\n"
        "计算: 增长率 = (115-100)/100 = 15%\n结论: 营收增长25%，超预期。",
        encoding="utf-8")
    cases.append(("B_计算结论不符应拦截",
                  check_derivation(b.read_text(encoding="utf-8"), prov_ids),
                  False))

    # 攻击C：证据造假（结论引用 [E9] 但未声明且无快照）
    c = tmp / "c_fake.md"
    c.write_text(
        "## 推导链\n证据 E1: provenance/ok.json\n"
        "计算: 指标 = 80%\n结论: 依据 [E9] 显示该指标达80%，看多。",
        encoding="utf-8")
    cases.append(("C_证据造假应拦截",
                  check_derivation(c.read_text(encoding="utf-8"), prov_ids),
                  False))

    # 攻击D：有计算但结论完全不出现计算结果（另一种不符）
    d = tmp / "d_missing_num.md"
    d.write_text(
        "## 推导链\n证据 E1: provenance/ok.json 营收100→115\n"
        "计算: 增长率 = (115-100)/100 = 15%\n结论: 营收明显改善，趋势向好。",
        encoding="utf-8")
    cases.append(("D_结论缺计算结果应拦截",
                  check_derivation(d.read_text(encoding="utf-8"), prov_ids),
                  False))

    total = len(cases)
    correct = sum(1 for (_, got, exp) in cases if got == exp)
    attacks = [c for c in cases if c[2] is False]
    atk_total = len(attacks)
    atk_blocked = sum(1 for (_, got, exp) in attacks if got == exp)
    fn = [n for (n, got, exp) in attacks if got != exp]
    fp = [n for (n, got, exp) in cases if got != exp and exp is True]

    summary = {
        "total_cases": total,
        "all_correct": correct,
        "attack_recall": f"{atk_blocked}/{atk_total}",
        "attack_recall_rate": round(atk_blocked / atk_total, 4) if atk_total else None,
        "false_negatives": fn,
        "false_positives": fp,
        "known_answer_questions": len(KNOWN_ANSWER_QUESTIONS),
        "details": [{"case": n, "got": got, "expected": exp, "match": got == exp}
                    for (n, got, exp) in cases],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if correct == total else 1)


if __name__ == "__main__":
    main()
