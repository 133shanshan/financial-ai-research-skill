"""
策略加载器
提供统一的策略加载接口，支持 MA、MACD、RSI、布林带等策略
"""

import sys
import os

# 添加策略目录到路径
strategy_dir = os.path.dirname(os.path.abspath(__file__))
if strategy_dir not in sys.path:
    sys.path.append(strategy_dir)


def load_strategy(strategy_name):
    """
    加载策略函数
    
    参数：
    - strategy_name: 策略名称（'ma_cross', 'macd', 'rsi', 'bollinger'）
    
    返回：
    - strategy_func: 策略函数（接收 row 和 history，返回信号）
    """
    if strategy_name == 'ma_cross':
        from strategies.ma_cross import ma_cross_strategy
        return ma_cross_strategy
    
    elif strategy_name == 'macd':
        from strategies.macd_strategy import macd_strategy
        return macd_strategy
    
    elif strategy_name == 'rsi':
        from strategies.rsi_strategy import rsi_strategy
        return rsi_strategy
    
    elif strategy_name == 'bollinger':
        from strategies.bollinger_strategy import bollinger_strategy
        return bollinger_strategy
    
    else:
        raise ValueError(f"未知策略：{strategy_name}，支持的策略：ma_cross, macd, rsi, bollinger")


def list_strategies():
    """
    列出所有可用策略
    
    返回：
    - strategies: 策略信息列表
    """
    strategies = [
        {
            'name': 'ma_cross',
            'description': 'MA 均线交叉策略',
            'parameters': {
                'fast_period': 5,
                'slow_period': 20
            },
            'signal': 'MA5 上穿 MA20 → 买入；MA5 下穿 MA20 → 卖出'
        },
        {
            'name': 'macd',
            'description': 'MACD 策略',
            'parameters': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            },
            'signal': 'DIF 上穿 DEA → 买入；DIF 下穿 DEA → 卖出'
        },
        {
            'name': 'rsi',
            'description': 'RSI 策略',
            'parameters': {
                'period': 14,
                'oversold': 30,
                'overbought': 70
            },
            'signal': 'RSI < 30 → 买入；RSI > 70 → 卖出'
        },
        {
            'name': 'bollinger',
            'description': '布林带策略',
            'parameters': {
                'period': 20,
                'std_dev': 2.0
            },
            'signal': '价格触及下轨 → 买入；价格触及上轨 → 卖出'
        }
    ]
    
    return strategies


# 示例使用
if __name__ == "__main__":
    # 列出所有策略
    strategies = list_strategies()
    print("可用策略列表：")
    print("=" * 50)
    for s in strategies:
        print(f"策略名称：{s['name']}")
        print(f"  描述：{s['description']}")
        print(f"  参数：{s['parameters']}")
        print(f"  信号：{s['signal']}")
        print()
    
    # 加载并测试 MA 策略
    print("测试 MA 均线交叉策略...")
    ma_func = load_strategy('ma_cross')
    print(f"✅ 策略加载成功：{ma_func}")
    
    # 加载并测试 MACD 策略
    print("\n测试 MACD 策略...")
    macd_func = load_strategy('macd')
    print(f"✅ 策略加载成功：{macd_func}")
    
    # 加载并测试 RSI 策略
    print("\n测试 RSI 策略...")
    rsi_func = load_strategy('rsi')
    print(f"✅ 策略加载成功：{rsi_func}")
    
    # 加载并测试布林带策略
    print("\n测试布林带策略...")
    bollinger_func = load_strategy('bollinger')
    print(f"✅ 策略加载成功：{bollinger_func}")
