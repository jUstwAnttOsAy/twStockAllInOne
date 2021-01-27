import Public.COMMON as COMMON
import pandas as pd
import datetime
import os

# https://mops.twse.com.tw/mops/web/t163sb04


# 爬蟲資產負債表資料
def crawl_balanceSheet(year, season, stocktype):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'isQuery': 'Y',
        'TYPEK': stocktype,
        'year': COMMON.year_CE2RC(year),
        'season': season
    }

    # 拆解內容
    table_array = COMMON.crawl_data2text(url, form_data).split('<table')
    dfbalanceSheet = pd.DataFrame()

    dtTitle = {
        'TotalAssets': ['資產總額', '資產總計'],
        'StockholdersEquity': ['權益總計', '權益總額'],
        'NetAssetValueShare': ['每股參考淨值'],
        'CurrentAssets': ['流動資產'],
        'NoncurrentAssets': ['非流動資產'],
        'CurrentLiabilities': ['流動負債'],
        'NoncurrentLiabilities': ['非流動負債'],
        'TotalLiabilities': ['負債總計', '負債總額']
    }

    for table in table_array:
        if '代號</th>' in table:
            tr_array = table.split('<tr')
            dtIndex = {
                'TotalAssets': -1,
                'StockholdersEquity': -1,
                'NetAssetValueShare': -1,
                'CurrentAssets': -1,
                'NoncurrentAssets': -1,
                'CurrentLiabilities': -1,
                'NoncurrentLiabilities': -1,
                'TotalLiabilities': -1,
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

                    TotalAssets, StockholdersEquity, NetAssetValueShare, CurrentAssets, NoncurrentAssets, CurrentLiabilities, NoncurrentLiabilities, TotalLiabilities = 0, 0, 0, 0, 0, 0, 0, 0

                    if dtIndex['TotalAssets'] >= 0:
                        TotalAssets, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(td_array[dtIndex['TotalAssets']]))
                    if dtIndex['StockholdersEquity'] >= 0:
                        StockholdersEquity, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['StockholdersEquity']]))
                    if dtIndex['NetAssetValueShare'] >= 0:
                        NetAssetValueShare, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['NetAssetValueShare']]))
                    if dtIndex['CurrentAssets'] >= 0:
                        CurrentAssets, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['CurrentAssets']]))
                    if dtIndex['NoncurrentAssets'] >= 0:
                        NoncurrentAssets, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['NoncurrentAssets']]))
                    if dtIndex['CurrentLiabilities'] >= 0:
                        CurrentLiabilities, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['CurrentLiabilities']]))
                    if dtIndex['NoncurrentLiabilities'] >= 0:
                        NoncurrentLiabilities, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['NoncurrentLiabilities']]))
                    if dtIndex['TotalLiabilities'] >= 0:
                        TotalLiabilities, vaild = COMMON.TryParse(
                            'float',
                            COMMON.col_clear(
                                td_array[dtIndex['TotalLiabilities']]))

                    data = [
                        TotalAssets, TotalLiabilities, StockholdersEquity,
                        NetAssetValueShare, CurrentAssets, NoncurrentAssets,
                        CurrentLiabilities, NoncurrentLiabilities
                    ]

                    stockpd = pd.DataFrame(
                        data=[data],
                        index=pd.MultiIndex.from_tuples([index]),
                        columns=[
                            '資產總額', '負債總額', '權益總額', '每股參考淨值', '流動資產', '非流動資產',
                            '流動負債', '非流動負債'
                        ])
                    dfbalanceSheet = dfbalanceSheet.append(stockpd)

    return dfbalanceSheet


# 爬10年資料並匯出csv
def get_balanceSheet_crawl(StocksData, fromN2Now):
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
                        crawl_balanceSheet(yyyy, season, COMMON.__LISTEDCODE__))
                    StocksData = StocksData.append(
                        crawl_balanceSheet(yyyy, season, COMMON.__OTCCODE__))
                    StocksData = StocksData.append(
                        crawl_balanceSheet(yyyy, season,
                                           COMMON.__EMERGINGSCODE__))
                    StocksData = StocksData.append(
                        crawl_balanceSheet(yyyy, season, COMMON.__PUBLICCODE__))
                except:
                    print(f'{yyyy}/{season}-NO DATA')

    if len(StocksData) > oCnt:
        path = os.path.abspath('./data/')
        StocksData.to_csv(f'{path}/balanceSheet.csv',
                          index_label=['公司代號', '所屬年度', '季'])
        COMMON.UpdateDataRecord('balanceSheet')

# 讀取資產負債表資料


def get_balanceSheet_data(n=10, reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/balanceSheet.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(
            file, index_col=[0, 1, 2], dtype={'公司代號': str})
        get_balanceSheet_crawl(StocksData, n)
        return StocksData
    else:
        # 預設帶出近10年
        print('RELOAD balanceSheet......')
        get_balanceSheet_crawl(pd.DataFrame(), n)
        return get_balanceSheet_data()
