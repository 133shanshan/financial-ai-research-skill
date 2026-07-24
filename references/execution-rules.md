# 通用执行规则

## 1. AkShare 数据调用规范
- 所有金融数据**优先使用 AkShare**，详见 `${CLAUDE_SKILL_DIR}/references/akshare-api.md`
- 数据获取后**必须标注来源和获取时间**
- 区分实时数据 vs 历史数据，明确告知用户数据时效

## 2. Human-in-the-Loop（HITL）节点
| 模块 | HITL 节点 | 说明 |
|------|-----------|------|
| 模块一 | 最终交易决策 | AI输出买卖信号后，需人工确认 |
| 模块二 | 政策取向判断 | 语义分边界案例需人工复核 |
| 模块三 | 权重调整 | AI动态权重结果需人工审核 |
| 模块四 | 行业结论 | AI生成行业报告后需人工确认 |
| 模块五 | 数据异常处理 | 数据缺失或异常时需人工判断 |
| 模块六 | 风险评级 | Risk-On/Off 极端值时需人工复核 |
| 模块七 | 情绪极值策略 | 情绪评分±0.8以上需人工确认 |
| 模块八 | 基金投资建议 | 给出买卖建议前需人工确认 |

### HITL 超时机制（P1缺陷修复）

**问题**：若用户长时间不响应HITL节点，分析流程挂起。

**解决方案**：

```
HITL节点触发
    ↓
等待用户响应
    ↓
超时？（默认30分钟）
    ↓ 是
执行默认行为（见下表）
    ↓ 否
继续流程
```

**超时时间设置**（可配置）：

| 场景 | 超时时间 | 默认行为 |
|------|---------|----------|
| 交易决策（模块一、八） | 30分钟 | 不执行交易，输出"未经人工确认，不提供买卖建议" |
| 政策判断（模块二） | 30分钟 | 使用AI判断结果，但标注"未经人工复核，置信度降低" |
| 权重调整（模块三） | 30分钟 | 使用AI计算结果，但标注"未经人工审核，请谨慎参考" |
| 行业结论（模块四） | 60分钟 | 使用AI生成报告，但标注"未经人工确认" |
| 数据异常处理（模块五） | 10分钟 | 使用备用数据源，或标注"数据异常，仅供参考" |
| 风险评级（模块六） | 30分钟 | 使用AI评级结果，但标注"未经人工复核，风险评级可能不准确" |
| 情绪极值策略（模块七） | 30分钟 | 不执行策略，输出"未经人工确认，不提供操作建议" |

**超时通知机制**：

```
# 在HITL节点代码中添加超时检测
import time

hitl_start_time = time.time()
timeout = 30 * 60  # 30分钟，单位：秒

while True:
    if time.time() - hitl_start_time > timeout:
        # 超时，执行默认行为
        print(f"HITL节点超时（{timeout/60}分钟），执行默认行为：{default_action}")
        # 记录日志
        with open("hitl_timeout.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - HITL节点超时 - {module_name} - {node_name}\n")
        break
    
    # 检查用户是否响应
    if user_responded:
        break
    
    time.sleep(60)  # 每60秒检查一次
```

**超时日志记录格式**：

```
[HITL超时日志]
时间：YYYY-MM-DD HH:MM:SS
模块：模块{x}（{模块名称}）
HITL节点：{节点名称}
超时时间：{timeout}分钟
默认行为：{default_action}
```

### HITL 节点代码模板

```python
# HITL 节点模板（含超时机制）
import time

def hitl_node(module_name, node_name, question, options, timeout_minutes=30, default_action="继续使用AI判断结果"):
    """
    HITL节点函数（含超时机制）
    module_name: 模块名称
    node_name: 节点名称
    question: 提问内容
    options: 选项列表
    timeout_minutes: 超时时间（分钟），默认30分钟
    default_action: 超时后的默认行为
    """
    print(f"=== HITL节点：{node_name} ===")
    print(question)
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
    print(f"（超时时间：{timeout_minutes}分钟，超时将{default_action}）")
    
    # 等待用户响应（含超时检测）
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while True:
        # 检查超时
        if time.time() - start_time > timeout_seconds:
            print(f"⚠️ HITL节点超时（{timeout_minutes}分钟），{default_action}")
            # 记录日志
            log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - HITL节点超时 - {module_name} - {node_name}\n"
            with open("hitl_timeout.log", "a") as f:
                f.write(log_entry)
            return "timeout", default_action
        
        # 模拟等待用户输入（实际中应使用SendMessage工具）
        # user_input = input("请输入选项编号：")
        # if user_input:
        #     return "user_response", user_input
        
        time.sleep(1)  # 避免CPU占用过高

# 使用示例（模块八：基金投资建议）
result_type, result_value = hitl_node(
    module_name="模块八：顶级基金深度分析",
    node_name="投资建议确认",
    question="基于以上分析，您是否同意以下投资建议？",
    options=["同意，执行买入/卖出", "部分同意，需要调整", "不同意，重新分析"],
    timeout_minutes=30,
    default_action="不执行交易，输出'未经人工确认，不提供买卖建议'"
)
```

## 3. 自动化触发（Cron）
- 模块五（宏观数据监控）支持每日自动触发
- 配置方式：详见 `${CLAUDE_SKILL_DIR}/references/knowledge-base/methodology/module5-macro-monitor.md` 末尾
- 触发时间：每日 22:00（可调整）

## 4. 知识库维护
- 每次分析完成后，将关键结论存入 `${CLAUDE_SKILL_DIR}/references/knowledge-base/cases/`
- 文件命名：`{股票代码}_{板块名称}_{YYYY-MM-DD}.md`
- 存入内容：分析结论、置信度、关键数据、后续观察点

## 5. 免责声明
- 所有输出末尾**必须添加**免责声明，详见 `${CLAUDE_SKILL_DIR}/references/disclaimer-sources.md`
- 数据源必须注明，禁止伪造数据
