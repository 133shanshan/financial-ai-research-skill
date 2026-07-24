# 辅助脚本目录

本目录存放"金融AI投研"Skill 可调用的辅助脚本，用于提高金融分析工作效率。

## 脚本命名规范

- AkShare 相关：`akshare_*.py`
- 数据获取：`data_fetch_*.py`
- 技术分析：`technical_analysis_*.py`
- 基本面分析：`fundamental_analysis_*.py`
- 回测脚本：`backtest_*.py`
- 可视化：`visualization_*.py`

## 使用方式

在 SKILL.md 或 references 文件中，使用 `${CLAUDE_SKILL_DIR}/scripts/` 路径引用脚本。

示例：
```markdown
执行数据获取：运行 `${CLAUDE_SKILL_DIR}/scripts/akshare_fetch.py`
```

## 注意事项

1. 脚本必须是自包含的，不依赖 Skill 目录外的文件
2. 脚本应输出清晰的执行日志，方便 AI 理解执行结果
3. 涉及文件操作时，使用相对路径或 `${CLAUDE_SKILL_DIR}` 变量
4. 金融数据获取脚本必须标注数据来源和获取时间
