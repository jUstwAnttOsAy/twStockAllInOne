import requests
import pandas as pd
'''
1.{月增率}月營收月增率>上月=5
2.{年增率-1}月營收年增率>去年同期=5
3.{年增率-2}累計營收年增率>去年同期=10
[https://concords.moneydj.com/z/zc/zch/zch_1101.djhtm]

4.{營業毛利成長率}毛利率季增率>上季=5
5.{營業毛利成長率}毛利率年增率>去年同季=5
6.{營業利益成長率}營業利益季增率>上季=5
7.{營業利益成長率}營業利益年增率>去年同季=5
[https://concords.moneydj.com/z/zc/zcr/zcr0.djhtm?b=Q&a=1101]
[季=>季表, 年=>年表]

8.{每股現金流量}5年營業活動現金流量>0=5
9.{營業利益成長率}5年營業利益季增率>0=5
10.{每股稅前淨利}5年本期淨利>0=5
[https://concords.moneydj.com/z/zc/zcr/zcr0.djhtm?b=Q&a=1101]
11.{現金股利}5年現金股利>0=5
[https://concords.moneydj.com/z/zc/zca/zca_1101.djhtm]

12.{流動比率}流動比率>100%=5
13.{負債比率%}負債比率<50%=5
[https://concords.moneydj.com/z/zc/zcr/zcra/zcra_1101.djhtm]

14.{本益比}本益比(越低)=15
15.{股價淨值比}股價淨值比(越低)=5
16.{最新現金股利/收盤價}}現金股利殖利率(越高)=10
[https://concords.moneydj.com/z/zc/zca/zca_1101.djhtm]
'''


