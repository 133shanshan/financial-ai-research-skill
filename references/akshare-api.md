# AkShare API 使用指南

> 本文件为「金融AI投研」Skill的 AkShare 数据调用规范文档。
> 所有金融数据优先使用 AkShare 开源库，禁止伪造数据。

---

## 安装与配置

```bash
pip install akshare --upgrade
```

Python 引入：
```python
import akshare as ak
```

---

## 常用 API 速查表

### 一、股票行情数据

| 函数 | 说明 | 返回字段 |
|------|------|----------|
| `ak.stock_zh_a_spot_em()` | A股实时行情（东财） | 代码、名称、最新价、涨跌幅、成交量… |
| `ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20260518", adjust="qfq")` | A股历史K线 | 日期、开盘、收盘、最高、最低、成交量、成交额 |
| `ak.stock_individual_info_em(symbol="000001")` | 个股基本信息 | 总股本、流通股本、总市值、流通市值… |
| `ak.stock_financial_abstract_ths(symbol="000001", indicator="按报告期")` | 财务摘要（同花顺） | ROE、毛利率、净利率、负债率… |

### 二、宏观数据

| 函数 | 说明 | 频率 |
|------|------|------|
| `ak.macro_china_cpi_monthly()` | CPI（居民消费价格指数） | 月度 |
| `ak.macro_china_ppi_monthly()` | PPI（工业生产者出厂价格指数） | 月度 |
| `ak.macro_china_pmi()` | PMI（制造业采购经理指数） | 月度 |
| `ak.macro_china_gdp()` | GDP（国内生产总值） | 季度 |
| `ak.macro_china_social_consumption_retail()` | 社会消费品零售总额 | 月度 |
| `ak.macro_china_foreign_exchange_reserves()` | 外汇储备 | 月度 |

### 三、货币政策数据

| 函数 | 说明 |
|------|------|
| `ak.macro_china_lpr()` | LPR（贷款市场报价利率） |
| `ak.macro_china_mlf()` | MLF（中期借贷便利） |
| `ak.macro_china_shibor()` | SHIBOR（上海银行间同业拆放利率） |

### 四、资金流向

| 函数 | 说明 |
|------|------|
| `ak.stock_market_fund_flow_individual()` | 个股资金流向 |
| `ak.stock_sector_fund_flow_rank(indicator="今日")` | 行业板块资金流向 |
| `ak.stock_north_flow_hist_em()` | 北向资金历史数据 |

### 五、指数数据

| 函数 | 说明 |
|------|------|
| `ak.stock_zh_index_spot_em()` | A股指数实时行情 |
| `ak.stock_zh_index_daily(symbol="sh000001")` | 指数历史K线（上证=`sh000001`，深证=`sz399001`） |

---

## 数据调用规范

### 1. 数据时效性标注（强制）
每次获取数据后，**必须在输出中标注**：
```
数据来源：AkShare（东方财富）
数据获取时间：YYYY-MM-DD HH:MM:SS
数据更新频率：实时/日频/月频/季频
```

### 2. 实时 vs 历史数据区分
- **实时数据**：`stock_zh_a_spot_em()` 等，标注"实时（延时15秒）"
- **历史数据**：`stock_zh_a_hist()` 等，标注数据起止日期

### 3. 数据异常处理
```python
try:
    df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20260518")
    if df.empty:
        print("警告：未获取到数据，请检查股票代码或日期范围")
except Exception as e:
    print(f"数据获取失败：{e}")
    print("建议：检查网络连接或AkShare版本，执行 pip install akshare --upgrade")
```

### 4. 股票代码格式
- 上交所：`sh600xxx`（6开头）
- 深交所：`sz00xxxx`（00开头）、`sz30xxxx`（创业板）
- 北交所：`bj8xxxxx`（8开头）

---

## 数据源备份方案（P1缺陷修复）

### 1. 备份切换逻辑

**当AkShare API调用失败时，按以下顺序切换**：

