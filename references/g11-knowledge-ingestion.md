# G11 非结构化知识回流（v3.11.0）

> 把投研相关的**非结构化外部沟通**（邮件：路演纪要、研报推送、客户/内部讨论、会议邀请附件）沉淀为可复用知识卡片，回流进 `experience/` 体系，供后续研究检索复用。
> 与 G4（交付后自动产出经验，来源=本次研究）互补：G11 来源=外部邮件；与 G9（self-evolution）协同，新卡片作为知识增量信号。

---

## 1. 背景与差距

- **G4 experience-deposition** 只沉淀"本次研究过程中"产生的经验（避坑/标的模板/行业框架），来源是 agent 自身产出，未覆盖散落在外部沟通里的投研知识。
- **真实投研大量知识在非结构化邮件里**：路演纪要、卖方研报推送、客户沟通要点、内部讨论、会议邀请附件（PDF/Excel/Word）。这些散落在邮箱，未被结构化、不可被下次研究复用。
- **连接器现状（2026-07-21 实测）**：`agent-mail` 经 `connector-proxy` 已接入，能力完整（GetMe / ListMessages / SearchMessages / GetMessage / ListAttachments / DownloadAttachment），但**用户 Agent 邮箱尚未开通**（`_agentmail_meta: {status:"not_bound"}`）。即"管道就位，只差开通"。
- 本规范补齐该层：把"邮件里的投研知识"变成"可检索复用的 experience 卡片"。**会议/聊天（calendar/chat 连接器）当前不可用**，标记 blocked，待连接器可用再扩展入口。

## 2. 知识入口与分类

入口：agent-mail 收件箱（经 `SearchMessages` 按投研关键词检索）。
分类（**复用 G4 三类 + 新增"邮件洞察"子类**，不另造体系）：

| 分类 | 写入路径 | 适用 |
|------|----------|------|
| 避坑清单 | `experience/lessons-learned.md` | 邮件揭示的踩坑/监管/合规红线 |
| 标的研判模板 | `experience/asset-templates/<标的>.md` | 邮件给出的个股/行业关键假设、估值锚、催化剂 |
| 行业框架 | `experience/industry-frameworks/<行业>.md` | 邮件沉淀的产业逻辑、供需框架 |
| 邮件洞察（G11 新增） | `experience/mail-insights/<主题>.md` | 无法归入以上三类的可复用要点（路演核心观点、客户真实诉求、会议结论） |

## 3. 摄取协议（agent-mail 可用时）

1. **权限确认**：`GetMe` 取别名/速率/附件约束，确认邮箱已开通且未超限。
2. **检索候选**：`SearchMessages(q=<投研关键词：标的代码/行业/路演/研报/会议/客户>)` 找相关邮件；按日期/发件人排序。
3. **读取正文**：`GetMessage(message_id)` 取 subject/sender/正文/附件元数据。
4. **取附件**（如有）：`ListAttachments` → `DownloadAttachment(message_id, attachment_id, output_dir)` 落盘到 `experience/_mail_raw/<delivery_id>/`，**仅处理 PDF/Excel/Word/CSV**（代码/二进制危险类型拒绝下载）。
5. **抽取与归类**：从正文+附件抽取可复用知识，归类为 §2 四类之一，写成卡片。
6. **写入 experience/**：追加到对应卡片文件，并打 `source: agent-mail:<message_id>` 溯源标记，与 G4 卡片（`source: self`）区分。
7. **回灌**：本次写入的卡片纳入"知识库加载/历史案例检索"范围，下次研究自动可检索（继承 G4 回灌机制）。
8. **协同 G9**：新卡片数/知识增量写入 `evolution/signals/<delivery_id>.json`（知识增量维度）。

## 4. 触发条件

- **显式**：用户指令"从邮件补充经验 / 摄取邮件知识 / 把路演纪要存成卡片"。
- **隐式**：研究任务引用了邮件来源信息（如"xx 邮件里提到…"），或 report-writer 阶段检测到未结构化外部输入。
- **best-effort**：agent-mail 未开通 / 检索无匹配 / 运行环境不可用 → 报告第20章写降级声明，不阻塞投递。

## 5. 与 G4 / G9 协同

- **复用 G4**：卡片写入同一 `experience/` 目录、同一回灌机制；G11 不另造体系。
- **喂给 G9**：卡片数/知识增量进 `evolution signals`，作为新的质量信号维度。
- **溯源**：每张 G11 卡片带 `source: agent-mail:<message_id>`，与 G4 卡片区分，便于审计与回退。

## 6. 报告结构（第 20 章「非结构化知识回流」）

- 摄取状态（agent-mail 已开通 / 未开通 / 未检索到）
- 检索到的相关邮件清单（message_id / sender / subject / 日期，脱敏）
- 抽取的知识卡片列表（分类 + 写入路径 + 溯源标记）
- 知识增量（新增卡片数）与对下次研究的预期效用
- 降级声明（若未开通/无匹配）：「本报告未摄取外部邮件知识：agent-mail 未开通 / 无匹配邮件（best-effort，不阻塞）」

## 7. 降级处置

- **agent-mail 未开通 / 不可用**：best-effort，不阻塞；第20章标注「agent-mail 未开通，本次未摄取外部邮件知识」；不触发第十三道拦截但须明确声明。
- **无投资建议 / 纯研究**：可显式声明「本报告不纳入非结构化知识回流」。
- **隐私边界**：仅摄取用户明确指向的邮件/主题；不主动扫描全部收件箱；附件仅落盘到 `experience/_mail_raw/` 受控目录，不外流。

## 8. 第十三道 fail-closed 校验逻辑（`check-knowledge-ingestion.sh`）

- 报告含「非结构化知识回流」章节：
  - 须含 **知识条目**（≥1 卡片：分类 + 路径 + 溯源标记）/ 或「本报告未摄取外部邮件知识」声明 / 或「本报告不纳入非结构化知识回流」豁免声明，否则拦截；
- 均无 → 拦截。

## 9. 开通指引（给用户）

- 当前 agent-mail 已接入框架，但邮箱未开通。前往 WorkBuddy「更多 - 我的邮箱」完成开通后，G11 即可真实摄取邮件知识；开通前 G11 以降级声明运行，不阻塞任何投递。
- 会议/聊天入口（calendar/chat 连接器）待 WorkBuddy 提供对应 MCP 连接器后扩展，当前标记 blocked。
