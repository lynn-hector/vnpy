from trader.utility import BarGenerator, ArrayManager
import csv
import pandas as pd
from datetime import datetime
from trader.object import TickData, BarData
from trader.object import Exchange

data = []


def on_bar(bar: BarData):
    print("do something")
    data.append(bar)
    return


def on_15min_bar():
    return


bg = BarGenerator(on_bar)
am = ArrayManager()


def gen_bar(row, last_tick=False):
    td = TickData(
        symbol="etc",
        exchange=Exchange.BINANCE,
        datetime=datetime.strptime(row["tra_time"], '%Y-%m-%d %H:%M:%S.%f'),
        name="etc",
        volume=row["vol"],
        turnover=row["vol"] * row["price"],
        open_interest=0,
        last_price=row["price"],
        last_volume=row["tra_time"],
        gateway_name="DB"
    )
    bg.update_tick(td, last_tick)
    return


def main():
    filename = "/app/dataset/aaa.csv"
    df = pd.read_csv(filename)
    if df is not None and not df.empty:
        for ix, row in df.iterrows():
            if ix == 5891:
                gen_bar(row, True)
                break
            gen_bar(row)
    else:
        print("Csv file has no Data!")
        return

    a = data[-1]
    print("gen kline is ok")


if __name__ == '__main__':
    main()
