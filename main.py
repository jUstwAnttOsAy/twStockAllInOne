import pandas as pd
import datetime
import time
from ldbydate import crawl_price_date
from peratio import crawl_peratio_date
from revenue import crawl_revenue_last

allow_max_errors_count = 5
erros_count = 0
has_data = False

# 抓最後一天資料(基本資料+營收)

# for Daily
date = datetime.datetime.now()
while has_data==False and erros_count<=allow_max_errors_count:
  try:
    print('daily:', date.strftime('%Y/%m/%d......'))
    pricedata = crawl_price_date(date)
    time.sleep(5)
    peratio = crawl_peratio_date(date)
    time.sleep(5)

    if pricedata.empty or peratio.empty:
      raise ValueError('no data')

    has_data = True
    print('Loaded!')
  except:
    print('failed!')
    date = date - datetime.timedelta(days=1)
    erros_count = erros_count+1

#for Month
erros_count = 0
has_data = False
while(has_data == False) and erros_count<=allow_max_errors_count:
  try:
    print('month:', date, '......')
    revenue = crawl_revenue_last(date)
    time.sleep(5)

    if revenue.empty:
      raise ValueError('no data')

    has_data = True
    print('Loaded!')
  except ValueError:
    print('failed!')
    date = datetime.datetime(date.year-(1 if date.month == 1 else 0),(12 if date.month == 1 else date.month-1), 1)
    erros_count = erros_count+1


if pricedata.empty==False and peratio.empty==False and revenue.empty==False:
  data=pd.merge(pricedata, peratio, how="left", on=["證券代號"])
  data=pd.merge(data, revenue, how="left", left_on='證券代號', right_on='公司代號')
  data.set_index("證券代號" , inplace=True)
else:
  print('no data to show(connection aborted?)')