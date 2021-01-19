import requests
from io import StringIO
import pandas as pd

def crawl_price_date(date):
  datestr = str(date).split(' ')[0].replace('-','')
  # 下載股價
  r = requests.post(
      'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' +
      datestr + '&type=ALL')

  # 整理資料，變成表格
  df = pd.read_csv(
      StringIO(r.text.replace("=", "")),
      header=["證券代號" in l for l in r.text.split("\n")].index(True) - 1)

  # 整理一些字串：
  df = df.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").replace("+", "1").replace("-", "-1"), errors='ignore'))

  # 只顯示要看的資訊
  df = df[["證券代號","證券名稱","成交股數","成交筆數","成交金額", "收盤價"]]

  return df