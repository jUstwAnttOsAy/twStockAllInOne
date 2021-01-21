
# https://mops.twse.com.tw/mops/web/t51sb01
# 載入公司資料
def GetAllCompany():
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

    df = translate_dataFrame(response.text)


def translate_dataFrame(response):
    # 拆解內容
    table_array = response.split('<form action="/mops/web/ajax_t51sb01"')
    tr_array = table_array[1].split('<tr')

    # 拆解td
    data = []
    index = []
    for i in range(len(tr_array)):
        td_array = tr_array[i].split('<td')
        if (len(td_array) > 1):
            try:
                code = remove_td(td_array[1])
                name = remove_td(td_array[2])
                revenue = float(remove_td(td_array[3]))
                profitRatio = float(remove_td(td_array[4]))
                profitMargin = float(remove_td(td_array[5]))
                preTaxIncomeMargin = float(remove_td(td_array[6]))
                afterTaxIncomeMargin = float(remove_td(td_array[7]))

                data.append([
                    code, name, revenue, profitRatio, profitMargin,
                    preTaxIncomeMargin, afterTaxIncomeMargin,
                    profitRatio * revenue, profitMargin * revenue,
                    preTaxIncomeMargin * revenue,
                    afterTaxIncomeMargin * revenue
                ])
                index.append(code)
            except ValueError:
                continue
