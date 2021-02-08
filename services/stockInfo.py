import pandas as pd
import arrow
from services import mongo as db, common
from io import StringIO


class Basic:
    def __init__(self, col, indx=[]):
        self.__db = db.MongoDB('twStockAllInOne', col)
        self.__indx = indx

    def load(self, condx={}):
        df = self.__db.query(condx)
        if df.empty:
            self.update()
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


class ComInfo(Basic):
    def __init__(self):
        super().__init__('ComInfo', indx='Ticker')
        self.data = pd.DataFrame()
        self.load()

    def load(self):
        self.data = super().load()

    def crawl(self):
        df = pd.DataFrame()

        for code in common.__TICKERTYPECODE__.values():
            df = df.append(self.crawl_comInfo_type(code))

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def crawl_comInfo_type(self, stocktype):
        url = 'https://mops.twse.com.tw/mops/web/ajax_t51sb01'
        form_data = {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': 1,
            'TYPEK': stocktype,
            'code': '',
        }

        # 拆解內容
        table_array = common.crawl_data2text(url, form_data).split('<table')
        tr_array = table_array[2].split('<tr')

        # 拆解td
        data, index = [], []
        for i in range(len(tr_array)):
            td_array = tr_array[i].split('<td')
            if (len(td_array) > 17):
                # 公司代號, 公司名稱, 公司簡稱, 產業類別
                Ticker = common.col_clear(td_array[1])
                ComName = common.col_clear(td_array[2])
                Com = common.col_clear(td_array[3])
                IC = common.col_clear(td_array[4])
                ESTD = common.date_RC2CE(common.col_clear(td_array[14]))
                LISTD = common.date_RC2CE(common.col_clear(td_array[15]))
                AoC = common.col_clear(td_array[17])
                index.append(Ticker)
                data.append([ComName, Com, IC, ESTD, LISTD, AoC])

        dfComInfo = pd.DataFrame(
            data=data,
            index=index,
            columns=['ComName', 'Com', 'IC', 'ESTD', 'LISTD', 'AoC'])

        dfComInfo.index.set_names('Ticker', inplace=True)

        return dfComInfo


class DQ(Basic):
    def __init__(self, rgDays=10):
        super().__init__('DQ', indx=['Ticker', 'Date'])
        self.rgDays = rgDays
        self.data = pd.DataFrame()
        self.lsDate = []
        self.load()

    def load(self):
        #load last n days data from now
        dateLimit = arrow.now().shift(days=-self.rgDays).format('YYYYMMDD')
        query = {'Date': {'$gte': dateLimit}}
        self.data = super().load(query)
        self.lsDate = self.data.index.get_level_values(1).unique()
        if dateLimit not in self.lsDate:
            super().update(query)
            self.data = super().load(query)

    def crawl(self):
        weekend = [5, 6]
        df = self.data
        ddate = arrow.now()
        cnt = 0

        while cnt < self.rgDays:
            if ddate.weekday() not in weekend:
                intddate = int(ddate.format('YYYYMMDD'))
                cnt += 1
                if intddate not in self.lsDate:
                    try:
                        df = df.append(self.crawl_DQ(ddate))
                    except:
                        print(ddate.format('YYYY/MM/DD'), 'no DQ data')

            ddate = ddate.shift(days=-1)

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def crawl_DQ(self, date):
        strDate = date.format('YYYYMMDD')
        # 下載股價
        url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={strDate}&type=ALL'
        rText = common.crawl_data2text(url, '', 'big5', delay=3000).replace(
            '=', '').replace('\r', '')

        def asFloat(x):
            val = x.replace(',', '')
            fval, vaild = common.TryParse('float', val)
            return fval if vaild else val

        # 整理資料，變成表格
        df = pd.read_csv(StringIO(rText),
                         header=['證券代號' in l
                                 for l in rText.split("\n")].index(True) - 1,
                         index_col=False,
                         converters={
                             '成交股數': asFloat,
                             '成交筆數': asFloat,
                             '開盤價': asFloat,
                             '最高價': asFloat,
                             '最低價': asFloat,
                             '收盤價': asFloat,
                             '漲跌價差': asFloat,
                             '最後揭示買價': asFloat,
                             '最後揭示買量': asFloat,
                             '最後揭示賣價': asFloat,
                             '最後揭示賣量': asFloat
                         },
                         usecols=[
                             '證券代號', '成交股數', '成交筆數', '成交金額', '開盤價', '最高價',
                             '最低價', '收盤價', '漲跌(+/-)', '漲跌價差', '最後揭示買價',
                             '最後揭示買量', '最後揭示賣價', '最後揭示賣量', '本益比'
                         ])

        df.columns = [
            'Ticker', 'TVol', 'TXN', 'TV', 'OP', 'HP', 'LP', 'CP', 'Dir',
            'CHG', 'LBBP', 'LBBV', 'LBSP', 'LBSV', 'PER'
        ]
        df['Date'] = strDate
        df = df.set_index(['Ticker', 'Date'])

        return df.sort_index()


