import LoadData.comInfo as comInfo
import LoadData.dividend as dividend
import LoadData.revenue as revenue
import LoadData.financialAnalysis as financialAnalysis
import LoadData.comprehensiveIncome as comprehensiveIncome
import LoadData.balanceSheet as balanceSheet
import pandas as pd

#公司基本資料
dfComInfo = comInfo.get_ComInfo_data()
#公司股利資料
dfDividend = dividend.get_Dividend_data()
#公司營收資料
dfRevenue = revenue.get_Revenue_data()
#財務分析資料
dfFinancialAnalysis = financialAnalysis.get_FinancialAnalysis_data()
#綜合損益表
dfcomprehensiveIncome = comprehensiveIncome.get_comprehensiveIncome_data()
#資產負債表
dfbalanceSheet = balanceSheet.get_balanceSheet_data()
