"""
RSI 策略模板
信号：
- RSI < 30 → 超卖，买入
- RSI > 70 → 超买，卖出
参数：
- period: RSI 计算周期（默认 14）
- oversold: 超卖阈值（默认 30）
- overbought: 超买阈值（默认 70）
"""

import pandas as pd
import numpy as np


def calculate_rsi(df, period=14):
    """
    计算 RSI 指标
    
    参数：
    - df: DataFrame，包含 'close' 列
    - period: RSI 计算周期
    
    返回：
    - df_with_rsi: 包含 RSI 列的 DataFrame
    """
    df = df.copy()
    
    # 计算价格变化
    delta = df['close'].diff()
    
    # 分别计算上涨和下跌
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # 计算平均上涨和平均下跌（使用 EMA）
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    
    # 计算 RS 和 RSI
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df


def rsi_strategy(row, history, period=14, oversold=30, overbought=70):
    """
    RSI 策略函数
    
    参数：
    - row: 当前行数据（Dict）
    - history: 历史数据（DataFrame）
    - period: RSI 计算周期
    - oversold: 超卖阈值
    - overbought: 超买阈值
    
    返回：
    - signal: "BUY" / "SELL" / "HOLD"
    """
    if len(history) < period + 1:
        return "HOLD"
    
    # 计算 RSI
    df_with_rsi = calculate_rsi(history, period)
    
    # 获取当前和前一日的 RSI
    current_rsi = df_with_rsi['RSI'].iloc[-1]
    prev_rsi = df_with_rsi['RSI'].iloc[-2]
    
    # RSI 从超卖区上穿 → 买入
    if prev_rsi <= oversold and current_rsi > oversold:
        return "BUY"
    # RSI 从超买区下穿 → 卖出
    elif prev_rsi >= overbought and current_rsi < overbought:
        return "SELL"
    else:
        return "HOLD"


# 示例使用
if __name__ == "__main__":
    # 创建模拟数据
    n = 100
    dates = pd.date_range('2025-01-01', periods=n, freq='B')
    np.random.seed(42)
    close_prices = 1800 + np.cumsum(np.random.randn(n) * 10)
    
    df = pd.DataFrame({
        'date': dates,
        'open': close_prices - 5,
        'high': close_prices + 10,
        'low': close_prices - 10,
        'close': close_prices,
        'volume': np.random.randint(1000000, 5000000, n)
    })
    
    # 测试策略
    signals = []
    for i in range(len(df)):
        row = df.iloc[i]
        history = df.iloc[:i] if i > 0 else df.iloc[0:0]
        signal = rsi_strategy(row, history)
        signals.append(signal)
    
    print(f"RSI 策略测试完成，共 {len(signals)} 个信号")
    print(f"买入信号：{signals.count('BUY')} 次")
    print(f"卖出信号：{signals.count('SELL')} 次")
    print(f"持有信号：{signals.count('HOLD')} 次")
