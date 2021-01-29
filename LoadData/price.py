import Public.COMMON as COMMON
import datetime
import pandas as pd
from io import StringIO
import os

# 公司代號,公司名稱,成交股數,成交筆數,成交金額,收盤價,本益比(今日))


def crawl_price(date):
    strDate = date.strftime('%Y%m%d')
    # 下載股價
    url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={strDate}&type=ALL'
    rText = COMMON.crawl_data2text(
        url, '', 'big5', delay=3000).replace('=', '').replace('\r', '')

    # 整理資料，變成表格
    df = pd.read_csv(StringIO(rText),
                     header=["證券代號" in l for l in rText.split(
                         "\n")].index(True) - 1,
                     usecols=['證券代號', '成交股數', '成交筆數', '成交金額', '收盤價', '本益比'])

    # 整理一些字串：
    data = []
    dfindex = []
    for index, row in df.iterrows():
        try:
            code = row['證券代號']
            priceDate = strDate
            tradingvolume, vaild = COMMON.TryParse(
                'float', row['成交股數'].replace(',', ''))
            transaction, vaild = COMMON.TryParse(
                'float', row['成交筆數'].replace(',', ''))
            tradvalue, vaild = COMMON.TryParse(
                'float', row['成交金額'].replace(',', ''))
            closevalue, vaild = COMMON.TryParse(
                'float', row['收盤價'].replace(',', ''))
            peratio, vaild = COMMON.TryParse(
                'float', row['本益比'].replace(',', ''))

            data.append([
                tradingvolume, transaction, tradvalue, closevalue, peratio
            ])
            dfindex.append((code, priceDate))
        except ValueError:
            continue

    return pd.DataFrame(
        data=data,
        index=pd.MultiIndex.from_tuples(dfindex),
        columns=['成交股數', '成交筆數', '成交金額', '收盤價', '本益比'])

# 爬近60日資料並匯出csv


def get_price_crawl(StocksData, fromN2Now):
    oneDay = datetime.timedelta(days=1)
    currDate = datetime.datetime.today()
    cnt = 0
    oCnt = 0 if StocksData.empty else len(StocksData)
    while cnt < fromN2Now:
        strDate = currDate.strftime('%Y%m%d')
        intDate, vaild = COMMON.TryParse('int', strDate)
        if StocksData.empty or intDate not in StocksData.index.get_level_values(1):
            try:
                StocksData = StocksData.append(crawl_price(currDate))
                cnt += 1
            except:
                print(f'{strDate}-NO DATA')
        elif len(StocksData)>0 and intDate in StocksData.index.get_level_values(1):
            cnt += 1
        currDate = currDate-oneDay

    if StocksData.empty!=True and len(StocksData) > oCnt:
        path = os.path.abspath('./data/')
        StocksData.sort_index().to_csv(f'{path}/price.csv', index_label=['公司代號', '資料日期'])
        COMMON.UpdateDataRecord('price')

# 讀取股利資料


def get_price_data(n=10, reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/price.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(file, dtype={'公司代號': str})
        StocksData = StocksData.set_index(['公司代號', '資料日期'])
        arrlastUpdDate = COMMON.GetDataRecord('price')
        today = datetime.datetime.today()
        if len(arrlastUpdDate)==3:
            yy,mm,dd = arrlastUpdDate
            lastUpdDate = datetime.datetime(yy,mm,dd)
            n = (today-lastUpdDate).days
        if n>0:
            print(n)
            get_price_crawl(StocksData, n)
        return StocksData.sort_index()
    else:
        # 預設帶出近n日
        print('RELOAD Price......')
        get_price_crawl(pd.DataFrame(), n)
        return get_price_data()
