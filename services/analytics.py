from services import common, stockInfo as info
import arrow
import pandas as pd
import numpy as np


class KD(common.Basic):
    def __init__(self, rsvDays=9, rgKD=1):
        super().__init__(col='KD', indx=['Ticker', 'Date'])
        self.ComInfo = info.ComInfo().data
        self.rsvDays, self.rgKD = rsvDays, rgKD
        self.lsClose, self.lsHigh, self.lsLow = [], [], []
        self.lmDate = arrow.now().shift(days=-(rsvDays*self.rgKD))
        self.data = pd.DataFrame()
        self.lsDate = []
        self.init_DQ()

    def init_DQ(self):
        DQ = info.DQ(rgDays=self.rsvDays*self.rgKD)
        self.lsClose = DQ.data['CP']
        self.lsHigh = DQ.data['HP']
        self.lsLow = DQ.data['LP']

    def load(self):
        # load last n days data from now
        datelimit = self.lmDate.format('YYYYMMDD')
        query = {'Date': {'$gte': datelimit}}
        self.data = super().load(query)
        self.lsDate = self.data.index.get_level_values(1).unique()
        if datelimit not in self.lsDate:
            self.init_DQ()
            super().update(query)
            self.data = super().load(query)

    def crawl(self):
        df = self.data
        now = arrow.now()

        while now >= datelimit:
            if now not in self.lsDate:
                for code in self.ComInfo.index:
                    df = df.append()

            now = now.shift(days=-1)

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def load_Sig(self, ticker, now):
        ndate = self.rsvDays*2
        edate = now.format('YYYYMMDD')
        Close = self.lsClose.loc[ticker][lambda x: x.index <= edate].tail(
            self.rsvDays*2)
        High = self.lsHigh.loc[ticker][lambda x: x.index <= edate].tail(
            self.rsvDays*2)
        Low = self.lsLow.loc[ticker][lambda x: x.index <=
                                     edate].tail(self.rsvDays*2)

        #(今日收盤價 - 最近九天的最低價)/(最近九天的最高價 - 最近九天最低價)
        RSV = []
        for j in range(self.rsvDays-1, ndate):
            print(j)
            periodHigh = np.max(High[(j-(self.rsvDays-1)):(j+1)])
            periodLow = np.min(Low[(j-(self.rsvDays-1)):(j+1)])
            RSV.append(100*(Close[j]-periodLow) / (periodHigh-periodLow))

        RSV = pd.Series(RSV, index=Close.index[(self.rsvDays-1):])

        K, D = [50], [50]

        for i in range(len(RSV)):
            KValue = (2/3)*K[-1] + (RSV[i]/3)
            DValue = (2/3)*D[-1] + KValue/3
            K.append(KValue)
            D.append(DValue)
        K = pd.Series(K[1:], index=RSV.index)
        K.name = 'K'
        D = pd.Series(D[1:], index=RSV.index)
        D.name = 'D'

        KDupbreak = self.upbreak(K, D)*1
        KDdownbreak = self.downbreak(K, D)*1

        Close = Close[self.lsClose.index.get_level_values(1).min():]
        difClose = Close.diff()

        prctrend = 2*(difClose[1:] >= 0)-1

        KDupSig = (KDupbreak[1:] == 1) & (prctrend == 1)
        KDdownSig = (KDdownbreak[1:] == 1) & (prctrend == -1)

        breakSig = KDupSig*1+KDdownSig*-1
        breakSig.name = 'breakSig'

        df = pd.concat([K, D, breakSig], axis=1)

        return df.sort_index()

    def upbreak(self, Line, RefLine):
        signal = np.all([Line > RefLine, Line.shift(1)
                         < RefLine.shift(1)], axis=0)
        return(pd.Series(signal[1:], index=Line.index[1:]))

    def downbreak(self, Line, RefLine):
        signal = np.all([Line < RefLine, Line.shift(1)
                         > RefLine.shift(1)], axis=0)
        return(pd.Series(signal[1:], index=Line.index[1:]))


'''

class MACD:

class bullStageCheck:
'''
