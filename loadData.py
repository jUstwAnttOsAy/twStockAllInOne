import Public.COMMON as COMMON
import arrow
import pandas as pd
from io import StringIO
import os


def crawl_DQ(date):
    strDate = date.format('YYYYMMDD')
    # 下載股價
    url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={strDate}&type=ALL'
    rText = COMMON.crawl_data2text(
        url, '', 'big5', delay=3000).replace('=', '').replace('\r', '')

    def asFloat(x): return x if x == '--' else float(x.replace(',', ''))

    # 整理資料，變成表格
    df = pd.read_csv(StringIO(rText), header=['證券代號' in l for l in rText.split("\n")].index(True) - 1,
                     index_col=False,
                     converters={'成交股數': asFloat, '成交筆數': asFloat, '開盤價': asFloat, '最高價': asFloat, '最低價': asFloat, '收盤價': asFloat,
                                 '漲跌價差': asFloat, '最後揭示買價': asFloat, '最後揭示買量': asFloat, '最後揭示賣價': asFloat, '最後揭示賣量': asFloat},
                     usecols=['證券代號', '成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌(+/-)', '漲跌價差', '最後揭示買價', '最後揭示買量', '最後揭示賣價', '最後揭示賣量', '本益比'])

    df.columns = ['ticker', 'TVol', 'TXN', 'TV', 'OP', 'HP', 'LP',
                  'CP', 'Dir', 'CHG', 'LBBP', 'LBBV', 'LBSP', 'LBSV', 'PER']
    df['Date'] = strDate
    df = df.set_index(['ticker', 'Date'])

    return df


# 爬近60日資料並匯出csv


def get_DQ_crawl(StocksData, fromN2Now):
    currDate = arrow.now()
    cnt = 0
    oCnt = 0 if StocksData.empty else len(StocksData)
    while cnt < fromN2Now:
        strDate = currDate.format('YYYYMMDD')
        intDate, vaild = COMMON.TryParse('int', strDate)
        if StocksData.empty or intDate not in StocksData.index.get_level_values(1):
            try:
                StocksData = StocksData.append(crawl_DQ(currDate))
                cnt += 1
            except:
                print(f'{strDate}-NO DATA')
        elif len(StocksData) > 0 and intDate in StocksData.index.get_level_values(1):
            cnt += 1
        currDate = currDate.shift(days=-1)

    if StocksData.empty != True and len(StocksData) > oCnt:
        path = os.path.abspath('./data/')
        StocksData.sort_index().to_csv(
            f'{path}/DQ.csv', index_label=['ticker', 'Date'])
        COMMON.UpdateDataRecord('DQ')

# 讀取股利資料


def get_DQ_data(n=1, reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/DQ.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(file, dtype={'ticker': str})
        StocksData = StocksData.set_index(['ticker', 'Date'])
        arrlastUpdDate = COMMON.GetDataRecord('DQ')
        today = arrow.now()
        if len(arrlastUpdDate) == 3:
            yy, mm, dd = arrlastUpdDate
            lastUpdDate = arrow.get(yy, mm, dd)
            n = (today-lastUpdDate).days
        if n > 0:
            print(n)
            get_DQ_crawl(StocksData, n)
        return StocksData.sort_index()
    else:
        # 預設帶出近n日
        print('RELOAD DQ......')
        get_DQ_crawl(pd.DataFrame(), n)
        return get_DQ_data()


get_DQ_data(reload=True)
