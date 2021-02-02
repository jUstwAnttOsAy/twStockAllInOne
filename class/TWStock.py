import basic

class Stock:
    # 建構式
    def __init__(self, ticker):
        #company info
        self.ticker = ticker  # 股票代號
        self.ComName = '' # 公司名稱
        self.Com = ''  # 公司簡稱
        self.IC = ''  # 產業類別
        self.ESTD = ''  # 成立日期
        self.LISTD = ''  # 上市日期
        self.AoC = ''  # 資本額
        
        #report
        self.DQ  #股價資訊
        self.REV  #營收資訊
        self.SCI  #綜合損益表
        self.BS  #資產負債表
        self.FSA  #財務分析
        self.DIV  #股利資訊

    # 方法(Method)

