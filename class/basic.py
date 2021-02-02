class DQ: #股價資訊
    # 建構式
    def __init__(self, dtData):
        self.TVol = dtData['TVol'] #成交股數
        self.TXN = dtData['TXN'] #成交筆數
        self.TV = dtData['TV'] #成交金額
        self.OP = dtData['OP'] #開盤價
        self.HP = dtData['HP'] #最高價
        self.LP = dtData['LP'] #最低價
        self.CP = dtData['CP'] #收盤價
        self.Dir = dtData['Dir'] #漲跌(+/-)
        self.CHG = dtData['CHG'] #漲跌價差
        self.LBBP = dtData['LBBP'] #最後揭示買價
        self.LBBV = dtData['LBBV'] #最後揭示買量
        self.LBSP = dtData['LBSP'] #最後揭示賣價
        self.LBSV = dtData['LBSV'] #最後揭示賣量
        self.PER = dtData['PER'] #本益比

class REV:  #營收資訊
    # 建構式
    def __init__(self, dtData):
        self.TVol = dtData['TVol'] #成交股數
        self.TXN = dtData['TXN'] #成交筆數
        self.TV = dtData['TV'] #成交金額
        self.OP = dtData['OP'] #開盤價
        self.HP = dtData['HP'] #最高價
        self.LP = dtData['LP'] #最低價
        self.CP = dtData['CP'] #收盤價
        self.Dir = dtData['Dir'] #漲跌(+/-)
        self.CHG = dtData['CHG'] #漲跌價差
        self.LBBP = dtData['LBBP'] #最後揭示買價
        self.LBBV = dtData['LBBV'] #最後揭示買量
        self.LBSP = dtData['LBSP'] #最後揭示賣價
        self.LBSV = dtData['LBSV'] #最後揭示賣量
        self.PER = dtData['PER'] #本益比



class SCI:  #綜合損益表
    # 建構式
    def __init__(self, dtData):
class BS:  #資產負債表
    # 建構式
    def __init__(self, dtData):
class FSA:  #財務分析
    # 建構式
    def __init__(self, dtData):
class DIV:  #股利資訊
    # 建構式
    def __init__(self, dtData):