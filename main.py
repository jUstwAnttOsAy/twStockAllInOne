import Public.COMMON as COMMON
import LoadData.comInfo as comInfo
import LoadData.dividend as dividend
import LoadData.revenue as revenue
import LoadData.financialAnalysis as financialAnalysis
import LoadData.comprehensiveIncome as comprehensiveIncome
import LoadData.balanceSheet as balanceSheet
import LoadData.price as price
import Formula.twPFScore as twPFScore
import pandas as pd
import datetime

# 公司基本資料
print('Start Loading Company Info...')
dfComInfo = comInfo.get_ComInfo_data()
print('Company Info Loaded!')
# 公司股利資料
print('Start Loading Dividend...')
dfDividend = dividend.get_Dividend_data()
print('Dividend Loaded!')
# 公司營收資料
print('Start Loading Revenue...')
dfRevenue = revenue.get_Revenue_data()
print('Revenue Loaded!')
# 財務分析資料
print('Start Loading Financial Analysis...')
dfFinancialAnalysis = financialAnalysis.get_FinancialAnalysis_data()
print('Financial Analysis Loaded!')
# 綜合損益表
print('Start Loading Comprehensive Income...')
dfcomprehensiveIncome = comprehensiveIncome.get_comprehensiveIncome_data()
print('Comprehensive Income Loaded!')
# 資產負債表
print('Start Loading Balance Sheet...')
dfbalanceSheet = balanceSheet.get_balanceSheet_data()
print('Balance Sheet Loaded!')
'''
# 每日價格
print('Start Loading Price...')
dfPrice = price.get_price_data()
print('Price Loaded!')
#皮氏選股
print('Start Loading PiotroskiFScore')
dfPFScore = twPFScore.getPiotroskiFScore(dfComInfo, dfFinancialAnalysis, dfbalanceSheet, dfcomprehensiveIncome)
print('PiotroskiFScore Loaded!')
'''

#今年, 去年
thisYYYY = dfFinancialAnalysis.index.get_level_values(1).max()
lastYYYY = thisYYYY-1
#當月, 前月, 去年同月
thisYYMM = dfRevenue.index.get_level_values(1).max()
thisYY = int(thisYYMM/100)
thisMM = int(thisYYMM%100)
dlastYYMM, strlastYYMM = COMMON.minusMonth(datetime.datetime(thisYY, thisMM, 1),'%Y%m')
lastYYMM, vaild = COMMON.TryParse('int',strlastYYMM)
lastSYYMM = (thisYY-1)*100+thisMM
#當季, 上季, 去年同季
thisSeasonYYYY = dfcomprehensiveIncome.index.get_level_values(1).max()
thisSeasonMM = 4
hasSeason = False
while hasSeason !=True:
    try:
        dfcomprehensiveIncome.loc[(slice(None),thisSeasonYYYY,thisSeasonMM),].head()
        hasSeason = True
    except:
        thisSeasonMM -=1
lastSeasonYYYY = thisSeasonYYYY if thisSeasonMM>1 else thisSeasonYYYY-1
lastSeasonMM = thisSeasonMM-1 if thisSeasonMM>1 else 4
lastSSeasonYYYY = thisSeasonYYYY-1
lastSSeasonMM = thisSeasonMM

print('今年', thisYYYY)
print('去年', lastYYYY)
print('當月', thisYYMM)
print('前月', lastYYMM)
print('去年同月', lastSYYMM)
print('當季', thisSeasonYYYY, thisSeasonMM)
print('上季', lastSeasonYYYY, lastSeasonMM)
print('去年同季', lastSSeasonYYYY, lastSSeasonMM)

data = []
index = []
for code in dfComInfo.index:
    #1.月營收月增率>上月=5
    MonthMoM = dfRevenue.loc[(code, thisYYMM), '營業收入-上月比較增減(%)']
    score1 = 5 if MonthMoM>0 else 0
    #2.月營收年增率>去年同期=5
    MonthSYoY = dfRevenue.loc[(code, thisYYMM), '營業收入-去年同月增減(%)']
    score2 = 5 if MonthSYoY>0 else 0
    #3.累計營收年增率>去年同期=10
    CumYoY = dfRevenue.loc[(code, thisYYMM), '累計營業收入-前期比較增減(%)']
    score3 = 10 if CumYoY>0 else 0
    #4.毛利率季增率>上季=5
    NetProfitSeasonRate = dfcomprehensiveIncome.loc[(code, thisSeasonYYYY, thisSeasonMM)]['營收']
    #5.毛利率年增率>去年同季=5
    #6.營業利益季增率>上季=5
    #7.營業利益年增率>去年同季=5
    #8.5年營業活動現金流量>0=5
    #9.5年營業利益季增率>0=5
    #10.5年本期淨利>0=5
    #11.5年現金股利>0=5
    #12.流動比率>100%=5
    #13.負債比率<50%=5
    #14.本益比(越低)=15
    #15.股價淨值比(越低)=5
    #16.現金股利殖利率(越高)=10
'''