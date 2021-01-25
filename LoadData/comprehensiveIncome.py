import Public.COMMON as COMMON
import pandas as pd
import datetime
import os

#https://mops.twse.com.tw/mops/web/t163sb04

# 爬蟲財務分析資料
def crawl_comprehensiveIncome(year, season, stocktype):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb19'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'TYPEK': stocktype,
        'code': '',
        'year': COMMON.year_CE2RC(year),
        'season':season
    }

    '''
    營收=營業收入	 218704469
    毛利=營業毛利（毛損） 90352125
    營業利益=營業利益（損失） 64266023
    稅前淨利=稅前淨利（淨損） 68181652
    稅後淨利=繼續營業單位本期淨利（淨損） 61387310
    母公司業主淨利=淨利（淨損）歸屬於母公司業主 61393851
    EPS=基本每股盈餘（元）
    '''
    # 拆解內容
    table_array = COMMON.crawl_data2text(url, form_data).split('<table')
    
    dfcomprehensiveIncome = pd.DataFrame()

    for table in table_array:
        if '公司代號' in table:
            tr_array = table.split('<tr')
            for tr in tr_array:
                td_array = tr.split('<td')
                if len(td_array) > 15:
                    #公司代號
                    CODE = COMMON.col_clear(td_array[1]).split('-')[0].strip()
                    #基本每股盈餘
                    EPS, vaild = COMMON.TryParse('float',
                                                  COMMON.col_clear(td_array[3]))
                    #長期資金佔不動產廠房及設備比率
                    LTFA, vaild = COMMON.TryParse('float',
                                                  COMMON.col_clear(td_array[4]))
                    #流動比率
                    CURR, vaild = COMMON.TryParse('float',
                                                  COMMON.col_clear(td_array[5]))
                    #速動比率
                    QUIR, vaild = COMMON.TryParse('float',
                                                  COMMON.col_clear(td_array[6]))
                    #利息保障倍數
                    IPM, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[7]))
                    #應收款項周轉率
                    RECTURR, vaild = COMMON.TryParse('float',
                                                  COMMON.col_clear(td_array[8]))
                    #平均收現日數
                    AVGCCD, vaild = COMMON.TryParse('float',
                                                    COMMON.col_clear(td_array[9]))
                    #存貨週轉率(次)
                    INVTUR, vaild = COMMON.TryParse('float',
                                                    COMMON.col_clear(td_array[10]))
                    #平均銷貨日數
                    AVGSALESD, vaild = COMMON.TryParse('float',
                                                      COMMON.col_clear(td_array[11]))
                    #不動產廠房及設備週轉率(次)
                    RPETURR, vaild = COMMON.TryParse('float',
                                                    COMMON.col_clear(td_array[12]))
                    #總資產週轉率(次)
                    TATUR, vaild = COMMON.TryParse('float',
                                                  COMMON.col_clear(td_array[13]))
                    #資產報酬率(%)
                    ROA, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[14]))
                    #權益報酬率(%)
                    ROE, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[15]))
                    #稅前純益佔實收資本比率(%)
                    NETPBTAXCAR, vaild = COMMON.TryParse(
                        'float', COMMON.col_clear(td_array[16]))
                    #純益率(%)
                    NETPR, vaild = COMMON.TryParse('float',
                                                  COMMON.col_clear(td_array[17]))
                    #每股盈餘(元)
                    EARNPER, vaild = COMMON.TryParse('float',
                                                    COMMON.col_clear(td_array[18]))
                    #現金流量比率(%)
                    CASHFR, vaild = COMMON.TryParse('float',
                                                    COMMON.col_clear(td_array[19]))
                    #現金流量允當比率(%)
                    ALLCASHFR, vaild = COMMON.TryParse('float',
                                                      COMMON.col_clear(td_array[20]))
                    #現金再投資比率(%)
                    CASHREINVR, vaild = COMMON.TryParse('float',
                                                        COMMON.col_clear(td_array[21]))

                    #判斷是否有該公司當年度資料，更新/新增
                    index = (CODE, COMMON.year_RC2CE(year))
                    data = [
                        DEBT, LTFA, CURR, QUIR, IPM, RECTURR, AVGCCD, INVTUR,
                        AVGSALESD, RPETURR, TATUR, ROA, ROE, NETPBTAXCAR, NETPR, EARNPER,
                        CASHFR, ALLCASHFR, CASHREINVR
                    ]
                    stockpd = pd.DataFrame(
                        data=[data],
                        index=pd.MultiIndex.from_tuples([index]),
                        columns=[
                            '負債占資產比率', '長期資金佔不動產廠房及設備比率', '流動比率', '速動比率', '利息保障倍數',
                            '應收款項週轉率', '平均收現日數', '存貨週轉率', '平均銷貨日數', '不動產廠房及設備週轉率',
                            '總資產週轉率', '資產報酬率', '權益報酬率', '稅前純益佔實收資本比率', '純益率', '每股盈餘',
                            '現金流量比率', '現金流量允當比率', '現金再投資比率'
                        ])
                    dfcomprehensiveIncome = dfcomprehensiveIncome.append(stockpd)

    return dfcomprehensiveIncome


#爬10年資料並匯出csv
def getcomprehensiveIncome_crawl(fromN2Now):
    eyyy = datetime.datetime.today().year - 1911
    syyy = eyyy - fromN2Now

    StocksData = pd.DataFrame()
    for yyy in range(syyy, eyyy):
        try:
            StocksData = StocksData.append(
                crawl_comprehensiveIncome(yyy, COMMON.__LISTEDCODE__))
            StocksData = StocksData.append(
                crawl_comprehensiveIncome(yyy, COMMON.__OTCCODE__))
            StocksData = StocksData.append(
                crawl_comprehensiveIncome(yyy, COMMON.__EMERGINGSCODE__))
            StocksData = StocksData.append(
                crawl_comprehensiveIncome(yyy, COMMON.__PUBLICCODE__))
        except:
            print(f'{yyy}-NO DATA')

    path = os.path.abspath('./data/')
    StocksData.to_csv(f'{path}/comprehensiveIncome.csv', index_label=['公司代號', '所屬年度'])

#讀取股利資料
def getcomprehensiveIncome_data(reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/comprehensiveIncome.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(file, index_col=[0, 1])
        return StocksData
    else:
        #預設帶出近10年
        print('RELOAD comprehensiveIncome......')
        getcomprehensiveIncome_crawl(10)
        return getcomprehensiveIncome_data()
