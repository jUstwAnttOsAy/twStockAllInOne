import LoadData.comInfo as comInfo
import LoadData.dividend as dividend
import LoadData.revenue as revenue
import LoadData.financialAnalysis as financialAnalysis
import pandas as pd

#公司基本資料
dfComInfo = comInfo.getComInfo_data()
#公司股利資料
dfDividend = dividend.getDividend_data()
#公司營收資料
dfRevenue = revenue.getRevenue_data()
#財務分析資料
dfFinancialAnalysis = financialAnalysis.getFinancialAnalysis_data()
