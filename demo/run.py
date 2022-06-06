import pandas as pd

from app.csv_backtester.engine import CsvBacktestingEngine, evaluate
# from app.cta_strategy.backtesting import OptimizationSetting
from app.cta_strategy.strategies.double_ma_strategy import (
    DoubleMaStrategy,
)
from app.cta_strategy.strategies.boll_channel_strategy import (
    BollChannelStrategy,
)
import os
from datetime import datetime
from app.cta_strategy.backtesting import BacktestingMode


def exec():
    engine = CsvBacktestingEngine()
    engine.set_parameters(
        vt_symbol="BTCUSD_PERP.BINANCE",
        interval="1m",
        start=datetime(2022, 3, 1),
        end=datetime(2022, 3, 31),
        rate=0.3/10000,
        slippage=0.2,
        size=300,
        pricetick=0.2,
        capital=1_000_000,
        mode=BacktestingMode.BAR
    )
    engine.add_strategy(DoubleMaStrategy, {})
    path = "/app/dataset/BTCUSD_PERP-1m-2022-03.csv"
    # abs_path = os.getcwd() + "/vnpy/dataset/ETHUSDT-15m-2022-02.csv"
    engine.load_data(path)

    engine.run_backtesting()
    df = engine.calculate_result()
    df.index = pd.Index([str(i) for i in df.index])
    statistics = engine.calculate_statistics()
    a = df.drop("trades", 1)

    # setting = OptimizationSetting()
    # setting.set_target("sharpe_ratio")
    # setting.add_parameter("slow_window", 3, 15, 1)
    # setting.add_parameter("fast_window", 10, 30, 1)
    #
    # engine.run_bf_optimization(setting, self_evaluate=evaluate)
    return a.to_dict(), statistics


# if __name__ == '__main__':
#     exec()
