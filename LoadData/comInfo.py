import Public.COMMON as COMMON
from datetime import datetime
import pandas as pd
import os

# https://mops.twse.com.tw/mops/web/t51sb01


# 載入公司資料
def crawl_comInfo(stocktype):
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
    data = []
    index = []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 17):
            # 公司代號, 公司名稱, 公司簡稱, 產業類別
            code = COMMON.col_clear(td_array[1])
            comName = COMMON.col_clear(td_array[2])
            comSName = COMMON.col_clear(td_array[3])
            comType = COMMON.col_clear(td_array[4])
            comCreateDate = datetime.strptime(
                COMMON.date_RC2CE(COMMON.col_clear(td_array[14])), '%Y/%m/%d')
            comOnDate = datetime.strptime(
                COMMON.date_RC2CE(COMMON.col_clear(td_array[15])), '%Y/%m/%d')
            comCapital = COMMON.col_clear(td_array[17])
            index.append(code)
            data.append([
                comName, comSName, comType, comCreateDate, comOnDate,
                comCapital
            ])

    dfComInfo = pd.DataFrame(
        data=data,
        index=index,
        columns=['公司名稱', '公司簡稱', '產業類別', '成立日期', '上市日期', '資本額'])

    return dfComInfo


# 取得公司資料並匯出csv
def get_Dividend_crawl():
    dfComInfo = pd.DataFrame()
    dfComInfo = dfComInfo.append(crawl_comInfo(COMMON.__LISTEDCODE__))
    dfComInfo = dfComInfo.append(crawl_comInfo(COMMON.__OTCCODE__))
    dfComInfo = dfComInfo.append(crawl_comInfo(COMMON.__EMERGINGSCODE__))
    dfComInfo = dfComInfo.append(crawl_comInfo(COMMON.__PUBLICCODE__))

    path = os.path.abspath('./data/')
    dfComInfo.to_csv(f'{path}/comInfo.csv', index_label=['公司代號'])
    COMMON.UpdateDataRecord('comInfo')


def get_ComInfo_data(reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/comInfo.csv'
    if reload != True and os.path.exists(file):
        dfComInfo = pd.read_csv(file, dtype={'公司代號':str})
        dfComInfo = dfComInfo.set_index('公司代號')
        return dfComInfo
    else:
        print('RELOAD ComInfo......')
        get_Dividend_crawl()
        return get_ComInfo_data()
