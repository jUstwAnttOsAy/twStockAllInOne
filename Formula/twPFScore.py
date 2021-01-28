import pandas as pd
import os


def getPiotroskiFScore(dfComInfo, dfFinancialAnalysis, dfbalanceSheet, dfcomprehensiveIncome):
    thisYYYY = dfFinancialAnalysis.index.get_level_values(1)[-1]
    lastYYYY = thisYYYY-1
    data = []
    index = []
    for code in dfComInfo.index:
        try:
            #1.資產報酬率(ROA)>0
            thisROA = dfFinancialAnalysis.loc[(code, thisYYYY),'資產報酬率']
            score1 = 1 if thisROA > 0 else 0
            #2.今年的ROA>去年ROA
            lastROA = dfFinancialAnalysis.loc[(code, lastYYYY),'資產報酬率']
            score2 = 1 if thisROA>lastROA else 0
            #3.今年的營業現金流>0[現金流量比率x流動負債]
            OperatingCashFlow = dfFinancialAnalysis.loc[(code, thisYYYY),'現金流量比率']*dfbalanceSheet.loc[(code, thisYYYY, 4), '流動負債']
            score3 = 1 if OperatingCashFlow>0 else 0
            #4.營業現金流>稅後淨利
            NetProfitAfterTax = dfcomprehensiveIncome.loc[(code, thisYYYY,),'稅後淨利'].sum()
            score4 = 1 if OperatingCashFlow>NetProfitAfterTax else 0
            #5.今年度的長期負債金額 < 上一年度
            thisNoncurrentLiabilities = dfbalanceSheet.loc[(code, thisYYYY, 4),'非流動負債']
            lastNoncurrentLiabilities = dfbalanceSheet.loc[(code, lastYYYY, 4),'非流動負債']
            score5 = 1 if thisNoncurrentLiabilities<lastNoncurrentLiabilities else 0
            #6.今年度的流動比率 > 上一年度
            thisCURR = dfFinancialAnalysis.loc[(code, thisYYYY),'流動比率']
            lastCURR = dfFinancialAnalysis.loc[(code, lastYYYY),'流動比率']
            score6 = 1 if thisCURR>lastCURR else 0
            #7.發行新股
            score7 = 0
            #8.今年度的毛利率 > 上一年度
            thisNetProfitRate = round(dfcomprehensiveIncome.loc[(code, thisYYYY,),'毛利'].sum()/dfcomprehensiveIncome.loc[(code, thisYYYY,),'營收'].sum(), 3)
            lastNetProfitRate = round(dfcomprehensiveIncome.loc[(code, lastYYYY,),'毛利'].sum()/dfcomprehensiveIncome.loc[(code, thisYYYY,),'營收'].sum(), 3)
            score8 = 1 if thisNetProfitRate>lastNetProfitRate else 0
            #9.今年度的資產週轉率 > 上一年度
            thisTATUR = dfFinancialAnalysis.loc[(code, thisYYYY),'總資產週轉率']
            lastTATUR = dfFinancialAnalysis.loc[(code, lastYYYY),'總資產週轉率']
            score9 = 1 if thisTATUR>lastTATUR else 0

            score = score1+score2+score3+score4+score5+score6+score7+score8+score9

            index.append((code, thisYYYY))
            data.append([dfComInfo.loc[code,'公司簡稱'],dfComInfo.loc[code,'產業類別'],thisROA, lastROA, OperatingCashFlow, NetProfitAfterTax, thisNoncurrentLiabilities, lastNoncurrentLiabilities, thisCURR, lastCURR, thisNetProfitRate, lastNetProfitRate, thisTATUR, lastTATUR, score])
        except:
            print(f'{code} no data in year {thisYYYY}')

    dfPFScore = pd.DataFrame(data = data, index = pd.MultiIndex.from_tuples(index), columns=['公司簡稱', '產業類別', '今年ROA', '去年ROA', '營業現金流','稅後淨利', '今年非流動負債','去年非流動負債','今年流動比率','去年流動比率','今年毛利率','去年毛利率','今年資產周轉率', '去年資產周轉率', '皮氏分數'])

    path = os.path.abspath('./result/')

    dfPFScore.to_csv(f'{path}/PiotroskiFScore_{thisYYYY}.csv', index_label=['公司代號', '年度'])

    return dfPFScore