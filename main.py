from services import stockInfo as info
from services import mongo as db, common
import pandas as pd
import arrow

db = db.MongoDB('twStockAllInOne', 'DQ')

#ComInfo = info.ComInfo()
#DQ = info.DQ()
#REV = info.REV()
#dfDQ = DQ.data
#comInfo = crawl.crawl_comInfo()
#db.InsertByDataFrame(comInfo)

#df = db.Find2DataFrame({})

'''
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
# 每日價格
print('Start Loading Price...')
dfPrice = price.get_price_data()
print('Price Loaded!')
#皮氏選股
print('Start Loading PiotroskiFScore')
dfPFScore = twPFScore.getPiotroskiFScore(dfComInfo, dfFinancialAnalysis, dfbalanceSheet, dfcomprehensiveIncome)
print('PiotroskiFScore Loaded!')
#價值選股
print('Start Loading ValueStockScore')
dfValueStockScore = twValueStockScore.getValueStockScore(dfComInfo, dfFinancialAnalysis, dfRevenue, dfcomprehensiveIncome, dfPrice, dfDividend, dfbalanceSheet)
print('ValueStockScore Loaded!')
'''