class Stock:
    # 建構式
    def __init__(self, code):
        self.code = code  # 股票代號
        self.monthly_revenue_growth_rate  #月營收月增率
        self.monthly_revenue_growth_rate  #月營收年增率
        self.cumulative_revenue_growth_rate  #累計營收年增率
        self.quarterly_growth_rate_of_gross_profit_margin  #毛利率季增率
        self.annual_growth_rate_of_gross_profit_margin  #毛利率年增率
        self.quarterly_growth_rate_of_operating_profit  #營業利益季增率
        self.annual_growth_rate_of_operating_profit  #營業利益年增率
        self.cash_flow_from_operating_activities  #營業活動現金流量
        self.net_profit_for_the_period  #本期淨利
        self.cash_dividend  #現金股利
        self.quarterly_return_on_assets  #季資產報酬率
        self.quarterly_operating_cash_flow  #季營業現金流
        self.quarterly_longterm_liabilities  #季長期負債
        self.quarterly_current_ratio  #季流動比率
        self.quarterly_quarterly_debt_ratio  #季負債比率
        self.quarterly_gross_margin  #季毛利率
        self.quarterly_asset_turnover  #季資產週轉率
        self.quarterly_pe_ratio  #季本益比
        self.quarterly_pricetonet_ratio  #季股價淨值比
        self.quarterly_cash_dividend_yield  #季現金股利殖利率
        self.annual_return_on_assets  #年資產報酬率
        self.annual_operating_cash_flow  #年營業現金流
        self.annual_longterm_liabilities  #年長期負債
        self.annual_current_ratio  #年流動比率
        self.annual_annual_debt_ratio  #年負債比率
        self.annual_gross_margin  #年毛利率
        self.annual_asset_turnover  #年資產週轉率
        self.annual_pe_ratio  #年本益比
        self.annual_pricetonet_ratio  #年股價淨值比
        self.annual_cash_dividend_yield  #年現金股利殖利率

    # 方法(Method)
    def remove_td(column):
        remove_one = column.split('<')
        remove_two = remove_one[0].split('>')
        return remove_two[1].replace(",", "")

    def getFScore(self, lsthis, lslast):
        factor = []
        # 資產報酬率(ROA)>0
        factor.append(1 if lsthis['資產報酬率'] > 0 else 0)
        # 今年的ROA>去年ROA
        factor.append(1 if lsthis['資產報酬率'] > lslast['資產報酬率'] else 0)
        # 今年的營業現金流>0
        factor.append(1 if lsthis['營業現金流'] > 0 else 0)
        # 營業現金流>稅後淨利
        factor.append(1 if lsthis['營業現金流'] > lsthis['稅後淨利'] else 0)
        # 今年度的長期負債金額 < 上一年度
        factor.append(1 if lsthis['長期負債'] < lslast['長期負債'] else 0)
        # 今年度的流動比率 > 上一年度
        factor.append(1 if lsthis['流動比率'] > lslast['流動比率'] else 0)
        # 發行新股
        factor.append(1)
        # 今年度的毛利率 > 上一年度
        factor.append(1 if lsthis['毛利率'] > lslast['毛利率'] else 0)
        # 今年度的資產週轉率 > 上一年度
        factor.append(1 if lsthis['資產週轉率'] > lslast['資產週轉率'] else 0)
        return sum(factor)

    def getPiotroskiFScore(self, year, code):
        df = self.loadDataAll(code, 'Y')
        fyear = str(year)
        lastyear = str(year - 1)
        if fyear in df.index and lastyear in df.index:
            return self.getFScore(df.loc[fyear], df.loc[lastyear])
        else:
            print(f'Out of Range({str(year-1)}-{str(year)})')

    def getPiotroskiFScoreByLastYear(self, code):
        df = self.loadDataAll(code, 'Y')
        fyear = df.index[0]
        lastyear = df.index[1]
        return self.getFScore(df.loc[fyear], df.loc[lastyear])

    def getPiotroskiFScoreByLast4Q(self, code):
        df = self.loadDataAll(code, 'Q')
        Q1 = df.index[0]
        Q2 = df.index[1]
        Q3 = df.index[2]
        Q4 = df.index[3]
        lastQ1 = df.index[4]
        lastQ2 = df.index[5]
        lastQ3 = df.index[6]
        lastQ4 = df.index[7]
        totalScore = self.getFScore(df.loc[Q1], df.loc[lastQ1])+self.getFScore(df.loc[Q2], df.loc[lastQ2]) + \
            self.getFScore(df.loc[Q3], df.loc[lastQ3]) + \
            self.getFScore(df.loc[Q4], df.loc[lastQ4])

        return int(round(totalScore / 4, 0))

    def loadDataAll(self, code, base):
        dataFrames = [
            self.loadData1(self, code, base),
            self.loadData2(self, code, base),
            self.loadData3(self, code, base),
            self.loadData4(self, code, base)
        ]

        return pd.concat(dataFrames, axis=1)

    def loadData1(self, code, base):
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
                itemName = self.remove_td(td_array[1]).strip()
                if any(itemName in s for s in keyword) and (
                    (itemName == '期別' and len(period) == 0)
                        or itemName != '期別'):
                    for j in range(len(td_array) - 2):
                        val = self.remove_td(td_array[j + 2])
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

    def loadData2(self, code, base):
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
                    val = self.remove_td(td_array[1]).split('.')
                    # 轉成西元年
                    yyyy = str(int(val[0]) + 1911)
                    if len(val) > 1:
                        yyyy = yyyy + '.' + val[1]
                    period.append(yyyy)
                    NetProfitAfterTax.append(
                        float(self.remove_td(td_array[5])))
                except:
                    continue

        return pd.DataFrame(
            data=NetProfitAfterTax, index=period, columns=['稅後淨利'])

    def loadData3(self, code, base):
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
                itemName = self.remove_td(td_array[1]).strip()
                if itemName == '期別' or itemName == '期末現金及約當現金':
                    for j in range(len(td_array) - 2):
                        val = self.remove_td(td_array[j + 2])
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

    def loadData4(self, code, base):
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
                itemName = self.remove_td(td_array[1]).strip()
                if itemName == '期別' or itemName == '非流動負債':
                    for j in range(len(td_array) - 2):
                        val = self.remove_td(td_array[j + 2])
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
