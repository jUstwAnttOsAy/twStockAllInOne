import pandas as pd
import requests

#公司代號,公司名稱,營業收入(百萬元),毛利率(%),營業利益率(%),稅前純益率(%),稅後純益率(%),營業毛利,營業利益,稅前純益,稅後純益
def remove_td(column):
    remove_one = column.split('<')
    remove_two = remove_one[0].split('>')
    return remove_two[1].replace(",", "")


def translate_dataFrame(response):
    # 拆解內容
    table_array = response.split('<table')
    tr_array = table_array[1].split('<tr')

    # 拆解td
    data = []
    index = []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 1):
            try:
                code = float(remove_td(td_array[1]))
                name = remove_td(td_array[2])
                revenue = float(remove_td(td_array[3]))
                profitRatio = float(remove_td(td_array[4]))
                profitMargin = float(remove_td(td_array[5]))
                preTaxIncomeMargin = float(remove_td(td_array[6]))
                afterTaxIncomeMargin = float(remove_td(td_array[7]))

                data.append([
                    code, name, revenue, profitRatio, profitMargin,
                    preTaxIncomeMargin, afterTaxIncomeMargin,
                    profitRatio * revenue, profitMargin * revenue,
                    preTaxIncomeMargin * revenue,
                    afterTaxIncomeMargin * revenue
                ])
                index.append(code)
            except ValueError:
                continue

    return pd.DataFrame(
        data=data,
        index=index,
        columns=[
            '公司代號', '公司名稱', '營業收入(百萬元)', '毛利率(%)', '營業利益率(%)', '稅前純益率(%)',
            '稅後純益率(%)', '營業毛利', '營業利益', '稅前純益', '稅後純益'
        ])


def financial_statement(stocktype, year, season):
    if year >= 1000:
        year -= 1911

    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'isQuery': 'Y',
        'TYPEK': stocktype,
        'year': year,
        'season': season,
    }

    response = requests.post(url, form_data)
    response.encoding = 'utf8'

    df = translate_dataFrame(response.text)
    return df


def financial_statement_all(year, season):
    dfsii = financial_statement('sii', year, season)
    dfotc = financial_statement('otc', year, season)
    dfrotc = financial_statement('rotc', year, season)
    dfpub = financial_statement('pub', year, season)

    df = dfsii.append(dfotc)
    df = df.append(dfrotc)
    df = df.append(dfpub)

    return df
