#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_experience_to_obsidian.py — 经验→Obsidian 多源同步（零 LLM / 增量 / 规则转换）

设计目标（对齐用户"高效+省钱"诉求）：
- 把"机器可读/跨对话沉淀"半自动转成 OB「人读版」，实现机器回灌 + 人读复习双轨。
- 多源汇聚：
    ① 金融AI投研 G4 experience/（避坑清单 / 标的模板 / 行业框架）
    ② 全局 self-improve 层（SessionEnd Hook 从【每个对话+每个 skill】自动产出的
       ERRORS.md 错题本 / LEARNINGS.md 学习 / FEATURE_REQUESTS.md 需求）
    ③ 自动发现其他 skill 的 experience/ 目录（将来可扩展）
- 零 LLM 调用：纯规则解析 + 套用 OB 笔记风格模板，不烧 token。
- 增量去重：基于 .ob_sync_index.json（源路径+内容 hash），仅同步新增/变更源。
- 双向链接成网：生成笔记自动链到 10-投研框架/ 相关框架与 MOC。

用法（OB 目标库路径经配置分离，绝不写死在代码中）：
  cd <skill 根目录>/scripts
  python sync_experience_to_obsidian.py --dry-run        # 预览将同步哪些
  python sync_experience_to_obsidian.py                  # 真实同步（自动读 OB_VAULT 或 config.local.json）
  python sync_experience_to_obsidian.py --ob-target <你的 OB vault 根>/AI投研知识库   # 自定义（覆盖配置）
配置优先级：--ob-target  >  环境变量 OB_VAULT  >  skill 根目录 config.local.json（gitignored，不随仓库泄露）
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
SKILLS = HOME / '.workbuddy' / 'skills'
SELF_IMPROVE = HOME / '.workbuddy' / 'self-improve'
INDEX_NAME = '.ob_sync_index.json'

# 配置分离（12-factor）：OB 目标库路径绝不写死在代码中。
# 解析优先级：CLI --ob-target  >  环境变量 OB_VAULT  >  gitignored config.local.json
# config.local.json 位于 skill 根目录，由 .gitignore 排除，不会随仓库泄露。
SKILL_DIR = Path(__file__).resolve().parent.parent
LOCAL_CFG = SKILL_DIR / 'config.local.json'


def resolve_ob_target(cli_value):
    """解析 OB 目标库根目录；三者皆无则 fail-closed 报错退出，绝不静默写错位置。"""
    if cli_value:
        return Path(cli_value)
    env = os.environ.get('OB_VAULT')
    if env:
        return Path(env)
    if LOCAL_CFG.exists():
        try:
            data = json.loads(LOCAL_CFG.read_text(encoding='utf-8'))
            v = data.get('ob_vault')
            if v:
                return Path(v)
        except Exception as e:
            print(f'[错误] 读取 {LOCAL_CFG} 失败：{e}', file=sys.stderr)
            sys.exit(1)
    print('[错误] 未配置 OB 目标库，已停止（不会写入任何位置）。请任选其一：\n'
          '  1) 设置环境变量 OB_VAULT=你的vault路径\n'
          f'  2) 在 {LOCAL_CFG} 写入 {{"ob_vault": "你的vault路径"}}'
          '（该文件已被 .gitignore 排除）\n'
          '  3) 用 --ob-target 参数指定', file=sys.stderr)
    sys.exit(1)

TODAY = datetime.now().strftime('%Y-%m-%d')


# ----------------------------------------------------------------------------
# 解析器
# ----------------------------------------------------------------------------
def parse_frontmatter(path: Path):
    """解析 G4 卡片的 YAML frontmatter（--- ... ---）。"""
    text = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    fm, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fm[k.strip()] = v.strip()
        body = text[m.end():]
    return fm, body.strip()


def parse_self_improve(path: Path):
    """按 '- **ID**:' 分块解析 self-improve 错题本/学习/需求条目。"""
    if not path.exists():
        return []
    text = path.read_text(encoding='utf-8')
    blocks = re.split(r'(?m)^- \*\*ID\*\*:\s*', text)
    out = []
    for b in blocks[1:]:
        eid = b.split('**', 1)[0].strip()
        if not eid:
            continue

        def field(name):
            m = re.search(r'\*\*' + name + r'\*\*[:\s]*([^\n]*)', b)
            return m.group(1).strip() if m else ''

        out.append({
            'id': eid,
            'type': field('类型'),
            'content': field('内容'),
            'fix': field('修复'),
            'source': field('来源'),
            'date': field('日期'),
            'priority': field('优先级'),
            'status': field('状态'),
            'tags': field('标签'),
        })
    return out


