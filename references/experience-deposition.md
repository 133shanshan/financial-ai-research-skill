# 经验沉淀规范（Experience Deposition, v3.5.0）

> 对齐蚂蚁 Agentar「长程记忆 → Skills 沉淀」机制：用出来的有效判断路径自动积累为可复用知识，越用越懂业务。
> 本 Skill 此前的「知识沉淀」步骤仅在工作流末尾一行带过、无具体产物，本文件将其具体化为**三类可复用知识卡片**，使研究产出可累积、可回灌。

---

## 一、触发时机（强制）

- 每次研究 `deliver_attachments` 完成后**必须触发一次**经验沉淀（report-writer Step 4.8 汇总，或 orchestrator 在 Step 6 之后统一触发）。
- 经验沉淀是「交付后动作」，**不阻塞**主报告投递；写入失败降级为 best-effort（见第六节）。

## 二、三类可复用产物

| 类型 | 文件位置 | 性质 | 内容骨架 |
|------|----------|------|----------|
| **避坑清单**（lessons-learned） | `experience/lessons-learned.md`（累积型，append） | 跨研究累积 | 日期 / 场景 / 踩的坑 / 正确做法 / 来源模块 |
| **标的研判模板**（asset-template） | `experience/asset-templates/<标的>.md` | 每标的一个 | 宏观映射 / 行业位置 / 财务要点 / 估值方法 / 情绪信号 / 投资建议模板 |
| **行业框架**（industry-framework） | `experience/industry-frameworks/<行业>.md` | 每行业一个 | 产业链图 / 关键指标 / 竞争格局 / 政策敏感度 / 分析 Checklist |

## 三、产物格式（结构化、可回灌）

每个卡片含轻量 frontmatter，便于下次检索加载：

```markdown
---
type: lessons-learned | asset-template | industry-framework
name: <卡片名>
created: YYYY-MM-DD
source_report: <报告文件名>
reusable_for: <适用场景一句话>
---
<结构化正文，按第二节骨架填写>
```

- 写入 `experience/` 目录（skill 根下的 `experience/`），首次运行自动建目录。
- report-writer 在报告**第 14 章「经验沉淀与复用」**列出本次新增/更新的卡片（类型 / 名称 / 路径 / 一句话价值）。

## 四、回灌机制（闭环，对齐 Agentar）

- 下次研究的「**知识库加载 / 历史案例检索**」步骤（见 SKILL.md 标准流程）须读取 `experience/` 目录：
  - 命中**标的模板** → 作为该标的分析骨架预填；
  - 命中**行业框架** → 作为该行业分析 Checklist 预载；
  - 命中**避坑清单** → 作为风险提示注入对应分析环节。
- 高价值卡片（被多次命中、被广泛复用）可经人工或 `SkillManage` 提升为正式 Skill，沉淀为机构/个人专属能力。

## 五、报告第 14 章「经验沉淀与复用」（v3.5.0 强制）

- 列出本次研究新增/更新的经验卡片（类型 / 名称 / 路径 / 一句话价值）。
- 若本次**无新增**可复用经验，须显式声明「**本次无新增可复用经验**」，不得留空。
- 交付前运行 `.workbuddy/hooks/check-experience-deposition.sh`（第七道 fail-closed 硬校验）：报告须含「经验沉淀与复用」章节且 ≥1 经验条目（避坑/模板/框架），或显式声明「本次无新增可复用经验」；返回 ok:false 必须补做经验沉淀记录，不得投递。

## 六、降级处置（降级而非崩溃）

- 经验文件写入失败（目录无权限 / 磁盘满 / 沙箱限制）→ **best-effort**：在第 14 章标注「经验卡片文件写入失败，已留文本记录于本报告」，不阻塞主报告投递。
- 经验沉淀**不绕过**前六道既有质量校验（provenance / 推导链 / 反方审计 / 自评估质量门 / 流程韧性声明 / 可执行推理），仅第七道校验专管本章节。

## 七、与既有护栏协同

经验沉淀是第 14 章，与已落地的「可信层 + 质量门 + 流程韧性 + 可执行推理」正交：

| 闸门 | 管什么 |
|------|--------|
| verify-provenance.py | 快照字符区间 |
| check-derivation-chain.sh | 证据→计算→结论三段链 |
| check-adversarial-audit.sh | 反方审计章节+挑战 |
| check-quality-gate.sh | 自评估三维度+verdict |
| check-resilience-declaration.sh | 第12章流程韧性声明 |
| check-code-agent.sh | 第13章可执行推理/变量空间 |
| check-experience-deposition.sh（本道） | 第14章经验沉淀与复用 |

## 八、经验→OB 同步通道（多源，v3.12.0 增补）

机器可读/跨对话沉淀落于 `experience/`（G4）与全局 `self-improve/` 错题本；为兼顾「人读复习」，提供半自动同步脚本，把多源经验转成 Obsidian 人读版（带 frontmatter / 5问速读 / 双链 / Changelog），沉淀到用户 vault 的 `AI投研知识库`。

**多源汇聚（关键：对话与其他 skill 也能同步）**：
- ① 金融AI投研 G4 `experience/`：避坑清单 / 标的模板 / 行业框架；
- ② 全局 `self-improve/` 层（SessionEnd Hook 从【每个对话 + 每个 skill】自动捕获）：
  `ERRORS.md` 错题本 → `30-避坑与方法论/跨项目错题本.md`、
  `LEARNINGS.md` 学习 → `50-工作流/跨项目学习沉淀.md`、
  `FEATURE_REQUESTS.md` 需求 → `50-工作流/跨项目需求沉淀.md`；
- ③ 自动发现其他 skill 的 `experience/` 目录（将来扩展零成本）。

- **脚本**：`scripts/sync_experience_to_obsidian.py`（零 LLM 调用、纯规则转换、基于内容 sha256 增量去重，重复运行安全，不消耗 token）。
- **映射规则**：
  - G4 `asset-template` → `20-标的与行业库/<标的>.md`
  - G4 `industry-framework` → `20-标的与行业库/<行业>行业框架.md`
  - G4 `lessons-learned` → `30-避坑与方法论/投研避坑积累.md`（累积单文件整体同步）
  - self-improve 三文件 → 上述 `30-避坑与方法论/` 与 `50-工作流/` 三篇人读版
  - 各类均自动双向链接到 `10-投研框架/` 或 `30-避坑与方法论/` 既有笔记，成网而非孤岛。
- **触发（半自动）**：用户说「同步经验到OB」即运行：
  `python scripts/sync_experience_to_obsidian.py [--ob-target <OB vault 根/AI投研知识库>] [--dry-run]`
  OB 目标库经配置分离（12-factor）：优先读环境变量 `OB_VAULT`，其次读 skill 根目录 `config.local.json`（gitignored，不随仓库泄露）；`--ob-target` 可临时覆盖；`--dry-run` 仅预览不写文件。
- **边界**：脚本只读取源（G4 卡片 / self-improve md）、绝不修改源真值；OB 人读版为衍生产物。高价值卡片经 `SkillManage` 提升为正式 Skill 的既有路径不变。