class REV(Basic):
    def __init__(self, rgYears=3):
        super().__init__('REV', indx=['Ticker', 'ym'])
        self.rgYears = rgYears
        self.lmDate = arrow.now().shift(years=-self.rgYears)
        self.data = pd.DataFrame()
        self.lsDate = []
        self.load()

    def load(self):
        #load last n days data from now
        ymlimit = int(self.lmDate.format('YYYYMM'))
        query = {'ym': {'$gte': ymlimit}}
        self.data = super().load(query)
        self.lsDate = self.data.index.get_level_values(1).unique()
        if ymlimit not in self.lsDate:
            super().update(query)
            self.data = super().load(query)

    def crawl(self):
        df = self.data
        ddate = arrow.now()

        while self.lmDate < ddate:
            intddate = int(ddate.format('YYYYMM'))
            if intddate not in self.lsDate:
                for code in common.__TICKERTYPECODE__.values():
                    df = df.append(
                        self.crawl_REV_type(ddate.year, ddate.month, code))
            ddate = ddate.shift(months=-1)

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def crawl_REV_type(self, year, month, stocktype):
        df = pd.read_csv(
            f'https://mops.twse.com.tw/nas/t21/{stocktype}/t21sc03_{str(common.year_CE2RC(year))}_{str(month)}.csv',
            usecols=[
                '公司代號', '資料年月', '營業收入-當月營收', '營業收入-上月營收', '營業收入-去年當月營收',
                '營業收入-上月比較增減(%)', '營業收入-去年同月增減(%)', '累計營業收入-當月累計營收',
                '累計營業收入-去年累計營收', '累計營業收入-前期比較增減(%)'
            ],
            index_col=['公司代號', '資料年月'],
            converters={'資料年月': lambda x: year * 100 + month})

        df.columns = [
            'RevM', 'RevLM', 'RevLYM', 'RevMcLM', 'RevMcLYM', 'RevYCml',
            'RevLYCml', 'RevYCml2LYCml'
        ]

        df.index.set_names(['Ticker', 'ym'], inplace=True)

        return df