# ----------------------------------------------------------------------------
# 渲染器（规则模板，零 LLM）
# ----------------------------------------------------------------------------
OB_HEADER = """> 本笔记由「经验→OB 同步通道」自动生成（零 LLM 规则转换），来源见 Changelog。
> 链接标准：[[顶级投研知识库标准]] · 返回：[[投研知识库 MOC]]"""

FIVE_Q = """## 5 问速读（Second Brain 检验）
1. **我们知道什么**：本条经验的核心结论/方法是什么？
2. **为何重要**：它避免/解决了什么错误、节省了什么？
3. **什么会打破论点**：何时该怀疑或更新这条？
4. **本季变了什么**：近期机制/环境是否使其过时？
5. **现在怎么做**：下一步可落地的动作是什么？"""


def render_g4_card(fm: dict, body: str, ob_rel: str) -> str:
    name = fm.get('name', '未命名卡片')
    ctype = fm.get('type', 'unknown')
    created = fm.get('created', TODAY)
    src = fm.get('source_report', '-')
    reusable = fm.get('reusable_for', '-')
    title_map = {
        'lessons-learned': '投研避坑积累',
        'asset-template': f'{name}（标的研判模板）',
        'industry-framework': f'{name}（行业框架）',
    }
    title = title_map.get(ctype, name)
    std = '[[顶级投研知识库标准]]'
    framework_links = {
        'asset-template': '[[估值框架]] · [[宏观分析框架]] · [[债券与固收投研框架]]',
        'industry-framework': '[[行业研究框架]] · [[因子与量化框架]]',
        'lessons-learned': '[[研究偏差避坑清单]] · [[Agent与Skill设计模式]]',
    }.get(ctype, '[[投研知识库 MOC]]')
    return f"""---
title: "{title}"
created: {created}
updated: {TODAY}
type: g4-{ctype}
tags: [g4, {ctype}, 自动同步]
standard: "{std}"
---

# {title}

{OB_HEADER}

{FIVE_Q}

## 来源与用途
- **G4 卡片名**：{name}
- **原始报告**：{src}
- **可复用场景**：{reusable}

## 内容
{body}

## 关联框架
{framework_links}

## Changelog
- {TODAY}：由 G4 经验卡片自动同步至 OB（来源：{src}）。
"""


def render_self_improve_file(src_path: Path, ob_rel: str, title: str,
                              kind: str) -> str:
    entries = parse_self_improve(src_path)
    if not entries:
        return ''
    blocks = []
    for e in entries:
        tags = e['tags'] or '-'
        line = f"""### {e['id']} · {e['type']}（{e['status'] or 'n/a'}）
- **内容**：{e['content']}"""
        if e['fix']:
            line += f"\n- **处置/修复**：{e['fix']}"
        if e['source']:
            line += f"\n- **来源**：{e['source']}"
        line += f"\n- **标签**：{tags}\n"
        blocks.append(line)
    std = '[[顶级投研知识库标准]]'
    return f"""---
title: "{title}"
created: {TODAY}
updated: {TODAY}
type: self-improve-{kind}
tags: [self-improve, {kind}, 跨项目, 自动同步]
standard: "{std}"
---

# {title}

> 汇聚自全局 self-improve 层：SessionEnd Hook 从【每个对话 + 每个 skill】自动捕获。
> 属于「轻量全局层」知识沉淀，与金融AI投研 G 系列（深度可信层）互补。

{OB_HEADER}

{FIVE_Q}

## 条目清单（共 {len(entries)} 条）
""" + '\n'.join(blocks) + f"""
## 关联
- 工作流视角：[[金融AI投研省token优化]] · [[Agent与Skill设计模式]]
- 避坑视角：[[研究偏差避坑清单]]

## Changelog
- {TODAY}：由 self-improve 层（{src_path.name}）自动同步至 OB（增量，hash 变更才重写）。
"""