```
AkShare API调用
    ↓ 失败？
重试3次（每次间隔2秒）
    ↓ 仍失败？
备用方案1：WebSearch搜索相同数据
    ↓ 仍失败？
备用方案2：提示用户手动输入或跳过该数据
    ↓ 完成
标注实际数据来源（禁止伪造）
```

### 2. 备用数据源清单

| 数据类型 | 主数据源 | 备用方案1 | 备用方案2 |
|----------|----------|-----------|-----------|
| 股票行情 | AkShare（东方财富） | WebSearch：`"{股票代码} 实时行情"` | 提示用户手动输入 |
| 基金净值 | AkShare（东方财富） | WebSearch：`"{基金代码} 最新净值"` | 使用上次缓存数据 |
| 宏观数据 | AkShare（国家统计局） | WebSearch：`"国家统计局 {指标} 最新"` | 标注"数据暂缺" |
| 货币政策 | AkShare（央行官网） | WebSearch：`"央行 {LPR/MLF} 最新"` | 标注"数据暂缺" |
| 基金排名 | AkShare（东方财富） | WebSearch：`"{基金代码} 排名"` | 标注"排名数据暂缺" |

### 3. 重试机制代码模板

```python
import time
import akshare as ak

def get_data_with_retry(func, max_retries=3, delay=2, *args, **kwargs):
    """
    带重试机制的数据获取函数
    func: AkShare API函数
    max_retries: 最大重试次数
    delay: 重试间隔（秒）
    """
    for i in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if i < max_retries - 1:
                print(f"第{i+1}次尝试失败：{e}，{delay}秒后重试...")
                time.sleep(delay)
            else:
                print(f"全部{max_retries}次尝试失败：{e}")
                return None

# 使用示例
fund_nav = get_data_with_retry(
    ak.fund_open_fund_info_em,
    max_retries=3,
    delay=2,
    symbol="005827",
    indicator="单位净值走势"
)

if fund_nav is None:
    print("AkShare获取数据失败，切换备用方案...")
    # 备用方案：WebSearch搜索
```

### 4. 数据来源标注规则（备份方案）

**当使用备用方案时，必须如实标注**：

```
数据来源：WebSearch（搜索引擎）
数据获取时间：YYYY-MM-DD HH:MM:SS
数据更新频率：实时（搜索引擎结果）
⚠️ 注意：此数据来自WebSearch，非AkShare官方接口，准确性需人工核实
```

### 5. 禁止行为（红线）

| 禁止行为 | 说明 | 后果 |
|----------|------|------|
| ❌ 伪造数据 | AkShare失败后编造数据 | 严重错误，必须杜绝 |
| ❌ 混淆来源 | 使用WebSearch数据但标注为AkShare | 误导用户，必须修正 |
| ❌ 静默失败 | API失败后不通知用户，直接继续 | 用户不知情，可能误导决策 |

---

*本备份方案为P1缺陷修复（2026-05-20），所有模块的数据获取必须遵循此方案。*

### 错误1：股票代码格式错误
```python
# ❌ 错误
ak.stock_zh_a_hist(symbol="600519", ...)  # 缺少交易所前缀

# ✅ 正确
ak.stock_zh_a_hist(symbol="sh600519", ...)
```

### 错误2：日期格式错误
```python
# ❌ 错误
start_date="2024-01-01"  # AkShare不接受连字符

# ✅ 正确
start_date="20240101"
```

### 错误3：adjust 参数错误
```python
# ❌ 错误
adjust="forward"  # AkShare不支持此参数

# ✅ 正确
adjust="qfq"   # 前复权
adjust="hfq"   # 后复权
adjust=""       # 不复权
```

---

## 数据质量检查清单

- [ ] 数据非空（df.empty == False）
- [ ] 日期范围正确（无未来数据）
- [ ] 字段名与文档一致（AkShare版本更新可能导致字段名变化）
- [ ] 标注了数据来源和获取时间
- [ ] 标注了数据更新频率

---

*本文件随 AkShare 版本更新而更新，请定期检查 AkShare 官方文档：https://akshare.akfamily.xyz/*