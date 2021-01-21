import requests
import pandas as pd


def getPiotroskiFScore(year, code):
    df = loadDataAll(code, 'Y')
    fyear = str(year)
    lastyear = str(year - 1)
    if fyear in df.index and lastyear in df.index:
        return getFScore(df.loc[fyear], df.loc[lastyear])
    else:
        print(f'Out of Range({str(year-1)}-{str(year)})')


def getPiotroskiFScoreByLastYear(code):
    df = loadDataAll(code, 'Y')
    fyear = df.index[0]
    lastyear = df.index[1]
    return getFScore(df.loc[fyear], df.loc[lastyear])


def getPiotroskiFScoreByLast4Q(code):
    df = loadDataAll(code, 'Q')
    Q1 = df.index[0]
    Q2 = df.index[1]
    Q3 = df.index[2]
    Q4 = df.index[3]
    lastQ1 = df.index[4]
    lastQ2 = df.index[5]
    lastQ3 = df.index[6]
    lastQ4 = df.index[7]
    totalScore = getFScore(df.loc[Q1], df.loc[lastQ1])+getFScore(df.loc[Q2], df.loc[lastQ2]) + \
        getFScore(df.loc[Q3], df.loc[lastQ3]) + \
        getFScore(df.loc[Q4], df.loc[lastQ4])

    return int(round(totalScore/4, 0))


def getFScore(lsthis, lslast):
    factor = []
    # 資產報酬率(ROA)>0
    factor.append(1 if lsthis['資產報酬率'] > 0 else 0)
    # 今年的ROA>去年ROA
    factor.append(
        1 if lsthis['資產報酬率'] > lslast['資產報酬率'] else 0)
    # 今年的營業現金流>0
    factor.append(1 if lsthis['營業現金流'] > 0 else 0)
    # 營業現金流>稅後淨利
    factor.append(
        1 if lsthis['營業現金流'] > lsthis['稅後淨利'] else 0)
    # 今年度的長期負債金額 < 上一年度
    factor.append(
        1 if lsthis['長期負債'] < lslast['長期負債'] else 0)
    # 今年度的流動比率 > 上一年度
    factor.append(
        1 if lsthis['流動比率'] > lslast['流動比率'] else 0)
    # 發行新股
    factor.append(1)
    # 今年度的毛利率 > 上一年度
    factor.append(
        1 if lsthis['毛利率'] > lslast['毛利率'] else 0)
    # 今年度的資產週轉率 > 上一年度
    factor.append(
        1 if lsthis['資產週轉率'] > lslast['資產週轉率'] else 0)
    return sum(factor)


def loadDataAll(code, base):
    dataFrames = [
        loadData1(code, base),
        loadData2(code, base),
        loadData3(code, base),
        loadData4(code, base)
    ]

    return pd.concat(dataFrames, axis=1)


def loadData1(code, base):
    url = f'https://concords.moneydj.com/z/zc/zcr/zcr0.djhtm?b={base}&a={code}'
    r = requests.get(url)
    keyword = ['期別', 'ROA(A)稅後息前', '流動比率', '營業毛利率', '總資產週轉次數']

    # 內容Table
    table_array = r.text.split('<table id="oMainTable"')
    tr_array = table_array[1].split('<tr')
    period = []
    ROA = []
    CurrentRatio = []
    GrossMargin = []
    AssetTurnover = []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 1):
            itemName = remove_td(td_array[1]).strip()
            if any(itemName in s for s in keyword) and (
                    (itemName == '期別' and len(period) == 0) or itemName != '期別'):
                for j in range(len(td_array)-2):
                    val = remove_td(td_array[j+2])
                    if itemName == '期別':
                        period.append(val)
                    else:
                        try:
                            val = float(val)
                            if itemName == 'ROA(A)稅後息前':
                                ROA.append(val)
                            elif itemName == '流動比率':
                                CurrentRatio.append(val)
                            elif itemName == '營業毛利率':
                                GrossMargin.append(val)
                            elif itemName == '總資產週轉次數':
                                AssetTurnover.append(val)
                        except:
                            continue
    # set to data
    data = []
    for i in range(len(period)):
        data.append(
            [ROA[i], CurrentRatio[i], GrossMargin[i], AssetTurnover[i]])

    return pd.DataFrame(
        data=data, index=period, columns=['資產報酬率', '流動比率', '毛利率', '資產週轉率'])


def loadData2(code, base):
    urlkey = 'j' if base == 'Y' else ''
    url = f'https://concords.moneydj.com/z/zc/zcd{urlkey}_{code}.djhtm'
    r = requests.get(url)

    # 內容Table
    table_array = r.text.split('<tr id="oScrollMenu"')
    tr_array = table_array[1].split('<tr')
    period = []
    NetProfitAfterTax = []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 1):
            try:
                val = remove_td(td_array[1]).split('.')
                # 轉成西元年
                yyyy = str(int(val[0]) + 1911)
                if len(val) > 1:
                    yyyy = yyyy + '.' + val[1]
                period.append(yyyy)
                NetProfitAfterTax.append(float(remove_td(td_array[5])))
            except:
                continue

    return pd.DataFrame(data=NetProfitAfterTax, index=period, columns=['稅後淨利'])


def loadData3(code, base):
    url = f'https://concords.moneydj.com/z/zc/zc30.djhtm?b={base}&a={code}'
    r = requests.get(url)

    # 內容Table
    table_array = r.text.split('<tr id="oScrollHead"')
    tr_array = table_array[1].split('<tr')
    period = []
    OperatingCashFlow = []
    for i in range(len(tr_array) - 1):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 1):
            itemName = remove_td(td_array[1]).strip()
            if itemName == '期別' or itemName == '期末現金及約當現金':
                for j in range(len(td_array)-2):
                    val = remove_td(td_array[j+2])
                    if itemName == '期別':
                        period.append(val)
                    else:
                        try:
                            val = float(val)
                            if itemName == '期末現金及約當現金':
                                OperatingCashFlow.append(val)
                        except:
                            continue
    return pd.DataFrame(
        data=OperatingCashFlow, index=period, columns=['營業現金流'])


def loadData4(code, base):
    url = f'https://concords.moneydj.com/z/zc/zcp/zcp.djhtm?a={code}&b=1&c={base}'
    r = requests.get(url)

    # 內容Table
    table_array = r.text.split('<tr id="oScrollHead"')
    tr_array = table_array[1].split('<tr')
    period = []
    LongTermLiabilities = []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 1):
            itemName = remove_td(td_array[1]).strip()
            if itemName == '期別' or itemName == '非流動負債':
                for j in range(len(td_array)-2):
                    val = remove_td(td_array[j+2])
                    if itemName == '期別':
                        period.append(val)
                    else:
                        try:
                            val = float(val)
                            if itemName == '非流動負債':
                                LongTermLiabilities.append(val)
                        except:
                            continue

    return pd.DataFrame(
        data=LongTermLiabilities, index=period, columns=['長期負債'])


def remove_td(column):
    remove_one = column.split('<')
    remove_two = remove_one[0].split('>')
    return remove_two[1].replace(",", "")


print(getPiotroskiFScoreByLast4Q('1101'))
