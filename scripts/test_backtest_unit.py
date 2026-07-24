#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略回测引擎单元测试
测试 backtest_engine.py 的核心功能
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加脚本目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_engine import (
    calculate_metrics,
    run_backtest,
    plot_net_value_curve,
    plot_drawdown_curve,
    generate_backtest_report
)


def test_calculate_metrics():
    """测试性能指标计算函数"""
    print("=" * 50)
    print("测试 1: calculate_metrics()")
    print("=" * 50)
    
    # 模拟投资组合净值（单位：元）
    # 初始资金 100 万，最终 107 万（收益率 7%）
    import numpy as np
    np.random.seed(42)
    n = 178
    portfolio = [1000000]
    for i in range(n):
        # 每天随机波动 -1% 到 +1%
        daily_return = np.random.uniform(-0.01, 0.01)
        new_value = portfolio[-1] * (1 + daily_return)
        portfolio.append(new_value)
    
    # 创建模拟的 df（DataFrame，只需要日期列）
    import pandas as pd
    df = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=n, freq='B')
    })
    
    metrics = calculate_metrics(portfolio, df, risk_free_rate=0.02)
    
    print(f"总收益率: {metrics['总收益率']:.4f}")
    print(f"年化收益率: {metrics['年化收益率']:.4f}")
    print(f"夏普比率: {metrics['夏普比率']:.4f}")
    print(f"最大回撤: {metrics['最大回撤']:.4f}")
    print(f"胜率: {metrics['胜率']:.4f}")
    
    # 断言检查
    assert -0.20 < metrics['总收益率'] < 0.20, f"总收益率应在 -20%-20% 之间，实际为 {metrics['总收益率']:.4f}"
    assert metrics['夏普比率'] > -5, f"夏普比率应 > -5，实际为 {metrics['夏普比率']:.4f}"
    assert 0 <= metrics['最大回撤'] < 0.5, f"最大回撤应在 0-50% 之间，实际为 {metrics['最大回撤']:.4f}"
    assert 0 <= metrics['胜率'] <= 1, f"胜率应在 0-1 之间，实际为 {metrics['胜率']:.4f}"
    
    print("✅ calculate_metrics() 测试通过\n")
    return True


def test_run_backtest():
    """测试回测执行函数"""
    print("=" * 50)
    print("测试 2: run_backtest()")
    print("=" * 50)
    
    # 定义测试策略（简单 MA 交叉策略）
    def ma_cross_strategy(row, history):
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
    
    # 创建测试数据（模拟 178 个交易日）
    n = 178
    dates = pd.date_range('2025-01-01', periods=n, freq='B')
    base_price = 1800.0
    price_data = []
    
    for i in range(n):
        price = base_price + i * 0.5 + np.random.randn() * 10
        price_data.append({
            'date': dates[i],
            'open': price - 5,
            'high': price + 10,
            'low': price - 10,
            'close': price,
            'volume': np.random.randint(1000000, 5000000)
        })
    
    df = pd.DataFrame(price_data)
    
    # 执行回测
    portfolio, trades, cash_history, position_history = run_backtest(
        ma_cross_strategy, df, initial_cash=1000000
    )
    
    print(f"交易日数: {len(portfolio)}")
    print(f"交易次数: {len(trades)}")
    print(f"最终资产: {portfolio[-1]:,.2f} 元")
    
    # 断言检查
    assert len(portfolio) == n + 1, f"投资组合长度应为 {n+1}，实际为 {len(portfolio)}"
    assert len(trades) >= 0, f"交易次数应 >= 0，实际为 {len(trades)}"
    assert portfolio[-1] > 0, f"最终资产应 > 0，实际为 {portfolio[-1]:,.2f}"
    
    print("✅ run_backtest() 测试通过\n")
    return True


def test_plot_functions():
    """测试图表生成函数"""
    print("=" * 50)
    print("测试 3: plot_net_value_curve() 和 plot_drawdown_curve()")
    print("=" * 50)
    
    # 创建测试数据
    portfolio = [1000000] * 50 + [1050000] * 50 + [1072700] * 78
    
    # 测试净值曲线图
    net_value_path = "test_net_value.png"
    plot_net_value_curve(portfolio, net_value_path)
    assert os.path.exists(net_value_path), f"净值曲线图未生成: {net_value_path}"
    print(f"✅ 净值曲线图已生成: {net_value_path}")
    
    # 测试回撤曲线图
    drawdown_path = "test_drawdown.png"
    plot_drawdown_curve(portfolio, drawdown_path)
    assert os.path.exists(drawdown_path), f"回撤曲线图未生成: {drawdown_path}"
    print(f"✅ 回撤曲线图已生成: {drawdown_path}")
    
    # 清理测试文件
    os.remove(net_value_path)
    os.remove(drawdown_path)
    
    print("✅ 图表生成函数测试通过\n")
    return True


def test_generate_report():
    """测试报告生成函数"""
    print("=" * 50)
    print("测试 4: generate_backtest_report()")
    print("=" * 50)
    
    # 创建模拟的 df（DataFrame，178 个交易日）
    import pandas as pd
    n = 178
    df = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=n, freq='B'),
        'close': [1000000 + i * 100 for i in range(n)]  # 模拟收盘价
    })
    
    # portfolio 长度 = len(df) + 1（第一个元素是初始资金）
    portfolio = [1000000] + df['close'].tolist()
    
    # 计算性能指标
    metrics = calculate_metrics(portfolio, df, risk_free_rate=0.02)
    
    # 生成图表
    net_value_img = "test_net_value.png"
    drawdown_img = "test_drawdown.png"
    plot_net_value_curve(portfolio, net_value_img)
    plot_drawdown_curve(portfolio, drawdown_img)
    
    # 创建模拟交易记录
    trades = [
        {'date': '2025-01-10', 'action': 'BUY', 'price': 1825.0, 'amount': 547.9, 'cash': 0},
        {'date': '2025-02-15', 'action': 'SELL', 'price': 1890.0, 'amount': 1034567.8, 'position': 0}
    ]
    
    # 生成报告
    report_path = "test_report.docx"
    generate_backtest_report(
        strategy_name="MA均线策略",
        symbol="600519",
        start_date="2025-01-01",
        end_date="2025-09-30",
        portfolio=portfolio,
        trades=trades,
        metrics=metrics,
        output_path=report_path,
        net_value_img=net_value_img,
        drawdown_img=drawdown_img
    )
    
    assert os.path.exists(report_path), f"报告未生成: {report_path}"
    print(f"✅ 报告已生成: {report_path}")
    
    # 清理测试文件
    os.remove(report_path)
    if os.path.exists(net_value_img):
        os.remove(net_value_img)
    if os.path.exists(drawdown_img):
        os.remove(drawdown_img)
    
    print("✅ generate_backtest_report() 测试通过\n")
    return True


def main():
    """运行所有测试"""
    print("开始运行策略回测引擎单元测试...\n")
    
    tests = [
        ("calculate_metrics", test_calculate_metrics),
        ("run_backtest", test_run_backtest),
        ("plot_functions", test_plot_functions),
        ("generate_report", test_generate_report)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, "通过"))
        except Exception as e:
            print(f"❌ {name} 测试失败: {e}\n")
            results.append((name, f"失败: {e}"))
    
    # 打印测试总结
    print("=" * 50)
    print("测试总结")
    print("=" * 50)
    for name, result in results:
        status = "✅" if result == "通过" else "❌"
        print(f"{status} {name}: {result}")
    
    passed = sum(1 for _, r in results if r == "通过")
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
