import requests
from io import StringIO
import pandas as pd

#公司代號,公司名稱,成交股數,成交筆數,成交金額,收盤價,本益比(今日))
def price_date(date):
    # 下載股價
    r = requests.post(
        'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' +
        date.strftime('%Y%m%d') + '&type=ALL')

    # 整理資料，變成表格
    df = pd.read_csv(
        StringIO(r.text.replace("=", "")),
        header=["證券代號" in l for l in r.text.split("\n")].index(True) - 1,
        usecols=['證券代號', '證券名稱', '成交股數', '成交筆數', '成交金額', '收盤價'])

    # 整理一些字串：
    data = []
    dfindex = []
    for index, row in df.iterrows():
        try:
            code = float(row['證券代號'])
            name = row['證券名稱']
            tradingvolume = float(row['成交股數'])
            transaction = float(row['成交筆數'])
            tradvalue = float(row['成交金額'])
            closevalue = float(row['收盤價'])
            peratio = float(row['本益比'])

            data.append([
                code, name, tradingvolume, transaction, tradvalue, closevalue,
                peratio
            ])
            dfindex.append(code)
        except ValueError:
            continue

    return pd.DataFrame(
        data=data,
        index=dfindex,
        columns=['公司代號', '公司名稱', '成交股數', '成交筆數', '成交金額', '收盤價', '本益比(今日))'])
