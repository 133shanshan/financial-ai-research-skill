#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版回测测试脚本 - 使用模拟数据
测试 MA 均线交叉策略
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backtest_engine import (
    run_backtest,
    calculate_metrics,
    plot_net_value_curve,
    plot_drawdown_curve,
    generate_backtest_report
)

def generate_mock_data(symbol="600519", days=250):
    """生成模拟的日线数据"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    # 只保留工作日
    dates = dates[dates.dayofweek < 5]

    np.random.seed(42)  # 固定随机种子，保证结果可重复

    base_price = 1800.0
    prices = []
    current_price = base_price

    for i in range(len(dates)):
        # 随机游走
        change = np.random.normal(0, 0.02)
        current_price = current_price * (1 + change)
        prices.append(current_price)

    # 生成 OHLC 数据
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        high = close * (1 + abs(np.random.normal(0, 0.01)))
        low = close * (1 - abs(np.random.normal(0, 0.01)))
        open_price = close * (1 + np.random.normal(0, 0.005))
        volume = int(np.random.randint(1e5, 5e5))

        data.append({
            '日期': date.strftime('%Y-%m-%d'),
            '开盘': round(open_price, 2),
            '最高': round(high, 2),
            '最低': round(low, 2),
            '收盘': round(close, 2),
            '成交量': volume
        })

    df = pd.DataFrame(data)
    df['日期'] = pd.to_datetime(df['日期'])
    df.set_index('日期', inplace=True)

    return df

def ma_cross_strategy(row, history):
    """
    MA 均线交叉策略
    - MA5 上穿 MA20 → 买入
    - MA5 下穿 MA20 → 卖出
    """
    if len(history) < 20:
        return "HOLD"

    ma5 = history['close'].tail(5).mean()
    ma20 = history['close'].tail(20).mean()

    if len(history) >= 21:
        prev_ma5 = history['close'].iloc[-6:-1].mean()
        prev_ma20 = history['close'].iloc[-21:-1].mean()
    else:
        prev_ma5 = ma5
        prev_ma20 = ma20

    if prev_ma5 <= prev_ma20 and ma5 > ma20:
        return "BUY"
    elif prev_ma5 >= prev_ma20 and ma5 < ma20:
        return "SELL"
    else:
        return "HOLD"

def main():
    print("=" * 60)
    print("策略回测测试（简化版 - 模拟数据）")
    print("=" * 60)

    # 1. 生成模拟数据
    print("\n[1/5] 生成模拟数据...")
    stock_data = generate_mock_data("600519", days=250)
    print(f"   生成 {len(stock_data)} 条日线数据")
    print(f"   价格区间: {stock_data['收盘'].min():.2f} - {stock_data['收盘'].max():.2f}")

    # 2. 运行回测
    print("\n[2/5] 运行回测...")
    portfolio, trades, cash_history, position_history = run_backtest(
        strategy_func=ma_cross_strategy,
        df=stock_data,
        initial_cash=1000000.0,
        commission=0.0003,
        stamp_duty=0.001,
        slippage=0.002
    )
    print(f"   交易次数: {len(trades)}")
    print(f"   最终资产: {portfolio[-1]:,.2f} 元")

    # 3. 计算性能指标
    print("\n[3/5] 计算性能指标...")
    metrics = calculate_metrics(portfolio, stock_data, risk_free_rate=0.025)

    print(f"   总收益率: {metrics['总收益率']*100:.2f}%")
    print(f"   年化收益率: {metrics['年化收益率']*100:.2f}%")
    print(f"   夏普比率: {metrics['夏普比率']:.2f}")
    print(f"   最大回撤: {metrics['最大回撤']*100:.2f}%")
    print(f"   胜率: {metrics['胜率']*100:.2f}%")

    # 4. 绘制图表
    print("\n[4/5] 绘制图表...")
    reports_dir = os.path.join(os.path.dirname(__file__), '../reports')
    os.makedirs(reports_dir, exist_ok=True)

    net_value_img = os.path.join(reports_dir, 'net_value_curve.png')
    drawdown_img = os.path.join(reports_dir, 'drawdown_curve.png')

    plot_net_value_curve(portfolio, net_value_img)
    plot_drawdown_curve(portfolio, drawdown_img)
    print(f"   净值曲线图: {net_value_img}")
    print(f"   回撤曲线图: {drawdown_img}")

    # 5. 生成报告
    print("\n[5/5] 生成报告...")
    output_path = os.path.join(reports_dir, f'MA均线策略_回测报告_{datetime.now().strftime("%Y-%m-%d")}.docx')

    generate_backtest_report(
        strategy_name="MA均线策略",
        symbol="600519",
        start_date=stock_data.index[0].strftime('%Y-%m-%d'),
        end_date=stock_data.index[-1].strftime('%Y-%m-%d'),
        portfolio=portfolio,
        trades=trades,
        metrics=metrics,
        output_path=output_path,
        net_value_img=net_value_img,
        drawdown_img=drawdown_img
    )

    print(f"   报告已生成: {output_path}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
