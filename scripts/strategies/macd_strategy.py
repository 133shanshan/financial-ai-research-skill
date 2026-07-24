"""
MACD 策略模板
信号：
- MACD 金叉（DIF 上穿 DEA）→ 买入
- MACD 死叉（DIF 下穿 DEA）→ 卖出
参数：
- fast_period: 快线周期（默认 12）
- slow_period: 慢线周期（默认 26）
- signal_period: 信号线周期（默认 9）
"""

import pandas as pd
import numpy as np


def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """
    计算 MACD 指标
    
    参数：
    - df: DataFrame，包含 'close' 列
    - fast_period: 快线周期
    - slow_period: 慢线周期
    - signal_period: 信号线周期
    
    返回：
    - df_with_macd: 包含 DIF、DEA、MACD 列的 DataFrame
    """
    df = df.copy()
    
    # 计算 EMA
    ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
    
    # 计算 DIF 和 DEA
    df['DIF'] = ema_fast - ema_slow
    df['DEA'] = df['DIF'].ewm(span=signal_period, adjust=False).mean()
    
    # 计算 MACD 柱
    df['MACD'] = (df['DIF'] - df['DEA']) * 2
    
    return df


def macd_strategy(row, history, fast_period=12, slow_period=26, signal_period=9):
    """
    MACD 策略函数
    
    参数：
    - row: 当前行数据（Dict）
    - history: 历史数据（DataFrame）
    - fast_period: 快线周期
    - slow_period: 慢线周期
    - signal_period: 信号线周期
    
    返回：
    - signal: "BUY" / "SELL" / "HOLD"
    """
    if len(history) < slow_period + signal_period:
        return "HOLD"
    
    # 计算 MACD
    df_with_macd = calculate_macd(history, fast_period, slow_period, signal_period)
    
    # 获取当前和前一日的 DIF、DEA
    current_dif = df_with_macd['DIF'].iloc[-1]
    current_dea = df_with_macd['DEA'].iloc[-1]
    prev_dif = df_with_macd['DIF'].iloc[-2]
    prev_dea = df_with_macd['DEA'].iloc[-2]
    
    # 金叉：DIF 上穿 DEA
    if prev_dif <= prev_dea and current_dif > current_dea:
        return "BUY"
    # 死叉：DIF 下穿 DEA
    elif prev_dif >= prev_dea and current_dif < current_dea:
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
        signal = macd_strategy(row, history)
        signals.append(signal)
    
    print(f"MACD 策略测试完成，共 {len(signals)} 个信号")
    print(f"买入信号：{signals.count('BUY')} 次")
    print(f"卖出信号：{signals.count('SELL')} 次")
    print(f"持有信号：{signals.count('HOLD')} 次")
