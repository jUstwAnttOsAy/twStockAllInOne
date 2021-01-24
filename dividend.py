import COMMON
import pandas as pd
import datetime

# https://mops.twse.com.tw/server-java/t05st09sub

# 載入股利資料


def crawl_dividend(year, stocktype):
    url = 'https://mops.twse.com.tw/server-java/t05st09sub'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'TYPEK': stocktype,
        'YEAR': COMMON.date_CE2RC(year),
        'first': '',
        'qryType': 1,
    }

    # 拆解內容
    table_array = COMMON.crawl_data2text(
        url, form_data, 'big5').split('<table')

    dfdividend = pd.DataFrame()

    for table in table_array:
        if '公司代號' in table:
            tr_array = table.split('<tr')
            for tr in tr_array:
                td_array = tr.split('<td')
                if len(td_array) > 15:
                    code = ''
                    belongY = 0
                    data = []
                    isNew = True
                    for tdIndex in range(len(td_array)):
                        val = COMMON.col_clear(td_array[tdIndex])
                        if tdIndex == 1:  # 公司代號
                            code = val.split('-')[0].strip()
                        # 所屬年度
                        elif tdIndex == 3:
                            ival, vaild = COMMON.TryParse(
                                'int', val.split('年')[0])
                            if vaild:
                                belongY = COMMON.date_RC2CE(ival)
                                index = (code, belongY)
                                if len(dfdividend.index) > 0 and index in dfdividend.index:
                                    data = dfdividend.loc[index]
                                    isNew = False
                        # 現金股利
                        elif tdIndex == 12:
                            earnM, vaild = COMMON.TryParse('float', val)
                            if len(data) > 0:
                                data[0] = data[0]+(earnM if vaild else 0)
                            else:
                                data.append(earnM if vaild else 0)
                        # 股票股利
                        elif tdIndex == 15:
                            earnS, vaild = COMMON.TryParse('float', val)
                            if len(data) > 1:
                                data[1] = data[1]+(earnS if vaild else 0)
                            else:
                                data.append(earnS if vaild else 0)

                    if isNew:
                        stockpd = pd.DataFrame(
                            data=[data], index=pd.MultiIndex.from_tuples([(code, belongY)]), columns=['現金股利', '股票股利'])
                        dfdividend = dfdividend.append(stockpd)
    return dfdividend


eyyy = datetime.datetime.today().year-1911
syyy = eyyy-10

StocksData = pd.DataFrame()
for yyy in range(syyy, eyyy):
    StocksData = StocksData.append(crawl_dividend(yyy, COMMON.__LISTEDCODE__))
    StocksData = StocksData.append(crawl_dividend(yyy, COMMON.__OTCCODE__))
    StocksData = StocksData.append(
        crawl_dividend(yyy, COMMON.__EMERGINGSCODE__))
    StocksData = StocksData.append(crawl_dividend(yyy, COMMON.__PUBLICCODE__))

StocksData.to_csv(f'dividend_{syyy}_{eyyy}.csv')
