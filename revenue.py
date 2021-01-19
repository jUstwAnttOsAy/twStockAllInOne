import pandas as pd

def crawl_revenue_last(date):
  year = date.year-1911
  month = date.month
  # 上市公司
  dfsii = pd.read_csv("https://mops.twse.com.tw/nas/t21/sii/t21sc03_"+str(year)+"_"+str(month)+".csv")
  # 上櫃公司
  dfotc = pd.read_csv("https://mops.twse.com.tw/nas/t21/otc/t21sc03_"+str(year)+"_"+str(month)+".csv")
  # 興櫃公司
  dfrotc = pd.read_csv("https://mops.twse.com.tw/nas/t21/rotc/t21sc03_"+str(year)+"_"+str(month)+".csv")
  # 公開發行公司
  dfpub = pd.read_csv("https://mops.twse.com.tw/nas/t21/pub/t21sc03_"+str(year)+"_"+str(month)+".csv")

  frames = [dfsii, dfotc, dfrotc, dfpub]
  df = pd.concat(frames)

  # 只顯示要看的資訊
  df = df[["公司代號","資料年月","營業收入-上月比較增減(%)","營業收入-去年同月增減(%)","累計營業收入-前期比較增減(%)"]]

  return df