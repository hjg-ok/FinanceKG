import pandas as pd
import json

SAVE_PATH = '../data/ganggu'

all_comp_info = {}
for i in range(1,110):  # 爬取全部179页数据
    url = 'http://s.askci.com/stock/h/?reportTime=2018-06-30&pageNum={}#QueryCondition'.format(i)
    tb = pd.read_html(url)[3] #经观察发现所需表格是网页中第4个表格，故为[3]
    codes = tb["股票代码"].values # Series -> numpy.ndarray
    tb.to_csv(SAVE_PATH + '1.csv', mode='a', encoding='utf_8_sig', header=1, index=0)
    for code in codes:
        if len(str(code)) < 6:
            sub_url = 'http://s.askci.com/stock/summary/%06d' % code
        else:
            sub_url = 'http://s.askci.com/stock/summary/{}'.format(code)
        sub_tb = pd.read_html(sub_url)[0]
        comp_dict = {}
        keys = sub_tb[0].values
#         print(type(keys))
        values = sub_tb[1].values
        for j,key in enumerate(keys):
            comp_dict[key[:-1]] = values[j] 
#         print(comp_dict)
        comp_name = comp_dict["公司名称"]
        all_comp_info[comp_name] = comp_dict
   
    print('第'+str(i)+'页抓取完成')         

with open(SAVE_PATH + '2.json', 'a', encoding='utf-8') as fw:
        json.dump(all_comp_info, fw, indent=4, ensure_ascii=False)    
        
    
    