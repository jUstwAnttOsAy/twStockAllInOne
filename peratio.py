import requests
from io import StringIO
import pandas as pd

def crawl_peratio_date(date):
  datestr = str(date).split(' ')[0].replace('-','')
  # 下載股價
  r = requests.post(
      'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date='+datestr+'&selectType=ALL')

  # 整理資料，變成表格
  df = pd.read_csv(
      StringIO(r.text.replace("=", "")),
      skiprows=1)

  # 整理一些字串：
  df = df.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").replace("+", "1").replace("-", "-1"), errors='ignore'))

  df=df[['證券代號', '殖利率(%)', '本益比', '股價淨值比']]

  return df