class SCI(Basic):
    def __init__(self, rgYears=5):
        super().__init__('SCI', indx=['Ticker', 'yr', 'qtr'])
        self.rgYears = rgYears
        self.lmDate = arrow.now().shift(years=-self.rgYears)
        self.data = pd.DataFrame()
        self.lsDate = []
        self.load()

    def load(self):
        #load last n days data from now
        yrlimit = int(self.lmDate.format('YYYY'))
        query = {'yr': {'$gte': yrlimit}}
        self.data = super().load(query)
        self.lsDate = self.data.index.get_level_values(1).unique()
        if yrlimit not in self.lsDate:
            super().update(query)
            self.data = super().load(query)

    def crawl(self):
        df = self.data
        yrNow = arrow.now().year
        yrLimit = yrNow - self.rgYears

        while yrNow >= yrLimit:
            if yrNow not in self.lsDate:
                for code in common.__TICKERTYPECODE__.values():
                    df = df.append(self.crawl_SCI_type(yrNow, 1, code)).append(
                        self.crawl_SCI_type(yrNow, 2, code)).append(
                            self.crawl_SCI_type(yrNow, 3, code)).append(
                                self.crawl_SCI_type(yrNow, 4, code))
            yrNow -= 1

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def crawl_SCI_type(self, year, season, stocktype):
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
        form_data = {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': 1,
            'TYPEK': stocktype,
            'code': '',
            'year': common.year_CE2RC(year),
            'season': season
        }

        # 拆解內容
        table_array = common.crawl_data2text(url, form_data).split('<table')
        dfcomprehensiveIncome = pd.DataFrame()

        dtTitle = {
            'Rev1': ['利息淨收益', '營業收入', '淨收益', '收益', '收入'],
            'Rev2': ['利息以外淨損益'],
            'GP': ['營業毛利（毛損）'],
            'OP': ['營業利益（損失）', '營業利益'],
            'NPBT':
            ['繼續營業單位稅前淨利（淨損）', '稅前淨利（淨損）', '繼續營業單位稅前損益', '繼續營業單位稅前純益（純損）'],
            'NPAT': ['本期稅後淨利（淨損）', '本期淨利（淨損）'],
            'NPPC': ['淨利（損）歸屬於母公司業主', '淨利（淨損）歸屬於母公司業主'],
            'EPS': ['基本每股盈餘（元）']
        }

        for table in table_array:
            if '代號</th>' in table:
                tr_array = table.split('<tr')
                dtIndex = {
                    'Rev1': -1,
                    'Rev2': -1,
                    'GP': -1,
                    'OP': -1,
                    'NPBT': -1,
                    'NPAT': -1,
                    'NPPC': -1,
                    'EPS': -1
                }

                for tr in tr_array:
                    if '<th' in tr:
                        th_array = tr.split('<th')
                        for thIndex in range(1, len(th_array)):
                            title = common.col_clear(th_array[thIndex]).strip()
                            for key in dtTitle.keys():
                                if title in dtTitle[key]:
                                    dtIndex[key] = thIndex
                        continue
                    td_array = tr.split('<td')
                    if len(td_array) > 1:
                        #公司代號, 年, 季
                        ticker = common.col_clear(td_array[1])
                        index = (ticker, common.year_RC2CE(year), season)
                        if index not in dfcomprehensiveIncome.index:
                            dtData = {
                                'Rev1': 0,
                                'Rev2': 0,
                                'GP': 0,
                                'OP': 0,
                                'NPBT': 0,
                                'NPAT': 0,
                                'NPPC': 0,
                                'EPS': 0
                            }

                            for key in dtIndex.keys():
                                if dtIndex[key] >= 0:
                                    val, vaild = common.TryParse(
                                        'float',
                                        common.col_clear(td_array[dtIndex[key]]))
                                    dtData[key] = val

                            data = [
                                dtData['Rev1'] + dtData['Rev2'], dtData['GP'],
                                dtData['OP'] if dtData['OP'] > 0 else
                                dtData['NPBT'], dtData['NPBT'], dtData['NPAT'],
                                dtData['NPPC'], dtData['EPS']
                            ]

                            df = pd.DataFrame(
                                data=[data],
                                index=pd.MultiIndex.from_tuples([index]),
                                columns=[
                                    'Rev', 'GP', 'OP', 'NPBT', 'NPAT', 'NPPC',
                                    'EPS'
                                ])

                            df['GM'] = df['GP'] / df['Rev']
                            df.index.set_names(['Ticker', 'yr', 'qtr'],
                                              inplace=True)
                            dfcomprehensiveIncome = dfcomprehensiveIncome.append(
                                df)

        return dfcomprehensiveIncome

