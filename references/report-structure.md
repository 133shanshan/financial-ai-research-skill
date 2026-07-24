# 输出报告结构定义

所有分析报告必须包含以下标准章节，最终输出为 **PDF 格式**（顶级券商研报标准）。

```
报告文件命名：{模块名}_{标的名称}_{YYYY-MM-DD}.pdf

标准章节结构：
1. 封面
   - 报告标题、标的名称、分析日期、数据来源标注
2. 核心结论（执行摘要）
   - 关键发现、买卖信号/评级/结论、置信度
3. 数据展示
   - 关键指标表格（三线表/网格型）、数据来源和获取时间标注
4. 分析过程
   - 方法论应用过程、逻辑推理链条
5. 风险提示
   - 数据局限性、模型假设限制、市场风险
6. 免责声明
   - 固定模板，详见 disclaimer-sources.md
```

## PDF 生成规范

### 生成流程
1. 使用 `python-docx` 生成 .docx 文件
2. 使用 `docx2pdf` 或 LibreOffice headless 模式转为 PDF
3. 如转换失败，保留 .docx 并标注原因

### Python 代码示例
```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import json, glob, os

# 生成 .docx
doc = Document()
# ... 填充内容 ...
doc.save('output/报告.docx')

# 转为 PDF
try:
    from docx2pdf import convert
    convert('output/报告.docx', 'output/报告.pdf')
except:
    # 降级方案：用 LibreOffice
    import subprocess
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf',
                   'output/报告.docx', '--outdir', 'output/'])
```

## 图表规范

- **表格**：网格型，表头灰色底纹（金融市场）或三线表（学术论文）
- **图片**：分辨率 ≥ 300dpi，嵌入型排版
- **数据来源**：每个图表下方必须标注"数据来源：XXX，获取时间：YYYY-MM-DD HH:MM"

## 模块特定要求

### 模块一：AI投资大师智能体
- 必须输出：大师逻辑匹配度评分、买卖信号、关键财务指标表格
- 示例：见 `../examples/ai-stock-selection-example.md`

### 模块二：货币政策语义分析
- 必须输出：政策取向判断（宽松/中性/紧缩）、语义评分、关键政策文本引用
- 示例：见 `../examples/monetary-policy-analysis-example.md`

### 模块三：国信AI资配框架
- 必须输出：股债相对强弱指数、三大周期资产配置权重、调整理由
- 示例：见 `../examples/asset-allocation-example.md`

### 模块四：行业基本面研究
- 必须输出：行业评级、关键驱动因素、竞争格局分析、风险提示
- 示例：见 `../examples/industry-research-example.md`

### 模块五：宏观数据监控
- 必须输出：关键宏观指标表格（CPI、PPI、PMI等）、趋势判断、市场影响分析
- 示例：见 `../examples/macro-data-analysis-example.md`

### 模块六：市场环境分析
- 必须输出：Risk-On/Off 评级、全球市场仪表盘、板块轮动分析
- 示例：见 `../examples/market-environment-example.md`

### 模块七：市场情绪脉搏
- 必须输出：情绪评分（-1 到 1）、资金流向、新闻情绪关键词云
- 示例：见 `../examples/sentiment-analysis-example.md`

### 模块八：顶级基金深度分析
- 必须输出：基金评级、关键财务指标、风险提示
- 示例：见 `../examples/fund-analysis-example.md`

### 模块九：策略回测引擎
- 必须输出：总收益率、年化收益率、夏普比率、最大回撤、胜率、盈亏比
- 必须包含：净值曲线图、回撤曲线图
- 必须包含：交易明细表（买入日期、买入价格、卖出日期、卖出价格、收益率）
- 策略评级：夏普比率 ≥2.0 优秀，≥1.0 良好，≥0.5 一般，<0.5 较差
- 示例：见 `../examples/backtest-example.md`

---

## 三、每章节 token 预算与紧模板（v3.13.0 新增，省 token）

> 目标：约束输出体积，按 tier 套用。report-writer 须严格遵守，超预算须压缩。

### 标准章节 token 预算（T3 完整档上限；T1/T2 按下方系数缩减）
| 章节 | T3 上限 | 紧模板（必含要点，禁散文） |
|------|---------|---------------------------|
| 1 封面 | ≤200 | 标题 / 标的 / 日期 / 数据截止日(红粗) |
| 2 核心结论 | ≤600 | 结论 + 评级 + 置信度（要点式，≤5 条） |
| 3 数据展示 | ≤800 | 三线表/网格表 + 来源(获取时间) |
| 4 分析过程 | ≤1500 | 方法论 + 推导链（要点 + [证据]/[结论]标记） |
| 5 风险提示 | ≤400 | ≤4 条风险（要点） |
| 6 免责声明 | 固定 | 模板见 disclaimer-sources.md |

### 按 tier 缩减系数
- **T1**：仅产「核心结论 + 数据 + 来源」，章节 4/5 可合并为 1–2 句或省略；总正文 ≤800 token。
- **T2**：章节 4 压缩为要点式，总正文 ≤2500 token。
- **T3**：执行上表上限（与 v3.12.1 一致）。
- 任何 tier 均不得用散文填充凑字数；超预算由 report-writer 自检压缩（优先压缩分析过程，不删来源/结论/ fail-closed 章节）。
