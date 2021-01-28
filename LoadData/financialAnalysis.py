import Public.COMMON as COMMON
import pandas as pd
import datetime
import os


# 爬蟲財務分析資料
def crawl_financialAnalysis(year, stocktype):
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

    dffinancialAnalysis = pd.DataFrame()

    tr_array = table_array[3].split('<tr')
    for tr in tr_array:
        td_array = tr.split('<td')
        if len(td_array) > 15:
            # 公司代號
            CODE = COMMON.col_clear(td_array[1]).split('-')[0].strip()
            # 負債占資產比率
            DEBT, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[3]))
            # 長期資金佔不動產廠房及設備比率
            LTFA, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[4]))
            # 流動比率
            CURR, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[5]))
            # 速動比率
            QUIR, vaild = COMMON.TryParse('float',
                                          COMMON.col_clear(td_array[6]))
            # 利息保障倍數
            IPM, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[7]))
            # 應收款項周轉率
            RECTURR, vaild = COMMON.TryParse('float',
                                             COMMON.col_clear(td_array[8]))
            # 平均收現日數
            AVGCCD, vaild = COMMON.TryParse('float',
                                            COMMON.col_clear(td_array[9]))
            # 存貨週轉率(次)
            INVTUR, vaild = COMMON.TryParse('float',
                                            COMMON.col_clear(td_array[10]))
            # 平均銷貨日數
            AVGSALESD, vaild = COMMON.TryParse('float',
                                               COMMON.col_clear(td_array[11]))
            # 不動產廠房及設備週轉率(次)
            RPETURR, vaild = COMMON.TryParse('float',
                                             COMMON.col_clear(td_array[12]))
            # 總資產週轉率(次)
            TATUR, vaild = COMMON.TryParse('float',
                                           COMMON.col_clear(td_array[13]))
            # 資產報酬率(%)
            ROA, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[14]))
            # 權益報酬率(%)
            ROE, vaild = COMMON.TryParse('float',
                                         COMMON.col_clear(td_array[15]))
            # 稅前純益佔實收資本比率(%)
            NETPBTAXCAR, vaild = COMMON.TryParse(
                'float', COMMON.col_clear(td_array[16]))
            # 純益率(%)
            NETPR, vaild = COMMON.TryParse('float',
                                           COMMON.col_clear(td_array[17]))
            # 每股盈餘(元)
            EARNPER, vaild = COMMON.TryParse('float',
                                             COMMON.col_clear(td_array[18]))
            # 現金流量比率(%)
            CASHFR, vaild = COMMON.TryParse('float',
                                            COMMON.col_clear(td_array[19]))
            # 現金流量允當比率(%)
            ALLCASHFR, vaild = COMMON.TryParse('float',
                                               COMMON.col_clear(td_array[20]))
            # 現金再投資比率(%)
            CASHREINVR, vaild = COMMON.TryParse('float',
                                                COMMON.col_clear(td_array[21]))

            # 判斷是否有該公司當年度資料，更新/新增
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
            dffinancialAnalysis = dffinancialAnalysis.append(stockpd)

    return dffinancialAnalysis


# 爬10年資料並匯出csv
def get_FinancialAnalysis_crawl(StocksData, fromN2Now):
    eyyyy = datetime.datetime.today().year
    syyyy = eyyyy - fromN2Now
    oCnt = 0 if StocksData.empty else len(StocksData)

    for yyyy in range(syyyy, eyyyy):
        if StocksData.empty or yyyy not in StocksData.index.get_level_values(1):
            try:
                StocksData = StocksData.append(
                    crawl_financialAnalysis(yyyy, COMMON.__LISTEDCODE__))
                StocksData = StocksData.append(
                    crawl_financialAnalysis(yyyy, COMMON.__OTCCODE__))
                StocksData = StocksData.append(
                    crawl_financialAnalysis(yyyy, COMMON.__EMERGINGSCODE__))
                StocksData = StocksData.append(
                    crawl_financialAnalysis(yyyy, COMMON.__PUBLICCODE__))
            except:
                print(f'{yyyy}-NO DATA')

    if StocksData.empty!=True and len(StocksData) > oCnt:
        path = os.path.abspath('./data/')
        StocksData.sort_index().to_csv(f'{path}/financialAnalysis.csv',
                          index_label=['公司代號', '所屬年度'])
        COMMON.UpdateDataRecord('financialAnalysis')

# 讀取股利資料


def get_FinancialAnalysis_data(n=6, reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/financialAnalysis.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(file, dtype={'公司代號': str})
        StocksData = StocksData.set_index(['公司代號', '所屬年度'])
        lastUpdDate = COMMON.GetDataRecord('financialAnalysis')
        if len(lastUpdDate)==0 or datetime.datetime(lastUpdDate[0], lastUpdDate[1], lastUpdDate[2])<datetime.datetime.today():
            get_FinancialAnalysis_crawl(StocksData, n)
        return StocksData
    else:
        # 預設帶出近6年
        print('RELOAD FinancialAnalysis......')
        get_FinancialAnalysis_crawl(pd.DataFrame(), n)
        return get_FinancialAnalysis_data()
