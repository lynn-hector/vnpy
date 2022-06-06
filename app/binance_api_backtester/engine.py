import pandas as pd
import requests

from app.cta_strategy.backtesting import *


def generate_bar_from_row(row, symbol, exchange, interval):
    """
    Generate bar from row.
    """
    return BarData(
        symbol=symbol,
        exchange=Exchange(exchange),
        interval=interval,
        open_price=float(row[1]),
        high_price=float(row[2]),
        low_price=float(row[3]),
        close_price=float(row[4]),
        open_interest=float(0),
        volume=float(row[5]),
        turnover=float(row[7]),
        datetime=datetime.fromtimestamp(row[0] / 1000),
        gateway_name="DB",
    )

def get_kline():
    return


class BinanceApiBacktestingEngine(BacktestingEngine):
    def __init__(self):
        super().__init__()

    def load_data(self):
        """
        具体载入数据的长度，取决于load_bar函数的参数控制（策略模板默认是10天）。
        数据载入后会以逐根K线（或者Tick）的方式推送给策略，实现内部变量的初始化计算，比如缓存K线序列、计算技术指标等。
        """
        self.output("开始加载历史数据")

        if not self.end:
            self.end = datetime.now()

        if self.start >= self.end:
            self.output("起始日期必须小于结束日期")
            return

        self.history_data.clear()  # Clear previously loaded history data

        # Load data each time and allow for progress update
        if self.interval.endswith("m"):
            progress_delta = timedelta(days=10)
        elif self.interval.endswith("h"):
            progress_delta = timedelta(days=30)
        elif self.interval.endswith("d"):
            progress_delta = timedelta(days=365)
        elif self.interval.endswith("w"):
            progress_delta = timedelta(days=365)
        else:
            progress_delta = timedelta(days=30)

        total_delta = self.end - self.start
        interval_delta = INTERVAL_DELTA_MAP[self.interval]

        start = self.start
        end = self.start + progress_delta
        progress = 0

        while start < self.end:
            end = min(end, self.end)  # Make sure end time stays within set range
            start_tp = round(start.timestamp())
            end_tp = round(end.timestamp())


            # Generate
            symbol, exchange = self.vt_symbol.split(".")

            params = {
                "symbol": symbol,
                "interval": self.interval,
                "startTime": start_tp * 1000,
                "endTime": end_tp * 1000,
            }
            resp = requests.get(url="https://api.binance.com/api/v3/klines", params=params)
            if resp.status_code != 200:
                return
            res_data = resp.json()

            df = pd.DataFrame(res_data)
            data = []
            if df is not None and not df.empty:
                for ix, row in df.iterrows():
                    dt = datetime.fromtimestamp(row[0] / 1000)
                    if self.start < dt < self.end:
                        if self.mode == BacktestingMode.BAR:
                            data.append(generate_bar_from_row(row, symbol, exchange, self.interval))
                        else:
                            self.output("Currently not supported tick mode")
                            return
            else:
                self.output("Csv file has no Data!")
                return

            self.history_data.extend(data)
            # cal loading percent
            progress += progress_delta / total_delta
            progress = min(progress, 1)
            progress_bar = "#" * int(progress * 10)
            self.output(f"加载进度：{progress_bar} [{progress:.0%}]")

            start = end + interval_delta
            end += progress_delta + interval_delta

        self.output(f"历史数据加载完成，数据量：{len(self.history_data)}")

    # def run_bf_optimization(self, optimization_setting: OptimizationSetting, output=True):
    #     """运行穷举算法优化器"""
    #     if not check_optimization_setting(optimization_setting):
    #         return
    #     # wrap_evaluate作用：给engine包装评估函数
    #     # 评估函数
    #     evaluate_func: callable = wrap_evaluate(self, optimization_setting.target_name)
    #     results = run_bf_optimization(
    #         evaluate_func,
    #         optimization_setting,
    #         get_target_value,
    #         output=self.output
    #     )
    #
    #     if output:
    #         for result in results:
    #             msg: str = f"参数：{result[0]}, 目标：{result[1]}"
    #             self.output(msg)
    #
    #     return results


def evaluate(
        target_name: str,
        strategy_class: CtaTemplate,
        vt_symbol: str,
        interval: Interval,
        start: datetime,
        rate: float,
        slippage: float,
        size: float,
        pricetick: float,
        capital: int,
        end: datetime,
        mode: BacktestingMode,
        inverse: bool,
        setting: dict
):
    """
    Function for running in multiprocessing.pool
    """
    engine = BinanceApiBacktestingEngine()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=interval,
        start=start,
        rate=rate,
        slippage=slippage,
        size=size,
        pricetick=pricetick,
        capital=capital,
        end=end,
        mode=mode,
        inverse=inverse
    )

    engine.add_strategy(strategy_class, setting)
    engine.load_data("dataset/ETHUSDT-15m-2022-02.csv")
    engine.run_backtesting()
    engine.calculate_result()
    statistics = engine.calculate_statistics(output=False)

    target_value = statistics[target_name]
    return (str(setting), target_value, statistics)

