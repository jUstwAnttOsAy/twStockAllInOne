import requests
from services import mongo as db
import pandas as pd
import arrow
import time
import os

# 常數

__TICKERTYPECODE__ = {
  'LISTED':'sii',# 上市代號
  'OTC':'otc',# 上櫃代號
  'EMERGINGS':'rotc',# 興櫃代號
  'PUBLIC':'pub',# 公開發行代號
}

__LISTEDCODE__ = 'sii'  # 上市代號
__OTCCODE__ = 'otc'  # 上櫃代號
__EMERGINGSCODE__ = 'rotc'  # 興櫃代號
__PUBLICCODE__ = 'pub'  # 公開發行代號

# 轉換值


def TryParse(parseType, val):
    defaultVal = val
    try:
        if parseType == 'int':
            defaultVal = 0
            nval = int(val)
        elif parseType == 'float':
            defaultVal = 0
            nval = float(val)
        else:
            raise ValueError('Parse Type not exists!')
        return nval, True
    except:
        return defaultVal, False


# 移除欄位中的雜訊


def col_clear(column):
    column = column.replace('&nbsp;', '').replace('\t', '').replace('<br>', '')
    remove_one = column.split('<')
    remove_two = remove_one[0].split('>')
    return remove_two[1].replace(",", "")

# 讀取url將頁面資料輸出


def crawl_data2text(url, formdata, encoding='utf-8', delay=500):
    response = requests.post(url, formdata)
    response.encoding = encoding
    result = response.text
    response.close()
    time.sleep(float(delay/1000))
    return result

# 西元年轉民國年


def year_CE2RC(year):
    if year > 1911:
        year = year-1911
    return year


def date_CE2RC(strdate):
    dateArray = strdate.split('/')
    if len(dateArray) > 1:
        intYear, vaild = TryParse('int', dateArray[0])
        if vaild:
            nstrdate = str(year_CE2RC(intYear))
            for i in range(1, len(dateArray)):
                nstrdate = nstrdate + f'/{dateArray[i]}'
            return nstrdate
    return strdate

# 民國年轉西元年


def year_RC2CE(year):
    if year < 300:
        year = year+1911
    return year


def date_RC2CE(strdate):
    dateArray = strdate.split('/')
    if len(dateArray) > 1:
        intYear, vaild = TryParse('int', dateArray[0])
        if vaild:
            nstrdate = str(year_RC2CE(intYear))
            for i in range(1, len(dateArray)):
                nstrdate = nstrdate + f'/{dateArray[i]}'
            return nstrdate
    return strdate

# 共通類別
class Basic:
    def __init__(self, col, indx=[]):
        self.__db = db.MongoDB('twStockAllInOne', col)
        self.__indx = indx

    def load(self, condx={}):
        df = self.__db.query(condx)
        if df.empty:
            if self.update(condx) == False:
                raise Exception('update FAILED')
            df = self.__db.query(condx)

        if len(self.__indx) > 0:
            df = df.set_index(self.__indx).sort_index()

        return df

    def update(self, query={}):
        if len(query) == 0:
            self.__db.drop()
        else:
            self.__db.remove(query)
        df = self.crawl()

        if df.empty:
            return False
        self.__db.insert(df)

        return True

    def clear(self):
        self.__db.drop()

    # 取得公司資料並匯出csv
    def crawl(self):
        raise ReferenceError('Need Method Overriding!')