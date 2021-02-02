import Public.COMMON as COMMON
import arrow
import pandas as pd
from io import StringIO
import os


# 公司資訊(ComInfo)
def crawl_comInfo_type(stocktype):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t51sb01'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'TYPEK': stocktype,
        'code': '',
    }

    # 拆解內容
    table_array = COMMON.crawl_data2text(url, form_data).split('<table')
    tr_array = table_array[2].split('<tr')

    # 拆解td
    data, index = [], []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 17):
            # 公司代號, 公司名稱, 公司簡稱, 產業類別
            Ticker = COMMON.col_clear(td_array[1])
            ComName = COMMON.col_clear(td_array[2])
            Com = COMMON.col_clear(td_array[3])
            IC = COMMON.col_clear(td_array[4])
            ESTD = arrow.get(COMMON.date_RC2CE(COMMON.col_clear(td_array[14])))
            LISTD = arrow.get(COMMON.date_RC2CE(COMMON.col_clear(
                td_array[15])))
            AoC = COMMON.col_clear(td_array[17])
            index.append(Ticker)
            data.append([ComName, Com, IC, ESTD, LISTD, AoC])

    dfComInfo = pd.DataFrame(
        data=data,
        index=index,
        columns=['ComName', 'Com', 'IC', 'ESTD', 'LISTD', 'AoC'])

    return dfComInfo


# 取得公司資料並匯出csv
def crawl_comInfo():
    df = pd.DataFrame()

    for code in COMMON.__TICKERTYPECODE__.values():
        df = df.append(crawl_comInfo_type(code))

    return df.sort_index()


# 彙整-股價資訊(日)(DQ)
def crawl_DQ(date):
    strDate = date.format('YYYYMMDD')
    # 下載股價
    url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={strDate}&type=ALL'
    rText = COMMON.crawl_data2text(url, '', 'big5',
                                   delay=3000).replace('=',
                                                       '').replace('\r', '')

    def asFloat(x):
        return x if x == '--' else float(x.replace(',', ''))

    # 整理資料，變成表格
    df = pd.read_csv(StringIO(rText),
                     header=['證券代號' in l
                             for l in rText.split("\n")].index(True) - 1,
                     index_col=False,
                     converters={
                         '成交股數': asFloat,
                         '成交筆數': asFloat,
                         '開盤價': asFloat,
                         '最高價': asFloat,
                         '最低價': asFloat,
                         '收盤價': asFloat,
                         '漲跌價差': asFloat,
                         '最後揭示買價': asFloat,
                         '最後揭示買量': asFloat,
                         '最後揭示賣價': asFloat,
                         '最後揭示賣量': asFloat
                     },
                     usecols=[
                         '證券代號', '成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價',
                         '收盤價', '漲跌(+/-)', '漲跌價差', '最後揭示買價', '最後揭示買量',
                         '最後揭示賣價', '最後揭示賣量', '本益比'
                     ])

    df.columns = [
        'ticker', 'TVol', 'TXN', 'TV', 'OP', 'HP', 'LP', 'CP', 'Dir', 'CHG',
        'LBBP', 'LBBV', 'LBSP', 'LBSV', 'PER'
    ]
    df['Date'] = strDate
    df = df.set_index(['ticker', 'Date'])

    return df.sort_index()


# 彙整-營收資訊(月)(REV)
def crawl_REV_type(year, month, stocktype):
    df = pd.read_csv(
        f'https://mops.twse.com.tw/nas/t21/{stocktype}/t21sc03_{str(COMMON.year_CE2RC(year))}_{str(month)}.csv',
        usecols=[
            '公司代號', '資料年月', '營業收入-當月營收', '營業收入-上月營收', '營業收入-去年當月營收',
            '營業收入-上月比較增減(%)', '營業收入-去年同月增減(%)', '累計營業收入-當月累計營收',
            '累計營業收入-去年累計營收', '累計營業收入-前期比較增減(%)'
        ],
        index_col=['公司代號', '資料年月'],
        converters={'資料年月': lambda x: year * 100 + month})

    df.columns = [
        'Ticker', 'ym', 'RevM', 'RevLM', 'RevLYM', 'RevMcLM', 'RevMcLYM',
        'RevYCml', 'RevLYCml', 'RevYCml2LYCml'
    ]

    return df