class BS(Basic):
    def __init__(self, rgYears=5):
        super().__init__('BS', indx=['Ticker', 'yr', 'qtr'])
        self.rgYears = rgYears
        self.lmDate = arrow.now().shift(years=-self.rgYears)
        self.data = pd.DataFrame()
        self.lsDate = []
        self.load()

    def load(self):
        #load last n days data from now
        yrlimit = int(self.lmDate.format('YYYY'))
        query = {'yr': {'$gte': yrlimit}}
        self.data = super().load(query)
        self.lsDate = self.data.index.get_level_values(1).unique()
        if yrlimit not in self.lsDate:
            super().update(query)
            self.data = super().load(query)

    def crawl(self):
        df = self.data
        yrNow = arrow.now().year
        yrLimit = yrNow - self.rgYears

        while yrNow >= yrLimit:
            if yrNow not in self.lsDate:
                for code in common.__TICKERTYPECODE__.values():
                    df = df.append(self.crawl_BS_type(yrNow, 1, code)).append(
                        self.crawl_BS_type(yrNow, 2, code)).append(
                            self.crawl_BS_type(yrNow, 3, code)).append(
                                self.crawl_BS_type(yrNow, 4, code))

            yrNow -= 1

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def crawl_BS_type(self, year, season, stocktype):
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
        form_data = {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': 1,
            'off': 1,
            'isQuery': 'Y',
            'TYPEK': stocktype,
            'year': common.year_CE2RC(year),
            'season': season
        }

        # 拆解內容
        table_array = common.crawl_data2text(url, form_data).split('<table')
        dfBS = pd.DataFrame()

        dtTitle = {
            'TA': ['資產總額', '資產總計'],
            'TL': ['負債總計', '負債總額'],
            'TE': ['權益總計', '權益總額'],
            'RNP': ['每股參考淨值'],
            'CA': ['流動資產'],
            'NCA': ['非流動資產'],
            'CL': ['流動負債'],
            'NCL': ['非流動負債']
        }

        for table in table_array:
            if '代號</th>' in table:
                tr_array = table.split('<tr')
                dtIndex = {
                    'TA': -1,
                    'TL': -1,
                    'TE': -1,
                    'RNP': -1,
                    'CA': -1,
                    'NCA': -1,
                    'CL': -1,
                    'NCL': -1,
                }

                for tr in tr_array:
                    if '<th' in tr:
                        th_array = tr.split('<th')
                        for thIndex in range(1, len(th_array)):
                            title = common.col_clear(th_array[thIndex]).strip()
                            for key in dtTitle.keys():
                                if title in dtTitle[key]:
                                    dtIndex[key] = thIndex
                        continue
                    td_array = tr.split('<td')
                    if len(td_array)>1:
                        #公司代號, 年, 季
                        ticker = common.col_clear(td_array[1])
                        index = (ticker, common.year_RC2CE(year), season)

                        dtData = {
                            'TA': 0,
                            'TL': 0,
                            'TE': 0,
                            'RNP': 0,
                            'CA': 0,
                            'NCA': 0,
                            'CL': 0,
                            'NCL': 0,
                        }

                        for key in dtIndex.keys():
                            if dtIndex[key] >= 0:
                                val, vaild = common.TryParse(
                                    'float', common.col_clear(td_array[dtIndex[key]]))
                                dtData[key] = val

                        data = [
                            dtData['TA'], dtData['TL'], dtData['TE'], dtData['RNP'],
                            dtData['CA'], dtData['NCA'], dtData['CL'], dtData['NCL']
                        ]

                        df = pd.DataFrame(data=[data],
                                          index=pd.MultiIndex.from_tuples([index]),
                                          columns=[
                                              '資產總額', '負債總額', '權益總額', '每股參考淨值', '流動資產',
                                              '非流動資產', '流動負債', '非流動負債'
                                          ])

                        df.index.set_names(['Ticker', 'yr', 'qtr'], inplace=True)

                        dfBS = dfBS.append(df)

        return dfBS

