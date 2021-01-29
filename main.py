import Public.COMMON as COMMON
import LoadData.comInfo as comInfo
import LoadData.dividend as dividend
import LoadData.revenue as revenue
import LoadData.financialAnalysis as financialAnalysis
import LoadData.comprehensiveIncome as comprehensiveIncome
import LoadData.balanceSheet as balanceSheet
import LoadData.price as price
import Formula.twPFScore as twPFScore
import Formula.twValueStockScore as twValueStockScore
import pandas as pd
import numpy as np
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
