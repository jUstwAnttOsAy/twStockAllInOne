from services import common, stockInfo as info
import arrow
import pandas as pd

class PiotroskiFScore(common.Basic):
    def __init__(self, rgYears = 3):
        super().__init__('PiotroskiFScore', indx=['Ticker', 'yr'])
        self.ComInfo = info.ComInfo().data
        self.FSA = info.FSA().data
        self.BS = info.BS().data
        self.SCI = info.SCI().data
        
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
        ddate = arrow.now()

        while self.lmDate < ddate:
            inYR = int(ddate.format('YYYY'))
            if inYR not in self.lsDate:
                df = df.append(self.get_PiotroskiFScore(inYR))
            ddate = ddate.shift(years=-1)

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def get_PiotroskiFScore(self, yr):
        dfPFScore = pd.DataFrame()

        data = []
        index = []
        for code in self.ComInfo.index:
            try:
                thisYYYY = yr
                lastYYYY = yr-1

                #1.ROA(ROA)>0
                thisROA = self.FSA.loc[(code, thisYYYY),'ROA']
                score1 = 1 if thisROA > 0 else 0
                #2.今年的ROA>去年ROA
                lastROA = self.FSA.loc[(code, lastYYYY),'ROA']
                score2 = 1 if thisROA>lastROA else 0
                #3.今年的營業現金流>0[CFRxCL]
                OperatingCashFlow = self.FSA.loc[(code, thisYYYY),'CFR']*self.BS.loc[(code, thisYYYY, 4), 'CL']
                score3 = 1 if OperatingCashFlow>0 else 0
                #4.營業現金流>NPAT
                NetProfitAfterTax = self.SCI.loc[(code, thisYYYY,),'NPAT'].sum()
                score4 = 1 if OperatingCashFlow>NetProfitAfterTax else 0
                #5.今年度的長期負債金額 < 上一年度
                thisNoncurrentLiabilities = self.BS.loc[(code, thisYYYY, 4),'NCL']
                lastNoncurrentLiabilities = self.BS.loc[(code, lastYYYY, 4),'NCL']
                score5 = 1 if thisNoncurrentLiabilities<lastNoncurrentLiabilities else 0
                #6.今年度的CR > 上一年度
                thisCURR = self.FSA.loc[(code, thisYYYY),'CR']
                lastCURR = self.FSA.loc[(code, lastYYYY),'CR']
                score6 = 1 if thisCURR>lastCURR else 0
                #7.發行新股
                score7 = 0
                #8.今年度的毛利率 > 上一年度
                thisNetProfitRate = round(self.SCI.loc[(code, thisYYYY,),'GP'].sum()/self.SCI.loc[(code, thisYYYY,),'Rev'].sum(), 3)
                lastNetProfitRate = round(self.SCI.loc[(code, lastYYYY,),'GP'].sum()/self.SCI.loc[(code, thisYYYY,),'Rev'].sum(), 3)
                score8 = 1 if thisNetProfitRate>lastNetProfitRate else 0
                #9.今年度的資產週轉率 > 上一年度
                thisTATUR = self.FSA.loc[(code, thisYYYY),'TATR']
                lastTATUR = self.FSA.loc[(code, lastYYYY),'TATR']
                score9 = 1 if thisTATUR>lastTATUR else 0

                score = score1+score2+score3+score4+score5+score6+score7+score8+score9

                index.append((code, thisYYYY))
                data.append([self.ComInfo.loc[code,'Com'],self.ComInfo.loc[code,'IC'],thisROA, lastROA, OperatingCashFlow, NetProfitAfterTax, thisNoncurrentLiabilities, lastNoncurrentLiabilities, thisCURR, lastCURR, thisNetProfitRate, lastNetProfitRate, thisTATUR, lastTATUR, score])
            except:
                continue

        if len(data)>0:
            dfPFScore = pd.DataFrame(data = data, index = pd.MultiIndex.from_tuples(index), columns=['Com', 'IC', 'this_ROA', 'last_ROA', 'OCF','NPAT', 'this_NCL','last_NCL','this_CR','last_CR','this_GM','last_GM','this_TATR', 'last_TATR', 'PFScore'])

            dfPFScore.index.set_names(['Ticker', 'yr'], inplace=True)

        return dfPFScore

