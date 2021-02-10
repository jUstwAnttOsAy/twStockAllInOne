from services import stockInfo as info, formula
from services import mongo as db, common
import pandas as pd
import arrow
import numpy as np
from io import StringIO

#db = db.MongoDB('twStockAllInOne', 'DQ')
'''
ComInfo = info.ComInfo().data
REV = info.REV().data
DQ = info.DQ().data
SCI = info.SCI().data
BS = info.BS().data
FSA = info.FSA().data
DIV = info.DIV().data
'''
#get data
DQ = info.DQ(ticker = '2330', rgDays=90)
Close = DQ.data.loc['2330']['CP']
High = DQ.data.loc['2330']['HP']
Low = DQ.data.loc['2330']['LP']

#get RSV
ndate=len(DQ.data)
RSV=[]
for j in range(8,ndate):
    periodHigh=np.max(High[(j-8):(j+1)])
    periodLow=np.min(Low[(j-8):(j+1)])
    RSV.append(100*(Close[j]-periodLow)\
           /(periodHigh-periodLow))

RSV=pd.Series(RSV,index=Close.index[8:])
RSV.name='RSV'

K=[50]
D=[50]
for i in range(len(RSV)):
    KValue = (2/3)*K[-1] + (RSV[i]/3)
    DValue = (2/3)*D[-1] + KValue/3
    K.append(KValue)
    D.append(DValue)
K=pd.Series(K[1:],index=RSV.index)
K.name='KValue'
D=pd.Series(D[1:],index=RSV.index)
D.name='DValue'

'''
PiotroskiFScore = formula.PiotroskiFScore()
TWValueScore = formula.TWValueScore()
'''
'''
tw0050= pd.read_csv('0050.TW.csv',sep=',').dropna()
tw0050.index=pd.to_datetime(tw0050.Date, format='%Y-%m-%d')
tw0050=tw0050['2017']
Close = tw0050.Close
High = tw0050.High
Low = tw0050.Low

#RSV
ndate=len(Close)
RSV=[]
for j in range(8,ndate):
    periodHigh=np.max(High[(j-8):(j+1)])
    periodLow=np.min(Low[(j-8):(j+1)])
    RSV.append(100*(Close[j]-periodLow)\
           /(periodHigh-periodLow))

RSV=pd.Series(RSV,index=Close.index[8:])
RSV.name='RSV'

Close1=Close['2017']
RSV1=RSV['2017']
Cl_RSV=pd.DataFrame([Close1,RSV1]).transpose()

#KD
K=[50]
D=[50]
for i in range(len(RSV)):
    KValue = (2/3)*K[-1] + (RSV[i]/3)
    DValue = (2/3)*D[-1] + KValue/3
    K.append(KValue)
    D.append(DValue)
K=pd.Series(K[1:],index=RSV.index)
K.name='KValue'
D=pd.Series(D[1:],index=RSV.index)
D.name='DValue'

def upbreak(Line,RefLine):
    signal=np.all([Line>RefLine,\
                   Line.shift(1)<RefLine.shift(1)],\
                   axis=0)
    return(pd.Series(signal[1:],\
                     index=Line.index[1:]))
def downbreak(Line,RefLine):
    signal=np.all([Line<RefLine,\                    Line.shift(1)>RefLine.shift(1)],\
                   axis=0)
    return(pd.Series(signal[1:],\
           index=Line.index[1:]))

KDupbreak=upbreak(K,D)*1
KDdownbreak=downbreak(K,D)*1

Close=Close['2017-01-14':]
difClose=Close.diff()

prctrend=2*(difClose[1:]>=0)-1

KDupSig=(KDupbreak[1:]==1)&(prctrend==1)
KDdownSig= (KDdownbreak[1:]==1)&(prctrend==-1) 

breakSig=KDupSig*1+KDdownSig*-1
breakSig.name='breakSig'
'''