from services import stockInfo as info, formula, analytics
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
KD = analytics.KD()
df = KD.load_Sig('2330', arrow.now())
print(df)