class FSA(Basic):
    def __init__(self, rgYears=5):
        super().__init__('FSA', indx=['Ticker', 'yr'])
        self.rgYears = rgYears
        self.lmDate = arrow.now().shift(years=-self.rgYears)
        self.data = pd.DataFrame()
        self.lsDate = []
        self.load()

    def load(self):
        #load last n days data from now
        yrlimit = int(self.lmDate.format('YYYY'))
        query = {'yr': {'$gte': yrlimit}}
        self.data = super().load(query)
        self.lsDate = self.data.index.get_level_values(1).unique()
        if yrlimit not in self.lsDate:
            super().update(query)
            self.data = super().load(query)

    def crawl(self):
        df = self.data
        yrNow = arrow.now().year
        yrLimit = yrNow - self.rgYears

        while yrNow >= yrLimit:
            if yrNow not in self.lsDate:
                for code in common.__TICKERTYPECODE__.values():
                    df = df.append(self.crawl_FSA_type(yrNow, code))

            yrNow -= 1

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def crawl_FSA_type(self, year, stocktype):
        url = 'https://mops.twse.com.tw/mops/web/ajax_t51sb02'
        form_data = {
            'encodeURIComponent': 1,
            'run': 'Y',
            'step': 1,
            'TYPEK': stocktype,
            'year': common.year_CE2RC(year),
            'isnew': '',
            'firstin': 1,
            'off': 1,
            'ifrs': 'Y',
        }

        # 拆解內容
        table_array = common.crawl_data2text(url, form_data).split('<table')

        dfFSA = pd.DataFrame()
        if len(table_array) <3:
            return dfFSA

        tr_array = table_array[3].split('<tr')
        for tr in tr_array:
            td_array = tr.split('<td')
            if len(td_array) > 15:
                # 公司代號
                ticker = common.col_clear(td_array[1]).split('-')[0].strip()
                # 負債占資產比率
                DR, vaild = common.TryParse('float', common.col_clear(td_array[3]))
                # 長期資金佔不動產廠房及設備比率
                LER, vaild = common.TryParse('float',
                                            common.col_clear(td_array[4]))
                # 流動比率
                CR, vaild = common.TryParse('float', common.col_clear(td_array[5]))
                # 速動比率
                UR, vaild = common.TryParse('float', common.col_clear(td_array[6]))
                # 利息保障倍數
                IPM, vaild = common.TryParse('float',
                                            common.col_clear(td_array[7]))
                # 應收款項周轉率
                ARTR, vaild = common.TryParse('float',
                                              common.col_clear(td_array[8]))
                # 平均收現日數
                ACCD, vaild = common.TryParse('float',
                                              common.col_clear(td_array[9]))
                # 存貨週轉率(次)
                ITR, vaild = common.TryParse('float',
                                            common.col_clear(td_array[10]))
                # 平均銷貨日數
                ASD, vaild = common.TryParse('float',
                                            common.col_clear(td_array[11]))
                # 不動產廠房及設備週轉率(次)
                PETR, vaild = common.TryParse('float',
                                              common.col_clear(td_array[12]))
                # 總資產週轉率(次)
                TATR, vaild = common.TryParse('float',
                                              common.col_clear(td_array[13]))
                # 資產報酬率(%)
                ROA, vaild = common.TryParse('float',
                                            common.col_clear(td_array[14]))
                # 權益報酬率(%)
                ROE, vaild = common.TryParse('float',
                                            common.col_clear(td_array[15]))
                # 稅前純益佔實收資本比率(%)
                NPBT2PCR, vaild = common.TryParse('float',
                                                  common.col_clear(td_array[16]))
                # 純益率(%)
                NPR, vaild = common.TryParse('float',
                                            common.col_clear(td_array[17]))
                # 每股盈餘(元)
                EPS, vaild = common.TryParse('float',
                                            common.col_clear(td_array[18]))
                # 現金流量比率(%)
                CFR, vaild = common.TryParse('float',
                                            common.col_clear(td_array[19]))
                # 現金流量允當比率(%)
                CFAR, vaild = common.TryParse('float',
                                              common.col_clear(td_array[20]))
                # 現金再投資比率(%)
                CRR, vaild = common.TryParse('float',
                                            common.col_clear(td_array[21]))

                # 判斷是否有該公司當年度資料，更新/新增
                index = (ticker, common.year_RC2CE(year))
                data = [
                    DR, LER, CR, UR, IPM, ARTR, ACCD, ITR, ASD, PETR, TATR, ROA,
                    ROE, NPBT2PCR, NPR, EPS, CFR, CFAR, CRR
                ]
                df = pd.DataFrame(data=[data],
                                  index=pd.MultiIndex.from_tuples([index]),
                                  columns=[
                                      'DR', 'LER', 'CR', 'UR', 'IPM', 'ARTR',
                                      'ACCD', 'ITR', 'ASD', 'PETR', 'TATR', 'ROA',
                                      'ROE', 'NPBT2PCR', 'NPR', 'EPS', 'CFR',
                                      'CFAR', 'CRR'
                                  ])

                df.index.set_names(['Ticker', 'yr'], inplace=True)

                dfFSA = dfFSA.append(df)

        return dfFSA

