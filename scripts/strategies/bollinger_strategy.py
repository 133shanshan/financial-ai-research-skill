"""
布林带策略模板
信号：
- 价格触及下轨 → 买入（超卖）
- 价格触及上轨 → 卖出（超买）
参数：
- period: 移动平均周期（默认 20）
- std_dev: 标准差倍数（默认 2.0）
"""

import pandas as pd
import numpy as np


def calculate_bollinger_bands(df, period=20, std_dev=2.0):
    """
    计算布林带指标
    
    参数：
    - df: DataFrame，包含 'close' 列
    - period: 移动平均周期
    - std_dev: 标准差倍数
    
    返回：
    - df_with_bb: 包含 中轨、上轨、下轨、带宽 列的 DataFrame
    """
    df = df.copy()
    
    # 计算中轨（SMA）
    df['中轨'] = df['close'].rolling(window=period).mean()
    
    # 计算标准差
    std = df['close'].rolling(window=period).std()
    
    # 计算上轨和下轨
    df['上轨'] = df['中轨'] + (std * std_dev)
    df['下轨'] = df['中轨'] - (std * std_dev)
    
    # 计算带宽
    df['带宽'] = (df['上轨'] - df['下轨']) / df['中轨']
    
    return df


def bollinger_strategy(row, history, period=20, std_dev=2.0):
    """
    布林带策略函数
    
    参数：
    - row: 当前行数据（Dict）
    - history: 历史数据（DataFrame）
    - period: 移动平均周期
    - std_dev: 标准差倍数
    
    返回：
    - signal: "BUY" / "SELL" / "HOLD"
    """
    if len(history) < period:
        return "HOLD"
    
    # 计算布林带
    df_with_bb = calculate_bollinger_bands(history, period, std_dev)
    
    # 获取当前和前一日的收盘价
    current_close = row.get('close', row.get('收盘', 0))
    prev_close = history['close'].iloc[-1] if len(history) > 0 else current_close
    
    # 获取当前和前一日布林带
    current_upper = df_with_bb['上轨'].iloc[-1]
    current_lower = df_with_bb['下轨'].iloc[-1]
    prev_upper = df_with_bb['上轨'].iloc[-2] if len(df_with_bb) >= 2 else current_upper
    prev_lower = df_with_bb['下轨'].iloc[-2] if len(df_with_bb) >= 2 else current_lower
    
    # 价格从下轨下方上穿下轨 → 买入（超卖反弹）
    if prev_close <= prev_lower and current_close > current_lower:
        return "BUY"
    # 价格从上轨上方下穿上轨 → 卖出（超买回落）
    elif prev_close >= prev_upper and current_close < current_upper:
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
        signal = bollinger_strategy(row, history)
        signals.append(signal)
    
    print(f"布林带策略测试完成，共 {len(signals)} 个信号")
    print(f"买入信号：{signals.count('BUY')} 次")
    print(f"卖出信号：{signals.count('SELL')} 次")
    print(f"持有信号：{signals.count('HOLD')} 次")