# ----------------------------------------------------------------------------
# 源收集
# ----------------------------------------------------------------------------
def collect_sources():
    """返回 [(src_id, src_path, ob_rel_path, render_kind, extra)]。"""
    sources = []

    # ① + ③ G4 experience 目录（含自动发现其他 skill）
    for skill_dir in sorted(SKILLS.iterdir()):
        exp = skill_dir / 'experience'
        if not exp.is_dir():
            continue
        sname = skill_dir.name
        # lessons-learned.md（累积单文件）
        ll = exp / 'lessons-learned.md'
        if ll.exists():
            sources.append((f'g4:{sname}:lessons',
                            ll, '30-避坑与方法论/投研避坑积累.md',
                            'g4-lessons', None))
        # asset-templates / 每对象一文件
        for p in sorted((exp / 'asset-templates').glob('*.md')):
            if p.name.lower() == 'readme.md':
                continue
            fm, _ = parse_frontmatter(p)
            nm = fm.get('name', p.stem)
            sources.append((f'g4:{sname}:asset:{p.stem}',
                            p, f'20-标的与行业库/{nm}.md',
                            'g4-asset', None))
        # industry-frameworks / 每对象一文件
        for p in sorted((exp / 'industry-frameworks').glob('*.md')):
            if p.name.lower() == 'readme.md':
                continue
            fm, _ = parse_frontmatter(p)
            nm = fm.get('name', p.stem)
            sources.append((f'g4:{sname}:industry:{p.stem}',
                            p, f'20-标的与行业库/{nm}行业框架.md',
                            'g4-industry', None))

    # ② 全局 self-improve 层
    mapping = {
        'ERRORS.md': ('30-避坑与方法论/跨项目错题本.md', '跨项目错题本', 'errors'),
        'LEARNINGS.md': ('50-工作流/跨项目学习沉淀.md', '跨项目学习沉淀', 'learnings'),
        'FEATURE_REQUESTS.md': ('50-工作流/跨项目需求沉淀.md', '跨项目需求沉淀', 'features'),
    }
    for fname, (ob_rel, title, kind) in mapping.items():
        fp = SELF_IMPROVE / fname
        if fp.exists():
            sources.append((f'self-improve:{fname}', fp, ob_rel,
                            'self-improve', (title, kind)))
    return sources


def hash_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def sync(ob_root: Path, dry_run: bool):
    sources = collect_sources()
    index_path = ob_root / INDEX_NAME
    index = {}
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding='utf-8'))
        except Exception:
            index = {}

    plan = []
    for src_id, src_path, ob_rel, kind, extra in sources:
        cur = hash_of(src_path)
        if index.get(src_id) == cur:
            continue  # 未变更，跳过
        plan.append((src_id, src_path, ob_rel, kind, extra, cur))

    if not plan:
        print('✅ 无新增/变更源，已全部同步（增量跳过）。')
        return

    print(f"{'[DRY-RUN] ' if dry_run else ''}将同步 {len(plan)} 个源 → {ob_root}")
    print('=' * 60)
    for src_id, src_path, ob_rel, kind, extra, cur in plan:
        print(f"  • {src_id}\n      → {ob_rel}  ({kind})")

    if dry_run:
        print('=' * 60)
        print('DRY-RUN 完成，未写盘。去掉 --dry-run 执行真实同步。')
        return

    for src_id, src_path, ob_rel, kind, extra, cur in plan:
        if kind.startswith('g4'):
            fm, body = parse_frontmatter(src_path)
            content = render_g4_card(fm, body, ob_rel)
        else:
            title, sk = extra
            content = render_self_improve_file(src_path, ob_rel, title, sk)
        if not content.strip():
            continue
        out = ob_root / ob_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding='utf-8')
        index[src_id] = cur
        print(f"  ✓ 已写 {ob_rel}")

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2),
                          encoding='utf-8')
    print('=' * 60)
    print(f"同步完成，共 {len(plan)} 篇更新。索引已存 {INDEX_NAME}")


def main():
    ap = argparse.ArgumentParser(description='经验→Obsidian 多源同步（零 LLM/增量）')
    ap.add_argument('--dry-run', action='store_true', help='仅预览，不写盘')
    ap.add_argument('--ob-target', default=None,
                    help='OB 目标库根目录（覆盖 OB_VAULT / config.local.json）')
    args = ap.parse_args()
    ob_root = resolve_ob_target(args.ob_target)
    if not ob_root.exists():
        print(f'OB 目标不存在：{ob_root}', file=sys.stderr)
        sys.exit(1)
    sync(ob_root, args.dry_run)


if __name__ == '__main__':
    main()