class DIV(Basic):
    def __init__(self, rgYears=5):
        super().__init__('DIV', indx=['Ticker', 'yr'])
        self.rgYears = rgYears
        self.lmDate = arrow.now().shift(years=-self.rgYears)
        self.data = pd.DataFrame()
        self.lsDate = []
        self.load()

    def load(self):
        #load last n days data from now
        yrlimit = int(self.lmDate.format('YYYY'))
        query = {'yr': {'$gte': yrlimit}}
        self.data = super().load(query)
        self.lsDate = self.data.index.get_level_values(1).unique()
        if yrlimit not in self.lsDate:
            super().update(query)
            self.data = super().load(query)

    def crawl(self):
        df = self.data
        yrNow = arrow.now().year
        yrLimit = yrNow - self.rgYears

        while yrNow >= yrLimit:
            if yrNow not in self.lsDate:
                for code in common.__TICKERTYPECODE__.values():
                    df = df.append(self.crawl_DIV_type(yrNow, code)).append(self.crawl_DIV_TDR_type(yrNow, code))

            yrNow -= 1

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def crawl_DIV_type(self, year, stocktype):
        url = 'https://mops.twse.com.tw/server-java/t05st09sub'
        form_data = {
            'encodeURIComponent': 1,
            'step': 1,
            'TYPEK': stocktype,
            'YEAR': common.year_CE2RC(year),
            'first': '',
            'qryType': 2,
        }

        # 拆解內容
        table_array = common.crawl_data2text(url, form_data,
                                            'big5').split('<table')

        dfDIV = pd.DataFrame()

        for table in table_array:
            if '公司代號' in table:
                tr_array = table.split('<tr')
                for tr in tr_array:
                    td_array = tr.split('<td')
                    if len(td_array) > 15:
                        # 公司代號
                        ticker = common.col_clear(
                            td_array[1]).split('-')[0].strip()
                        # 所屬年度
                        intyr, vaild = common.TryParse(
                            'int',
                            common.col_clear(td_array[3]).split('年')[0])
                        yr = common.year_RC2CE(intyr)
                        # 現金股利
                        CD, vaild = common.TryParse('float',
                                                    common.col_clear(td_array[12]))
                        # 股票股利
                        SD, vaild = common.TryParse('float',
                                                    common.col_clear(td_array[15]))
                        # 判斷是否有該公司當年度資料，更新/新增
                        index = (ticker, yr)

                        if len(dfDIV.index) > 0 and index in dfDIV.index:
                            data = dfDIV.loc[index]
                            data[0] = data[0] + CD
                            data[1] = data[1] + SD
                        else:
                            df = pd.DataFrame(data=[[CD, SD]],
                                            index=pd.MultiIndex.from_tuples(
                                                [index]),
                                            columns=['CD', 'SD'])
                            df.index.set_names(['Ticker', 'yr'], inplace=True)

                            dfDIV = dfDIV.append(df)

        return dfDIV


    def crawl_DIV_TDR_type(self, year, stocktype):
        url = 'https://mops.twse.com.tw/mops/web/ajax_t66sb23'
        form_data = {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': '1',
            'Off': '1',
            'TYPEK': stocktype,
            'YEAR': common.year_CE2RC(year)
        }

        # 拆解內容
        table_array = common.crawl_data2text(url, form_data,
                                            'big5').split('<table')

        dfDIVTDR = pd.DataFrame()

        for table in table_array:
            if '公司代號' in table:
                tr_array = table.split('<tr')
                for tr in tr_array:
                    td_array = tr.split('<td')
                    if len(td_array) > 15:
                        # 公司代號
                        ticker = common.col_clear(
                            td_array[1]).split('-')[0].strip()
                        # 所屬年度
                        yr = common.year_RC2CE(year)
                        # 現金股利
                        CD, vaild = common.TryParse('float',
                                                    common.col_clear(td_array[11]))
                        # 股票股利
                        SD, vaild = common.TryParse('float',
                                                    common.col_clear(td_array[13]))
                        # 判斷是否有該公司當年度資料，更新/新增
                        index = (ticker, yr)

                        if len(dfDIVTDR.index) > 0 and index in dfDIVTDR.index:
                            data = dfDIVTDR.loc[index]
                            data[0] = data[0] + CD
                            data[1] = data[1] + SD
                        else:
                            df = pd.DataFrame(data=[[CD, SD]],
                                            index=pd.MultiIndex.from_tuples(
                                                [index]),
                                            columns=['CD', 'SD'])
                            df.index.set_names(['Ticker', 'yr'], inplace=True)

                            dfDIVTDR = dfDIVTDR.append(df)

        return dfDIVTDR