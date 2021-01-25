import requests
from io import StringIO
import pandas as pd

#公司代號,公司名稱,殖利率(%),本益比,股價淨值比,財報年/季
def peratio_date(date):
    # 下載股價
    r = requests.post(
        'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date=' +
        date.strftime('%Y%m%d') + '&selectType=ALL')

    # 整理資料，變成表格
    df = pd.read_csv(
        StringIO(r.text.replace("=", "")),
        skiprows=1,
        usecols=['證券代號', '證券名稱', '殖利率(%)', '本益比', '股價淨值比', '財報年/季'],
    )

    data = []
    dfindex = []
    for index, row in df.iterrows():
        try:
            code = float(row['證券代號'])
            if code>1:
              name = row['證券名稱']
              dividendyield = float(row['殖利率(%)'])
              peratio = float(row['本益比'])
              pbratio = float(row['股價淨值比'])
              fiscalys = row['財報年/季']
              data.append(
                  [code, name, dividendyield, peratio, pbratio, fiscalys])
              dfindex.append(code)
        except ValueError:
            continue

    return pd.DataFrame(
        data=data,
        index=dfindex,
        columns=['公司代號', '公司名稱', '殖利率(%)', '本益比', '股價淨值比', '財報年/季'])
