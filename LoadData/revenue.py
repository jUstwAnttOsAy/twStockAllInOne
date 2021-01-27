import Public.COMMON as COMMON
from datetime import date
import pandas as pd
import os

# 公司代號,資料年月,營業收入-上月比較增減(%),營業收入-去年同月增減(%),累計營業收入-前期比較增減(%)


def crawl_revenue(year, month, stocktype):
    dfRevenue = pd.read_csv(
        f'https://mops.twse.com.tw/nas/t21/{stocktype}/t21sc03_{str(COMMON.year_CE2RC(year))}_{str(month)}.csv',
        usecols=[
            '公司代號', '資料年月', '營業收入-當月營收', '營業收入-上月營收', '營業收入-去年當月營收', '營業收入-上月比較增減(%)', '營業收入-去年同月增減(%)', '累計營業收入-當月累計營收', '累計營業收入-去年累計營收', '累計營業收入-前期比較增減(%)'
        ],
        index_col=['公司代號', '資料年月'],
        converters={'資料年月': lambda x: COMMON.date_RC2CE(x)})

    dfRevenue = pd.read_csv(
        f'https://mops.twse.com.tw/nas/t21/{stocktype}/t21sc03_{str(COMMON.year_CE2RC(year))}_{str(month)}.csv',
        usecols=[
            '公司代號', '資料年月', '營業收入-當月營收', '營業收入-上月營收', '營業收入-去年當月營收', '營業收入-上月比較增減(%)', '營業收入-去年同月增減(%)', '累計營業收入-當月累計營收', '累計營業收入-去年累計營收', '累計營業收入-前期比較增減(%)'
        ],
        index_col=['公司代號', '資料年月'],
        converters={'資料年月': lambda x: COMMON.date_RC2CE(x)})

    return dfRevenue


def get_Revenue_crawl(StocksData, fromN2Now):
    revenueDate = date.today()
    oCnt = len(StocksData)
    for i in range(fromN2Now):
        revenueDate, YYMM = COMMON.minusMonth(revenueDate, '%Y/%m')
        arrYYMM = YYMM.split('/')

        intYYYY, vaild = COMMON.TryParse('int', arrYYMM[0])
        intMM, vaild = COMMON.TryParse('int', arrYYMM[1])

        if StocksData.empty or f'{str(intYYYY)}/{str(intMM)}' not in StocksData.index.get_level_values(1):
            try:
                StocksData = StocksData.append(
                    crawl_revenue(intYYYY, intMM, COMMON.__LISTEDCODE__))
                StocksData = StocksData.append(
                    crawl_revenue(intYYYY, intMM, COMMON.__OTCCODE__))
                StocksData = StocksData.append(
                    crawl_revenue(intYYYY, intMM, COMMON.__EMERGINGSCODE__))
                StocksData = StocksData.append(
                    crawl_revenue(intYYYY, intMM, COMMON.__PUBLICCODE__))
            except:
                print(f'{arrYYMM}-NO DATA')

    if len(StocksData) > oCnt:
        path = os.path.abspath('./data/')
        StocksData.to_csv(f'{path}/revenue.csv', index_label=['公司代號', '資料年月'])
        COMMON.UpdateDataRecord('revenue')

# 讀取營收資料


def get_Revenue_data(n=120, reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/revenue.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(file, index_col=[0, 1], dtype={'公司代號': str})
        get_Revenue_crawl(StocksData, n)
        return StocksData
    else:
        # 預設帶出近10年
        print('RELOAD REVENUE......')
        get_Revenue_crawl(pd.DataFrame, n)
        return get_Revenue_data()
