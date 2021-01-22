import requests
import pandas as pd

# https://mops.twse.com.tw/mops/web/t51sb01

def company_list_all():
    dfsii = company_list('sii')
    dfotc = company_list('otc')
    dfrotc = company_list('rotc')
    dfpub = company_list('pub')

    df = dfsii.append(dfotc)
    df = df.append(dfrotc)
    df = df.append(dfpub)

    return df

# 載入公司資料
def company_list(stocktype):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t51sb01'
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'TYPEK': stocktype,
        'code': '',
    }

    response = requests.post(url, form_data)
    response.encoding = 'utf8'

    # 拆解內容
    table_array = response.text.split('<table')
    tr_array = table_array[2].split('<tr')

    # 標題
    valindex = []
    titlelist = []
    keyword = ['公司代號','公司簡稱','產業類別']

    trtitle = tr_array[1].replace('<br>', '')
    td_array = trtitle.split('<th')
    for i in range(len(td_array)):
      title = remove_td(td_array[i])
      if title in keyword:
        titlelist.append(title)
        valindex.append(i)

    # 拆解td
    data = []
    temp = []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 1):
            temp = []
            for i in range(len(td_array)):
                if i in valindex:
                    temp.append(remove_td(td_array[i]))
            data.append(temp)

    df = pd.DataFrame(data=data, columns=titlelist)
    df = df.set_index('公司代號')

    return df

def remove_td(column):
    remove_one = column.replace('&nbsp;', '').split('<')
    remove_two = remove_one[0].split('>')
    return remove_two[1].replace(",", "")