def crawl_REV(year, month):
    df = pd.DataFrame()

    for code in COMMON.__TICKERTYPECODE__.values():
        df = df.append(crawl_REV_type(year, month, code))

    return df.sort_index()


# 彙整-綜合損益表(季)(SCI)
def crawl_SCI_type(year, season, stocktype):
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
        'Rev1': ['利息淨收益', '營業收入', '淨收益', '收益', '收入'],
        'Rev2': ['利息以外淨損益'],
        'GP': ['營業毛利（毛損）'],
        'OP': ['營業利益（損失）', '營業利益'],
        'NPBT': ['繼續營業單位稅前淨利（淨損）', '稅前淨利（淨損）', '繼續營業單位稅前損益', '繼續營業單位稅前純益（純損）'],
        'NPAT': ['本期稅後淨利（淨損）', '本期淨利（淨損）'],
        'NPPC': ['淨利（損）歸屬於母公司業主', '淨利（淨損）歸屬於母公司業主'],
        'EPS': ['基本每股盈餘（元）']
    }

    for table in table_array:
        if '代號</th>' in table:
            tr_array = table.split('<tr')
            dtIndex = {
                'Rev1': -1,
                'Rev2': -1,
                'GP': -1,
                'OP': -1,
                'NPBT': -1,
                'NPAT': -1,
                'NPPC': -1,
                'EPS': -1
            }

            for tr in tr_array:
                if '<th' in tr:
                    th_array = tr.split('<th')
                    for thIndex in range(1, len(th_array)):
                        title = COMMON.col_clear(th_array[thIndex]).strip()
                        for key in dtTitle.keys():
                            if title in dtTitle[key]:
                                dtIndex[key] = thIndex
                    continue
                td_array = tr.split('<td')
                #公司代號, 年, 季
                ticker = COMMON.col_clear(td_array[1])
                index = (ticker, COMMON.year_RC2CE(year), season)

                dtData = {
                    'Rev1': 0,
                    'Rev2': 0,
                    'GP': 0,
                    'OP': 0,
                    'NPBT': 0,
                    'NPAT': 0,
                    'NPPC': 0,
                    'EPS': 0
                }

                for key in dtIndex.keys():
                    if dtIndex[key] >= 0:
                        val, vaild = COMMON.TryParse(
                            'float', COMMON.col_clear(td_array[dtIndex[key]]))
                        dtData[key] = val

                data = [
                    dtData['Rev1'] + dtData['Rev2'], dtData['GP'],
                    dtData['OP'] if dtData['OP'] > 0 else dtData['NPBT'],
                    dtData['NPBT'], dtData['NPAT'], dtData['NPPC'],
                    dtData['EPS']
                ]

                df = pd.DataFrame(
                    data=[data],
                    index=pd.MultiIndex.from_tuples([index]),
                    columns=['Rev', 'GP', 'OP', 'NPBT', 'NPAT', 'NPPC', 'EPS'])

                df['GM'] = df['GP'] / df['Rev']
                dfcomprehensiveIncome = dfcomprehensiveIncome.append(df)

    return dfcomprehensiveIncome


def crawl_SCI(year, season):
    df = pd.DataFrame()

    for code in COMMON.__TICKERTYPECODE__.values():
        df = df.append(crawl_SCI_type(year, code))

    return df.sort_index()


