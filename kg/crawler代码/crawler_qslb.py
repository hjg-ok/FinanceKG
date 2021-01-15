# -*- coding: utf-8 -*-
import requests
import json
from pyquery import PyQuery as pq

SAVE_PATH = '../data/quanshangliebiao_xsb.json'

# def print_dict(dt):
#     ss = json.dumps(dt).decode('unicode-escape')
#     print (ss)

def save_to_json(dt, path):
#     print (dt)
    with open(path, 'a', encoding='utf-8') as fw:
        json.dump(dt, fw, indent=4, ensure_ascii=False)
    
# 列表页
base_url = 'http://xinsanban.eastmoney.com/api/Organization/Broker/qslb?page={}&pagesize=10&sortType=INYINSHORTNAME&sortRule=1'
# 每个详情页格式：http://xinsanban.eastmoney.com/F10/430725.OC.html 后面的430725.oc可通过上面列表页返回数据获取
detail_url = 'http://xinsanban.eastmoney.com/Organization/BrokerInfo/'
detail_urls = []
codes = []
for page in range(1, 11):
    # 总共10页
    url = base_url.format(page)
    r = requests.get(url, headers={'Accept': 'application/json'})
    datas = json.loads(r.text)
    for data in datas['result']:
#         print (data)
        code = data['STR_BROKER_CODE'] # 代码
        codes.append(code)
        detail_urls.append(detail_url + code + '.html')

print ('num of urls:',len(detail_urls))
all_broker_info = {}
for i,ele_url in enumerate(detail_urls):
    print (i)
    # 爬取券商
    # 有些数据是异步加载的，打开chrome开发者工具->network->xhr 刷新页面可以看到加载连接
    r = requests.get(ele_url)
    code_id = codes[i]
    doc = pq(r.text, parser='html_fragments')
    broker_info = {}

    # 基本信息
    comp_jbxx = {}
    jbxx = doc('div.basicInfo')
    for ele_li in jbxx('.intoBottom.clearfix')('li').items():  # 表的一行
        key = ele_li('.left_span').text()[:-1]
        key_len = len(key)
        value = ele_li.text()[key_len+1:]
        comp_jbxx[key] = value
    str_gsjj = jbxx('.intoTop.clearfix').text()
    comp_jbxx["公司简介"] = str_gsjj
    # print(comp_jbxx)
    broker_info["基本信息"] = comp_jbxx

    # 重要指标
    comp_zyzb = {}
    zyzb = doc('.pannel.clearfix')
    for j, ele_li in enumerate(zyzb('li').items()):  # 表的一行
    #     print(ele_li)
        if j >= 6:
            break
        if(j % 3 == 0):
            continue
        tmp_dict = {}
        tmp_dict["具体数值"] = ele_li('.w100').text()
        tmp_dict["同比增长率(%)"] = ele_li('.w125').text()
        key = ele_li('.w120').text()
        comp_zyzb[key] = tmp_dict
    broker_info["重要指标"] = comp_zyzb

    # 成交统计(异步加载)
    comp_cjtj = {}
    cjtj_url = "http://xinsanban.eastmoney.com/api/Organization/BrokerInfo/ywtj?code={}".format(code_id)
    r = requests.get(cjtj_url, headers={'Accept': 'application/json'})
    data = json.loads(r.text)  # size = 1
    comp_cjtj["成交金额(万元)"] = {"买入":data['DEC_TVAL_SUM_BUY'], "卖出":data['DEC_TVAL_SUM_SELL']}
    comp_cjtj["占总量比(%)"] = {"买入":data['DEC_TVAL_SUM_BUY_RATE'], "卖出":data['DEC_TVAL_SUM_SELL_RATE']}
    comp_cjtj["成交数量(万股)"] = {"买入":data['DEC_TVOL_SUM_BUY'], "卖出":data['DEC_TVOL_SUM_SELL']}
    comp_cjtj["占总量比(%)"] = {"买入":data['DEC_TVOL_SUM_BUY_RATE'], "卖出":data['DEC_TVOL_SUM_SELL_RATE']}
    comp_cjtj["成交笔数"] = {"买入":data['INT_TRADE_COUNT_BUY'], "卖出":data['INT_TRADE_COUNT_SELL']}
    comp_cjtj["成交家数"] = {"买入":data['INT_SEC_COUNT_BUY'], "卖出":data['INT_SEC_COUNT_SELL']}
    broker_info["成交统计"] = comp_cjtj

    broker_name = comp_jbxx["公司名称"]
    all_broker_info[broker_name] = broker_info

save_to_json(all_broker_info, SAVE_PATH)
    