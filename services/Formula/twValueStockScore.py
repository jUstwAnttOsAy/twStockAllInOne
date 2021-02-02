import Public.COMMON as COMMON
import datetime
import pandas as pd
import os

def getValueStockScore(dfComInfo, dfFinancialAnalysis, dfRevenue, dfcomprehensiveIncome, dfPrice, dfDividend, dfbalanceSheet):
    data = []
    index = []
    for code in dfComInfo.index:
        try:
            if code not in dfFinancialAnalysis.index.get_level_values(0):
                continue
            #今年, 去年
            thisYYYY = dfFinancialAnalysis.loc[(code,)].index.max()
            lastYYYY = thisYYYY-1
            #當月, 前月, 去年同月
            thisYYMM = dfRevenue.loc[(code,)].index.max()
            thisYY = int(thisYYMM/100)
            thisMM = int(thisYYMM%100)
            dlastYYMM, strlastYYMM = COMMON.minusMonth(datetime.datetime(thisYY, thisMM, 1),'%Y%m')
            lastYYMM, vaild = COMMON.TryParse('int',strlastYYMM)
            lastYAYYMM = (thisYY-1)*100+thisMM
            #當季, 上季, 去年同季
            arrthisSSNYYYY = dfcomprehensiveIncome.loc[(code,)].index.max()
            thisSSNYYYY, thisSSN = arrthisSSNYYYY
            lastSSNYYYY = thisSSNYYYY if thisSSN>1 else thisSSNYYYY-1
            lastSSN = thisSSN-1 if thisSSN>1 else 4
            lastYASSNYYYY = thisSSNYYYY-1
            lastYASSNMM = thisSSN
            #前日
            currDate = dfPrice.loc[(code,)].index.max()

            #1.月營收月增率>上月=5
            MonthMoM = dfRevenue.loc[(code, thisYYMM), '營業收入-上月比較增減(%)'].values[0]
            score1 = 5 if MonthMoM>0 else 0
            #2.月營收年增率>去年同期=5
            MonthYAYoY = dfRevenue.loc[(code, thisYYMM), '營業收入-去年同月增減(%)'].values[0]
            score2 = 5 if MonthYAYoY>0 else 0
            #3.累計營收年增率>去年同期=10
            CumYAYoY = dfRevenue.loc[(code, thisYYMM), '累計營業收入-前期比較增減(%)'].values[0]
            score3 = 10 if CumYAYoY>0 else 0
            #4.毛利率季增率>上季=5
            GrossMarginQoQ = (dfcomprehensiveIncome.loc[(code, thisSSNYYYY, thisSSN)]['毛利']/dfcomprehensiveIncome.loc[(code, lastSSNYYYY, lastSSN)]['毛利'])-1
            score4 = 5 if GrossMarginQoQ>0 else 0
            #5.毛利率年增率>去年同季=5
            GrossMarginYoY = (dfcomprehensiveIncome.loc[(code, thisSSNYYYY, list(range(1, thisSSN+1)))]['毛利'].sum()/dfcomprehensiveIncome.loc[(code, lastSSNYYYY, list(range(1, lastYASSNMM+1)))]['毛利'].sum())-1
            score5 = 5 if GrossMarginYoY>0 else 0
            #6.營業利益季增率>上季=5
            OperatingProfitQoQ = (dfcomprehensiveIncome.loc[(code, thisSSNYYYY, thisSSN)]['營業利益']/dfcomprehensiveIncome.loc[(code, lastSSNYYYY, lastSSN)]['營業利益'])-1
            score6 = 5 if OperatingProfitQoQ>0 else 0
            #7.營業利益年增率>去年同季=5
            OperatingProfitYoY = (dfcomprehensiveIncome.loc[(code, thisSSNYYYY, list(range(1, thisSSN+1)))]['營業利益'].sum()/dfcomprehensiveIncome.loc[(code, lastSSNYYYY, list(range(1, lastYASSNMM+1)))]['營業利益'].sum())-1
            score7 = 5 if OperatingProfitYoY>0 else 0
            #8.5年營業活動現金流量>0=5
            ls5YCASHO = dfFinancialAnalysis.loc[(code, list(range(thisYYYY-4, thisYYYY+1))),'現金流量比率']*dfbalanceSheet.loc[(code, list(range(thisYYYY-4, thisYYYY+1)), 4)]['流動負債']
            score8 = 0 if False in list(ls5YCASHO>0) else 5
            #9.5年營業利益>0=5
            ls5YOCF = dfcomprehensiveIncome.loc[(code, list(range(thisYYYY-4, thisYYYY+1)), ),'營業利益'].groupby('所屬年度').sum()
            score9 = 0 if False in list(ls5YOCF>0) else 5
            #10.5年本期淨利>0=5
            ls5NetProfit = dfcomprehensiveIncome.loc[(code, list(range(thisYYYY-4, thisYYYY+1)), ),'稅前淨利'].groupby('所屬年度').sum()
            score10 = 0 if False in list(ls5NetProfit>0) else 5
            #11.5年現金股利>0=5
            ls5EarnM = dfDividend.loc[(code, list(range(thisYYYY-4, thisYYYY+1))), '現金股利']
            score11 = 0 if False in list(ls5EarnM>0) else 5
            #12.流動比率>100%=5
            CURR = dfFinancialAnalysis.loc[(code, thisYYYY),'流動比率']
            score12 =5 if CURR>100 else 0
            #13.負債比率<50%=5
            Debt2AssetsRatio = dfFinancialAnalysis.loc[(code, thisYYYY),'負債占資產比率']
            score13 =5 if Debt2AssetsRatio<50 else 0
            #14.本益比(越低)=15
            score14 = -1
            PEScore=[40, 30, 25, 20, 15, 12, 10]
            PE = dfPrice.loc[(code, currDate), '本益比']
            PER = [x<PE for x in PEScore]
            for i in range(len(PER)):
                if PER[i]:
                    score14 = i*2.5
                    break
            if score14<0:
                score14 = 15
            #15.股價淨值比(越低)=5
            score15 = -1
            PBScore=[8.5, 6, 4, 2.5, 1.5, 1]
            PB = dfPrice.loc[(code, currDate), '收盤價']/dfbalanceSheet.loc[(code, thisSSNYYYY, thisSSN), '每股參考淨值']
            PBR = [x<PB for x in PBScore]
            for i in range(len(PBR)):
                if PBR[i]:
                    score15 = i*2.5
                    break
            if score15 < 0:
                score15 = 5
            #16.現金股利殖利率(越高)=10
            score16 = -1
            DividendYieldScore = [0, 1, 2, 2.5, 3, 4, 5, 6, 8, 10]
            DividendYield = dfDividend.loc[(code, thisYYYY), '現金股利']/dfPrice.loc[(code, currDate), '收盤價']
            DividendYieldR = [x>DividendYield for x in DividendYieldScore]
            for i in range(len(DividendYieldR)):
                if DividendYieldR[i]:
                    score16 = (i-1)*2.5
                    break
            if score16<0:
                score16 = 10

            score = score1+score2+score3+score4+score5+score6+score7+score8+score9+score10+score11+score12+score13+score14+score15+score16

            index.append((code, thisYYYY))
            data.append([dfComInfo.loc[code,'公司簡稱'],dfComInfo.loc[code,'產業類別'],MonthMoM,MonthYAYoY, CumYAYoY, GrossMarginQoQ, GrossMarginYoY, OperatingProfitQoQ, OperatingProfitYoY, CURR, Debt2AssetsRatio, PE, PB, DividendYield, score])
        except:
            print(f'{code} no data in year {thisYYYY}')

    dfValueStockScore = pd.DataFrame(data = data, index = pd.MultiIndex.from_tuples(index), columns=['公司簡稱', '產業類別', '月營收月增率', '月營收年增率', '累計營收年增率', '毛利率季增率','毛利率年增率','營業利益季增率','營業利益年增率','流動比率','負債比率','本益比','股價淨值比', '現金股利殖利率','價值股分數'])

    path = os.path.abspath('./result/')
    strDate = datetime.date.today().strftime('%Y%m%d')
    dfValueStockScore.to_csv(f'{path}/TWValueStockScore__{strDate}.csv', index_label=['公司代號', '年度'])

    return dfValueStockScore