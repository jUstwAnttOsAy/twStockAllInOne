import pandas as pd
from df2gspread import df2gspread as d2g
from df2gspread import gspread2df as g2d
from oauth2client.service_account import ServiceAccountCredentials as SAC
from basicCompany import company_list
from twPFScore import getPiotroskiFScoreByLastYear, getPiotroskiFScoreByLast4Q

def load2GSheet(df, sheetName):
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = SAC.from_json_keyfile_name("credentials.json", scopes)

    spreadsheet_key = '1HqhkjYDrTR8jgLIZ0GMJzYqGk4tRNd6hTWVlzfySccE'
    d2g.upload(df=df, gfile=spreadsheet_key, wks_name=sheetName, credentials=credentials, row_names=True)

def load2df(sheetName):
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = SAC.from_json_keyfile_name("credentials.json", scopes)
    spreadsheet_key = '1HqhkjYDrTR8jgLIZ0GMJzYqGk4tRNd6hTWVlzfySccE'
    df = g2d.download(gfile=spreadsheet_key, wks_name=sheetName, credentials=credentials)

    #設定第1欄 index, 第1列 column
    data = []
    column = []
    index = []

    for i in range(1, len(df.loc[0])):
      column.append(df.loc[0][i])
    
    for i in range(1, len(df.index)):
        tmpls = list(df.values[i])
        index.append(tmpls.pop(0))
        data.append(tmpls)

    return pd.DataFrame(data=data, columns=column, index=index)

def uploadStockInfoByType(stocktype, sheetName):
    print(f'----------------讀取{sheetName}----------------')
    #因線上編輯程式限制，每次僅執行50筆
    maxCnt = 200
    cnt = 0
    try:
        Odf = load2df(sheetName)
        if '皮氏分數-最近一年' not in Odf.columns:
          Odf['皮氏分數-最近一年'] = []
        if '皮氏分數-最近四季' not in Odf.columns:
          Odf['皮氏分數-最近四季'] = []
    except:
        Odf = pd.DataFrame()
        print(f'----------------建立{sheetName}----------------')

    Cdf = company_list(stocktype)
    for code in Cdf.index:
        try:
            if Odf.empty!=True and code in Odf.index:
                if Odf.loc[code]['皮氏分數-最近一年']=='':
                  Odf.loc[code]['皮氏分數-最近一年'] == getPiotroskiFScoreByLastYear(code)
                if Odf.loc[code]['皮氏分數-最近四季']=='':
                  Odf.loc[code]['皮氏分數-最近四季'] == getPiotroskiFScoreByLast4Q(code)
            else:
                name = Cdf.loc[code]['公司簡稱']
                slastYear = getPiotroskiFScoreByLastYear(code)
                slas4Q = getPiotroskiFScoreByLast4Q(code)
                ndf = pd.DataFrame(data=[[name, str(slastYear), str(slas4Q)]], columns=['公司簡稱', '皮氏分數-最近一年', '皮氏分數-最近四季'], index=[code])
                Odf = Odf.append(ndf)
                cnt = cnt+1
            if cnt>=maxCnt:
              break
        except:
            print(f'!!!讀取失敗【{code}-{name}】!!!')
    load2GSheet(Odf, sheetName)
    if cnt == maxCnt:
      print(f'-------------{sheetName}已寫入{cnt}筆--------------')
      return False
    else:
      print(f'----------------{sheetName}上傳完成----------------')
      return True

while uploadStockInfoByType('sii', '上市') == False:
    print(f'-------!!!上市未完成!!!，繼續執行--------')
while uploadStockInfoByType('otc', '上櫃') == False:
    print(f'-------!!!上櫃未完成!!!，繼續執行--------')
while uploadStockInfoByType('rotc', '興櫃') == False:
    print(f'-------!!!興櫃未完成!!!，繼續執行--------')
while uploadStockInfoByType('pub', '公開發行') == False:
    print(f'-------!!!公開未完成!!!，繼續執行--------')