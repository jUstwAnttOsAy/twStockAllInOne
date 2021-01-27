import Public.COMMON as COMMON
import pandas as pd
import datetime
import os

# https://mops.twse.com.tw/server-java/t05st09sub

# 爬蟲股利資料


def crawl_dividend(year, stocktype):
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

    dfdividend = pd.DataFrame()

    for table in table_array:
        if '公司代號' in table:
            tr_array = table.split('<tr')
            for tr in tr_array:
                td_array = tr.split('<td')
                if len(td_array) > 15:
                    #公司代號
                    code = COMMON.col_clear(td_array[1]).split('-')[0].strip()
                    #所屬年度
                    iBelongY, vaild = COMMON.TryParse('int',COMMON.col_clear(td_array[3]).split('年')[0])
                    belongY = COMMON.year_RC2CE(iBelongY)
                    # 現金股利
                    earnM, vaild = COMMON.TryParse('float', COMMON.col_clear(td_array[12]))
                    # 股票股利
                    earnS, vaild = COMMON.TryParse('float', COMMON.col_clear(td_array[15]))
                    #判斷是否有該公司當年度資料，更新/新增
                    index = (code, belongY)

                    if len(dfdividend.index) > 0 and index in dfdividend.index:
                        data = dfdividend.loc[index]
                        data[0] = data[0] + earnM
                        data[1] = data[1] + earnS
                    else:
                        data = [earnM, earnS]
                        stockpd = pd.DataFrame(
                            data=[data],
                            index=pd.MultiIndex.from_tuples([(code, belongY)]),
                            columns=['現金股利', '股票股利'])
                        dfdividend = dfdividend.append(stockpd)
                        
    return dfdividend

def crawl_dividendTDR(year, stocktype):
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

    dfdividendTDR = pd.DataFrame()

    for table in table_array:
        if '公司代號' in table:
            tr_array = table.split('<tr')
            for tr in tr_array:
                td_array = tr.split('<td')
                if len(td_array) > 15:
                    #公司代號
                    code = COMMON.col_clear(td_array[1]).split('-')[0].strip()
                    #所屬年度
                    belongY = COMMON.year_RC2CE(year)
                    # 現金股利
                    earnM, vaild = COMMON.TryParse('float', COMMON.col_clear(td_array[11]))
                    # 股票股利
                    earnS, vaild = COMMON.TryParse('float', COMMON.col_clear(td_array[13]))
                    #判斷是否有該公司當年度資料，更新/新增
                    index = (code, belongY)

                    if len(dfdividendTDR.index) > 0 and index in dfdividendTDR.index:
                        data = dfdividendTDR.loc[index]
                        data[0] = data[0] + earnM
                        data[1] = data[1] + earnS
                    else:
                        data = [earnM, earnS]
                        stockpd = pd.DataFrame(
                            data=[data],
                            index=pd.MultiIndex.from_tuples([(code, belongY)]),
                            columns=['現金股利', '股票股利'])
                        dfdividendTDR = dfdividendTDR.append(stockpd)
                        
    return dfdividendTDR


#爬10年資料並匯出csv
def get_Dividend_crawl(StocksData, fromN2Now):
    eyyyy = datetime.datetime.today().year
    syyyy = eyyyy - fromN2Now
    isUpd = False

    for yyyy in range(syyyy, eyyyy):
        if yyyy not in StocksData.index.get_level_values(1):
            try:
                StocksData = StocksData.append(
                    crawl_dividend(yyyy, COMMON.__LISTEDCODE__))
                StocksData = StocksData.append(crawl_dividend(yyyy, COMMON.__OTCCODE__))
                StocksData = StocksData.append(
                    crawl_dividend(yyyy, COMMON.__EMERGINGSCODE__))
                StocksData = StocksData.append(
                    crawl_dividend(yyyy, COMMON.__PUBLICCODE__))
                #for TDR
                StocksData = StocksData.append(
                    crawl_dividendTDR(yyyy, COMMON.__LISTEDCODE__))
                StocksData = StocksData.append(crawl_dividendTDR(yyyy, COMMON.__OTCCODE__))
                StocksData = StocksData.append(
                    crawl_dividendTDR(yyyy, COMMON.__EMERGINGSCODE__))
                StocksData = StocksData.append(
                    crawl_dividendTDR(yyyy, COMMON.__PUBLICCODE__))
                isUpd = True
            except:
                print(f'{yyyy}-NO DATA')

    if isUpd:
        path = os.path.abspath('./data/')
        StocksData.to_csv(f'{path}/dividend.csv', index_label=['公司代號', '所屬年度'])
        COMMON.UpdateDataRecord('dividend')


#讀取股利資料
def get_Dividend_data(n = 10, reload=False):
    path = os.path.abspath('./data/')
    file = f'{path}/dividend.csv'
    if reload != True and os.path.exists(file):
        StocksData = pd.read_csv(file, index_col=[0, 1], dtype={'公司代號':str})
        get_Dividend_crawl(StocksData, n)
        return StocksData
    else:
        #預設帶出近10年
        print('RELOAD DIVIDEND......')
        get_Dividend_crawl(pd.DataFrame(), n)
        return get_Dividend_data()
