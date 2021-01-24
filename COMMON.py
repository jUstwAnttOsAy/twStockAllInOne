import requests

# 常數

__LISTEDCODE__ = 'sii'  # 上市代號
__OTCCODE__ = 'otc'  # 上櫃代號
__EMERGINGSCODE__ = 'rotc'  # 興櫃代號
__PUBLICCODE__ = 'pub'  # 公開發行代號

# 轉換值


def TryParse(parseType, val):
    try:
        if parseType == 'int':
            nval = int(val)
        elif parseType == 'float':
            nval = float(val)
        else:
            raise ValueError('Parse Type not exists!')
        return nval, True
    except:
        return val, False


# 移除欄位中的雜訊


def col_clear(column):
    column = column.replace('&nbsp;', '').replace('\t', '').replace('<br>', '')
    remove_one = column.split('<')
    remove_two = remove_one[0].split('>')
    return remove_two[1].replace(",", "")

# 讀取url將頁面資料輸出


def crawl_data2text(url, formdata, encoding='utf-8'):
    response = requests.post(url, formdata)
    response.encoding = encoding

    return response.text

# 西元年轉民國年


def date_CE2RC(year):
    if year > 1911:
        year = year-1911
    else:
        print('The Year is already R.C.')

    return year

# 民國年轉西元年


def date_RC2CE(year):
    if year < 300:
        year = year+1911
    else:
        print('The Year is already C.E.')

    return year
