import Public.COMMON as COMMON
import pandas as pd
import datetime
import os

# https://mops.twse.com.tw/mops/web/t163sb04


# 爬蟲綜合損益表資料
def crawl_comprehensiveIncome(year, season, stocktype):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'TYPEK': stocktype,
        'code': '',
        'year': COMMON.year_CE2RC(year),
        'season': season
    }

    # 拆解內容
    table_array = COMMON.crawl_data2text(url, form_data).split('<table')
    dfcomprehensiveIncome = pd.DataFrame()

    dtTitle = {
        'Revenue1': ['利息淨收益', '營業收入', '淨收益', '收益', '收入'],
        'Revenue2': ['利息以外淨損益'],
        'GrossProfit': ['營業毛利（毛損）'],
        'BusinessInterest': ['營業利益（損失）', '營業利益'],
        'NetProfitBeforeTax':
        ['繼續營業單位稅前淨利（淨損）', '稅前淨利（淨損）', '繼續營業單位稅前損益', '繼續營業單位稅前純益（純損）'],
        'NetProfitAfterTax': ['本期稅後淨利（淨損）', '本期淨利（淨損）'],
        'NetProfitOfParentCompanyOwners': ['淨利（損）歸屬於母公司業主', '淨利（淨損）歸屬於母公司業主'],
        'EPS': ['基本每股盈餘（元）']
    }

    for table in table_array:
        if '代號</th>' in table:
            tr_array = table.split('<tr')
            dtIndex = {
                'Revenue1': -1,
                'Revenue2': -1,
                'GrossProfit': -1,
                'BusinessInterest': -1,
                'NetProfitBeforeTax': -1,
                'NetProfitAfterTax': -1,
                'NetProfitOfParentCompanyOwners': -1,
                'EPS': -1,
            }

            for tr in tr_array:
                if '<th' in tr:
                    th_array = tr.split('<th')
                    for thIndex in range(1, len(th_array)):
                        title = COMMON.col_clear(th_array[thIndex]).strip()
                        for key in dtTitle.keys():
                            if title in dtTitle[key]:
                                dtIndex[key] = thIndex
                elif '<td' in tr:
                    td_array = tr.split('<td')
                    #公司代號, 年, 季
                    code = COMMON.col_clear(td_array[1])
                    index = (code, COMMON.year_RC2CE(year), season)

                    Revenue1, Revenue2, GrossProfit, BusinessInterest, NetProfitBeforeTax, NetProfitAfterTax, NetProfitOfParentCompanyOwners, EPS = 0, 0, 0, 0, 0, 0, 0, 0

                    if dtIndex['Revenue1'] >= 0:
                        Revenue1, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(td_array[dtIndex['Revenue1']]))
                    if dtIndex['Revenue2'] >= 0:
                        Revenue2, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(td_array[dtIndex['Revenue2']]))
                    if dtIndex['GrossProfit'] >= 0:
                        GrossProfit, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(td_array[dtIndex['GrossProfit']]))
                    if dtIndex['BusinessInterest'] >= 0:
                        BusinessInterest, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['BusinessInterest']]))
                    if dtIndex['NetProfitBeforeTax'] >= 0:
                        NetProfitBeforeTax, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['NetProfitBeforeTax']]))
                    if dtIndex['NetProfitAfterTax'] >= 0:
                        NetProfitAfterTax, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['NetProfitAfterTax']]))
                    if dtIndex['NetProfitOfParentCompanyOwners'] >= 0:
                        NetProfitOfParentCompanyOwners, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(td_array[
                                dtIndex['NetProfitOfParentCompanyOwners']]))
                    if dtIndex['EPS'] >= 0:
                        EPS, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(td_array[dtIndex['EPS']]))

                    data = [
                        Revenue1 + Revenue2, GrossProfit, BusinessInterest
                        if BusinessInterest > 0 else NetProfitBeforeTax,
                        NetProfitBeforeTax, NetProfitAfterTax,
                        NetProfitOfParentCompanyOwners, EPS
                    ]

                    stockpd = pd.DataFrame(
                        data=[data],
                        index=pd.MultiIndex.from_tuples([index]),
                        columns=[
                            '營收', '毛利', '營業利益', '稅前淨利', '稅後淨利', '母公司業主淨利',
                            'EPS'
                        ])
                    dfcomprehensiveIncome = dfcomprehensiveIncome.append(
                        stockpd)

    return dfcomprehensiveIncome


# 爬10年資料並匯出csv
def get_comprehensiveIncome_crawl(StocksData, fromN2Now):
    eyyyy = datetime.datetime.today().year
    syyyy = eyyyy - fromN2Now
    oCnt = len(StocksData)

    for yyyy in range(syyyy, eyyyy):
        for season in (range(1, 5)):
            try:
                StocksData.loc[slice(None), yyyy, season].head()
            except:
                try:
                    StocksData = StocksData.append(
                        crawl_comprehensiveIncome(yyyy, season,
                                                  COMMON.__LISTEDCODE__))
                    StocksData = StocksData.append(
                        crawl_comprehensiveIncome(yyyy, season,
                                                  COMMON.__OTCCODE__))
                    StocksData = StocksData.append(
                        crawl_comprehensiveIncome(yyyy, season,
                                                  COMMON.__EMERGINGSCODE__))
                    StocksData = StocksData.append(
                        crawl_comprehensiveIncome(yyyy, season,
                                                  COMMON.__PUBLICCODE__))
                except:
                    print(f'{yyyy}/{season}-NO DATA')

    if len(StocksData) > oCnt:
        path = os.path.abspath('./data/')
        StocksData.to_csv(f'{path}/comprehensiveIncome.csv',
                          index_label=['公司代號', '所屬年度', '季'])
        COMMON.UpdateDataRecord('comprehensiveIncome')


# 讀取綜合資料
def get_comprehensiveIncome_data(n=6, reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/comprehensiveIncome.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(file, dtype={'公司代號': str})
        StocksData = StocksData.set_index(['公司代號', '所屬年度', '季'])
        lastUpdDate = COMMON.GetDataRecord('comprehensiveIncome')
        if len(lastUpdDate)==0 or datetime.datetime(lastUpdDate[0], lastUpdDate[1], lastUpdDate[2])<datetime.datetime.today():
            get_comprehensiveIncome_crawl(StocksData, n)
        return StocksData
    else:
        # 預設帶出近6年
        print('RELOAD comprehensiveIncome......')
        get_comprehensiveIncome_crawl(pd.DataFrame(), n)
        return get_comprehensiveIncome_data()
