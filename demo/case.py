from app.binance_api_backtester.engine import BinanceApiBacktestingEngine
from app.cta_strategy.strategies.double_ma_strategy import (
    DoubleMaStrategy,
)
from datetime import datetime

def main():
    engine = BinanceApiBacktestingEngine()
    engine.set_parameters(
        vt_symbol="BTCUSDT.BINANCE",
        interval="15m",
        start=datetime.strptime("2022-03-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
        end=datetime.strptime("2022-04-30 00:00:00", "%Y-%m-%d %H:%M:%S"),
        rate=float("0.001"),
        slippage=float("0.001"),
        size=1,
        pricetick=float("0.001"),
        capital=100000,
    )

    engine.add_strategy(DoubleMaStrategy, {})

    engine.load_data()
    engine.run_backtesting()
    daily_df = engine.calculate_result()
    statistics = engine.calculate_statistics()
    print(statistics)


if __name__ == '__main__':
    main()
