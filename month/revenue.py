import pandas as pd

#公司代號,資料年月,營業收入-上月比較增減(%),營業收入-去年同月增減(%),累計營業收入-前期比較增減(%)
def revneue_statement(stocktype, year, month):
    df = pd.read_csv(
        'https://mops.twse.com.tw/nas/t21/' + stocktype + '/t21sc03_' +
        str(year) + '_' + str(month) + '.csv',
        usecols=[
            '公司代號', '資料年月', '營業收入-上月比較增減(%)', '營業收入-去年同月增減(%)',
            '累計營業收入-前期比較增減(%)'
        ])

    return df


def revneue_statement_all(year, month):
    # 上市公司
    dfsii = revneue_statement('sii', year, month)
    # 上櫃公司
    dfotc = revneue_statement('otc', year, month)
    # 興櫃公司
    dfrotc = revneue_statement('rotc', year, month)
    # 公開發行公司
    dfpub = revneue_statement('pub', year, month)

    df = dfsii.append(dfotc)
    df = df.append(dfrotc)
    df = df.append(dfpub)

    return df