# 彙整-資產負債表(季)(BS)
def crawl_BS_type(year, season, stocktype):
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
    dfBS = pd.DataFrame()

    dtTitle = {
        'TA': ['資產總額', '資產總計'],
        'TL': ['負債總計', '負債總額'],
        'TE': ['權益總計', '權益總額'],
        'RNP': ['每股參考淨值'],
        'CA': ['流動資產'],
        'NCA': ['非流動資產'],
        'CL': ['流動負債'],
        'NCL': ['非流動負債']
    }

    for table in table_array:
        if '代號</th>' in table:
            tr_array = table.split('<tr')
            dtIndex = {
                'TA': -1,
                'TL': -1,
                'TE': -1,
                'RNP': -1,
                'CA': -1,
                'NCA': -1,
                'CL': -1,
                'NCL': -1,
            }

            for tr in tr_array:
                if '<th' in tr:
                    th_array = tr.split('<th')
                    for thIndex in range(1, len(th_array)):
                        title = COMMON.col_clear(th_array[thIndex]).strip()
                        for key in dtTitle.keys():
                            if title in dtTitle[key]:
                                dtIndex[key] = thIndex
                    continue
                td_array = tr.split('<td')
                #公司代號, 年, 季
                ticker = COMMON.col_clear(td_array[1])
                index = (ticker, COMMON.year_RC2CE(year), season)

                dtData = {
                    'TA': 0,
                    'TL': 0,
                    'TE': 0,
                    'RNP': 0,
                    'CA': 0,
                    'NCA': 0,
                    'CL': 0,
                    'NCL': 0,
                }

                for key in dtIndex.keys():
                    if dtIndex[key] >= 0:
                        val, vaild = COMMON.TryParse(
                            'float', COMMON.col_clear(td_array[dtIndex[key]]))
                        dtData[key] = val

                data = [
                    dtData['TA'], dtData['TL'], dtData['TE'], dtData['RNP'],
                    dtData['CA'], dtData['NCA'], dtData['CL'], dtData['NCL']
                ]

                df = pd.DataFrame(data=[data],
                                  index=pd.MultiIndex.from_tuples([index]),
                                  columns=[
                                      '資產總額', '負債總額', '權益總額', '每股參考淨值', '流動資產',
                                      '非流動資產', '流動負債', '非流動負債'
                                  ])

                dfBS = dfBS.append(df)

    return dfBS


def crawl_BS(year, season):
    df = pd.DataFrame()

    for code in COMMON.__TICKERTYPECODE__.values():
        df = df.append(crawl_BS_type(year, code))

    return df.sort_index()


# 彙整-財務分析(年)(FSA)
def crawl_FSA_type(year, stocktype):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t51sb02'
    form_data = {
        'encodeURIComponent': 1,
        'run': 'Y',
        'step': 1,
        'TYPEK': stocktype,
        'year': COMMON.year_CE2RC(year),
        'isnew': '',
        'firstin': 1,
        'off': 1,
        'ifrs': 'Y',
    }

    # 拆解內容
    table_array = COMMON.crawl_data2text(url, form_data).split('<table')

    dfFSA = pd.DataFrame()

    tr_array = table_array[3].split('<tr')
    for tr in tr_array:
        td_array = tr.split('<td')
        if len(td_array) > 15:
            # 公司代號
            ticker = COMMON.col_clear(td_array[1]).split('-')[0].strip()
            # 負債占資產比率
            DR, vaild = COMMON.TryParse('float', COMMON.col_clear(td_array[3]))
            # 長期資金佔不動產廠房及設備比率
            LER, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[4]))
            # 流動比率
            CR, vaild = COMMON.TryParse('float', COMMON.col_clear(td_array[5]))
            # 速動比率
            UR, vaild = COMMON.TryParse('float', COMMON.col_clear(td_array[6]))
            # 利息保障倍數
            IPM, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[7]))
            # 應收款項周轉率
            ARTR, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[8]))
            # 平均收現日數
            ACCD, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[9]))
            # 存貨週轉率(次)
            ITR, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[10]))
            # 平均銷貨日數
            ASD, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[11]))
            # 不動產廠房及設備週轉率(次)
            PETR, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[12]))
            # 總資產週轉率(次)
            TATR, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[13]))
            # 資產報酬率(%)
            ROA, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[14]))
            # 權益報酬率(%)
            ROE, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[15]))
            # 稅前純益佔實收資本比率(%)
            NPBT2PCR, vaild = COMMON.TryParse('float',
                                              COMMON.col_clear(td_array[16]))
            # 純益率(%)
            NPR, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[17]))
            # 每股盈餘(元)
            EPS, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[18]))
            # 現金流量比率(%)
            CFR, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[19]))
            # 現金流量允當比率(%)
            CFAR, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[20]))
            # 現金再投資比率(%)
            CRR, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[21]))

            # 判斷是否有該公司當年度資料，更新/新增
            index = (ticker, COMMON.year_RC2CE(year))
            data = [
                DR, LER, CR, UR, IPM, ARTR, ACCD, ITR, ASD, PETR, TATR, ROA,
                ROE, NPBT2PCR, NPR, EPS, CFR, CFAR, CRR
            ]
            df = pd.DataFrame(data=[data],
                              index=pd.MultiIndex.from_tuples([index]),
                              columns=[
                                  'DR', 'LER', 'CR', 'UR', 'IPM', 'ARTR',
                                  'ACCD', 'ITR', 'ASD', 'PETR', 'TATR', 'ROA',
                                  'ROE', 'NPBT2PCR', 'NPR', 'EPS', 'CFR',
                                  'CFAR', 'CRR'
                              ])
            dfFSA = dfFSA.append(df)

    return dfFSA