class TWValueScore(common.Basic):
    def __init__(self):
        super().__init__('TWValueScore', indx=['Ticker', 'Date'])
        self.ComInfo = info.ComInfo().data
        self.FSA = info.FSA().data
        self.BS = info.BS().data
        self.SCI = info.SCI().data
        self.REV = info.REV().data
        self.DQ = info.DQ().data
        self.DIV = info.DIV().data

        self.data = pd.DataFrame()
        self.load()

    def load(self, new = False):
        #load last n days data from now
        self.data = super().load()
        if new:
            qDate = self.DQ.index.get_level_values(1).max()
            self.lsDate = self.data.index.get_level_values(1).unique()
            if qDate not in self.lsDate:
                super().update()
                self.data = super().load()

    def crawl(self):
        df = self.data
        df = df.append(self.get_TWValueScore())

        return df.sort_index()

    def clear(self):
        super().clear()
        self.data = pd.DataFrame()

    def get_TWValueScore(self):
        dfValueStockScore = pd.DataFrame()
        data = []
        index = []
        for code in self.ComInfo.index:
            try:
                if code not in self.FSA.index.get_level_values(0):
                    continue
                #今年, 去年
                thisYYYY = self.FSA.loc[(code,)].index.max()
                lastYYYY = thisYYYY-1
                #當月, 前月, 去年同月
                thisYYMM = self.REV.loc[(code, )].index.max()
                thisYY = int(thisYYMM/100)
                thisMM = int(thisYYMM%100)
                strlastYYMM = arrow.get(thisYY, thisMM, 1).shift(months=-1).format('YYYYMM')
                lastYYMM, vaild = common.TryParse('int',strlastYYMM)
                lastYAYYMM = (thisYY-1)*100+thisMM
                #當季, 上季, 去年同季
                arrthisSSNYYYY = self.SCI.loc[(code,)].index.max()
                thisSSNYYYY, thisSSN = arrthisSSNYYYY
                lastSSNYYYY = thisSSNYYYY if thisSSN>1 else thisSSNYYYY-1
                lastSSN = thisSSN-1 if thisSSN>1 else 4
                lastYASSNYYYY = thisSSNYYYY-1
                lastYASSNMM = thisSSN
                #前日
                currDate = self.DQ.loc[(code,)].index.max()

                #1.月營收月增率>上月=5
                MonthMoM = self.REV.loc[(code, thisYYMM), 'RevMcLM'].values[0]
                score1 = 5 if MonthMoM>0 else 0
                #2.月營收年增率>去年同期=5
                MonthYAYoY = self.REV.loc[(code, thisYYMM), 'RevMcLYM'].values[0]
                score2 = 5 if MonthYAYoY>0 else 0
                #3.累計營收年增率>去年同期=10
                CumYAYoY = self.REV.loc[(code, thisYYMM), 'RevYCml2LYCml'].values[0]
                score3 = 10 if CumYAYoY>0 else 0
                #4.毛利率季增率>上季=5
                thisSSNGM = self.SCI.loc[(code, thisSSNYYYY, thisSSN)]['GM']
                lastSSNGM = self.SCI.loc[(code, lastSSNYYYY, lastSSN)]['GM']
                GrossMarginQoQ = 0 if lastSSNGM == 0 else (thisSSNGM/lastSSNGM)-1
                score4 = 5 if GrossMarginQoQ>0 else 0
                #5.毛利率年增率>去年同季=5
                thisYASSNGP = self.SCI.loc[(code, thisSSNYYYY, list(range(1, thisSSN+1)))]['GP'].sum()
                lastYASSNGP = self.SCI.loc[(code, lastYASSNYYYY, list(range(1, lastYASSNMM+1)))]['GP'].sum()
                GrossMarginYoY =0 if lastYASSNGP == 0 else (thisYASSNGP/lastYASSNGP)-1
                score5 = 5 if GrossMarginYoY>0 else 0
                #6.OP季增率>上季=5
                thisSSNOP = self.SCI.loc[(code, thisSSNYYYY, thisSSN)]['OP']
                lastSSNOP = self.SCI.loc[(code, lastSSNYYYY, lastSSN)]['OP']
                OperatingProfitQoQ = 0 if lastSSNOP == 0 else (thisSSNOP/lastSSNOP)-1
                score6 = 5 if OperatingProfitQoQ>0 else 0
                #7.OP年增率>去年同季=5
                thisYASSNOP = self.SCI.loc[(code, thisSSNYYYY, list(range(1, thisSSN+1)))]['OP'].sum()
                lastYASSNOP = self.SCI.loc[(code, lastYASSNYYYY, list(range(1, lastYASSNMM+1)))]['OP'].sum()
                OperatingProfitYoY = 0 if lastYASSNOP == 0 else (thisYASSNOP/lastYASSNOP)-1
                score7 = 5 if OperatingProfitYoY>0 else 0
                #8.5年營業活動現金流量>0=5
                ls5YCASHO = self.FSA.loc[(code, list(range(thisYYYY-4, thisYYYY+1))),'CFR']*self.BS.loc[(code, list(range(thisYYYY-4, thisYYYY+1)), 4)]['CL']
                score8 = 0 if False in list(ls5YCASHO>0) else 5
                #9.5年OP>0=5
                ls5YOCF = self.SCI.loc[(code, list(range(thisYYYY-4, thisYYYY+1)), ),'OP'].groupby('yr').sum()
                score9 = 0 if False in list(ls5YOCF>0) else 5
                #10.5年本期淨利>0=5
                ls5NetProfit = self.SCI.loc[(code, list(range(thisYYYY-4, thisYYYY+1)), ),'NPBT'].groupby('yr').sum()
                score10 = 0 if False in list(ls5NetProfit>0) else 5
                #11.5年CD>0=5
                ls5EarnM = self.DIV.loc[(code, list(range(thisYYYY-4, thisYYYY+1))), 'CD']
                score11 = 0 if False in list(ls5EarnM>0) else 5
                #12.CR>100%=5
                CURR = self.FSA.loc[(code, thisYYYY),'CR']
                score12 =5 if CURR>100 else 0
                #13.負債比率<50%=5
                Debt2AssetsRatio = self.FSA.loc[(code, thisYYYY),'DR']
                score13 =5 if Debt2AssetsRatio<50 else 0
                #14.PER(越低)=15
                score14 = -1
                PEScore=[40, 30, 25, 20, 15, 12, 10]
                try:
                    PE = float(self.DQ.loc[(code, currDate), 'PER'])
                    PER = [x<PE for x in PEScore]
                    for i in range(len(PER)):
                      if PER[i]:
                          score14 = i*2.5
                          break
                    if score14<0:
                      score14 = 15
                except:
                    PE = 0
                    score14 = 0
                #15.股價淨值比(越低)=5
                CP = float(self.DQ.loc[(code, currDate), 'CP'])
                CD = float(self.DIV.loc[(code, thisYYYY), 'CD'])
                RNper = float(self.BS.loc[(code, thisSSNYYYY, thisSSN), 'RNper'])

                score15 = -1
                PBScore=[8.5, 6, 4, 2.5, 1.5, 1]
                if RNper == 0:
                    PB = -1
                    score15 = 0
                else:
                    PB = CP/RNper
                    PBR = [x<PB for x in PBScore]
                    for i in range(len(PBR)):
                      if PBR[i]:
                          score15 = i*2.5
                          break
                    if score15 < 0:
                      score15 = 5
                #16.CD殖利率(越高)=10
                score16 = -1
                DividendYieldScore = [0, 1, 2, 2.5, 3, 4, 5, 6, 8, 10]
                DividendYield = 0 if CP == 0 else CD/CP
                DividendYieldR = [x>DividendYield for x in DividendYieldScore]
                for i in range(len(DividendYieldR)):
                  if DividendYieldR[i]:
                      score16 = (i-1)*2.5
                      break
                if score16<0:
                  score16 = 10

                score = score1+score2+score3+score4+score5+score6+score7+score8+score9+score10+score11+score12+score13+score14+score15+score16

                index.append([code, currDate])
                #當日, 當月, 當季, 當年
                data.append([thisYYMM, str(thisSSNYYYY)+'/'+str(thisSSN), thisYYYY,
                self.ComInfo.loc[code,'Com'],self.ComInfo.loc[code,'IC'],MonthMoM,MonthYAYoY, CumYAYoY, GrossMarginQoQ, GrossMarginYoY, OperatingProfitQoQ, OperatingProfitYoY, CURR, Debt2AssetsRatio, PE, PB, DividendYield, score])
            except:
                continue

        if len(data)>0:
            dfValueStockScore = pd.DataFrame(data = data, index = pd.MultiIndex.from_tuples(index), 
            columns=['thisYYMM', 'thisSSN', 'thisYYYY', 'Com', 'IC', 'MonthMoM', 'MonthYAYoY', 'CumYAYoY', 'GrossMarginQoQ','GrossMarginYoY','OperatingProfitQoQ','OperatingProfitYoY','CURR','Debt2AssetsRatio','PE','PB', 'DividendYield','TWValueScore'])

            dfValueStockScore.index.set_names(['Ticker', 'Date'], inplace=True)

        return dfValueStockScore