def crawl_FSA(year, season):
    df = pd.DataFrame()

    for code in COMMON.__TICKERTYPECODE__.values():
        df = df.append(crawl_FSA_type(year, code))

    return df.sort_index()


# 彙整-鼓勵資訊(年)(DIV)
def crawl_DIV_type(year, stocktype):
    url = 'https://mops.twse.com.tw/server-java/t05st09sub'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'TYPEK': stocktype,
        'YEAR': COMMON.year_CE2RC(year),
        'first': '',
        'qryType': 2,
    }

    # 拆解內容
    table_array = COMMON.crawl_data2text(url, form_data,
                                         'big5').split('<table')

    dfDIV = pd.DataFrame()

    for table in table_array:
        if '公司代號' in table:
            tr_array = table.split('<tr')
            for tr in tr_array:
                td_array = tr.split('<td')
                if len(td_array) > 15:
                    # 公司代號
                    ticker = COMMON.col_clear(
                        td_array[1]).split('-')[0].strip()
                    # 所屬年度
                    intyr, vaild = COMMON.TryParse(
                        'int',
                        COMMON.col_clear(td_array[3]).split('年')[0])
                    yr = COMMON.year_RC2CE(intyr)
                    # 現金股利
                    CD, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[12]))
                    # 股票股利
                    SD, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[15]))
                    # 判斷是否有該公司當年度資料，更新/新增
                    index = (ticker, yr)

                    if len(dfDIV.index) > 0 and index in dfDIV.index:
                        data = dfDIV.loc[index]
                        data[0] = data[0] + CD
                        data[1] = data[1] + SD
                    else:
                        dfDIV = dfDIV.append(
                            pd.DataFrame(data=[[CD, SD]],
                                         index=pd.MultiIndex.from_tuples(
                                             [index]),
                                         columns=['CD', 'SD']))

    return dfDIV


def crawl_DIV_TDR_type(year, stocktype):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t66sb23'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': '1',
        'Off': '1',
        'TYPEK': stocktype,
        'YEAR': COMMON.year_CE2RC(year)
    }

    # 拆解內容
    table_array = COMMON.crawl_data2text(url, form_data,
                                         'big5').split('<table')

    dfDIVTDR = pd.DataFrame()

    for table in table_array:
        if '公司代號' in table:
            tr_array = table.split('<tr')
            for tr in tr_array:
                td_array = tr.split('<td')
                if len(td_array) > 15:
                    # 公司代號
                    ticker = COMMON.col_clear(
                        td_array[1]).split('-')[0].strip()
                    # 所屬年度
                    yr = COMMON.year_RC2CE(year)
                    # 現金股利
                    CD, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[11]))
                    # 股票股利
                    SD, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[13]))
                    # 判斷是否有該公司當年度資料，更新/新增
                    index = (ticker, yr)

                    if len(dfDIVTDR.index) > 0 and index in dfDIVTDR.index:
                        data = dfDIVTDR.loc[index]
                        data[0] = data[0] + CD
                        data[1] = data[1] + SD
                    else:
                        dfDIVTDR = dfDIVTDR.append(
                            pd.DataFrame(data=[[CD, SD]],
                                         index=pd.MultiIndex.from_tuples(
                                             [index]),
                                         columns=['CD', 'SD']))

    return dfDIVTDR


def crawl_DIV(year):
    df = pd.DataFrame()

    for code in COMMON.__TICKERTYPECODE__.values():
        df = df.append(crawl_DIV_type(year, code)).append(
            crawl_DIV_TDR_type(year, code))

    return df.sort_index()