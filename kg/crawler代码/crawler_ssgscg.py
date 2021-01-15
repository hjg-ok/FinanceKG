# -*- coding: utf-8 -*-
import requests
import json
from pyquery import PyQuery as pq

SAVE_PATH = '../data/shangshigongsichigu_xsb.json'

# def print_dict(dt):
#     ss = json.dumps(dt).decode('unicode-escape')
#     print (ss)

def save_to_json(dt, path):
#     print (dt)
    with open(path, 'a', encoding='utf-8') as fw:
        json.dump(dt, fw, indent=4, ensure_ascii=False)
    
# 列表页
base_url = 'http://xinsanban.eastmoney.com/api/DataCenter/JGCG/GetSSGSCG?page={}&pagesize=20&sortType=INT_SEC&sortRule=-1&tdsourcetag=s_pcqq_aiomsg'
# 每个详情页格式：http://xinsanban.eastmoney.com/F10/430725.OC.html 后面的430725.oc可通过上面列表页返回数据获取
detail_url = 'http://xinsanban.eastmoney.com/F10/'
detail_urls = []
codes = []
for page in range(1, 30):
    # 总共29页，也可以通过r.text是否是空数据判断页面是否遍历结束
    url = base_url.format(page)
    r = requests.get(url, headers={'Accept': 'application/json'})
    datas = json.loads(r.text)
    for data in datas['result']:
#         print (data)
        code = data['MSECUCODE'] # 代码
        codes.append(code[:6])
        detail_urls.append(detail_url + code + '.html')

print ('num of urls:',len(detail_urls))
all_company_info = {}
for i,ele_url in enumerate(detail_urls):
    print (i)
    # 爬取单个公司
    # 有些数据如重要指标、十大股东、主管列表等异步加载的，打开chrome开发者工具->network->xhr 刷新页面可以看到加载连接
    r = requests.get(ele_url)
    code_id = codes[i]
    doc = pq(r.text, parser='html_fragments')
    company_info = {}
    
    ## 公司介绍
    gsjs_url = "http://xinsanban.eastmoney.com/F10/CompanyInfo/Introduction/{}.html".format(code_id)
    r = requests.get(gsjs_url)
    sub_doc = pq(r.text, parser='html_fragments')
    # 公司资料
    comp_gszl = {}
    gszl = sub_doc('div#company_info')
    for li in gszl('li').items():  # 表的一行
        for ele_li in li.items():
            key = ele_li('.company-page-item-left').text()
            value = ele_li('.company-page-item-right').text()
            comp_gszl[key] = value 
    company_info["公司资料"] = comp_gszl
    
    # 证券资料
    comp_zqzl = {}
    zqzl = sub_doc('div#security_info')
    for li in zqzl('li').items():  # 表的一行
        for ele_li in li.items():
            key = ele_li('.company-page-item-left').text()
            value = ele_li('.company-page-item-right').text()
            comp_zqzl[key] = value 
    company_info["证券资料"] = comp_zqzl
    
    # 财务政要
    key = ""
    comp_cwzy = {}
    cwzy = doc('div.cwzy')
    for tr in cwzy('tr').items():  # 表的一行
        for td in tr('td').items():
            if td('.tl'):
                key = td.text()
            else:
                comp_cwzy[key] = td.text()
    company_info["财务政要"] = comp_cwzy

    # 重要指标（异步加载）
    comp_zyzb = {}
    zyzb_url = "http://xinsanban.eastmoney.com/api/F10/HomeIndex/GetIndicator?code={}".format(code_id)
    r = requests.get(zyzb_url, headers={'Accept': 'application/json'})
    datas = json.loads(r.text)['result'] # list, size = 1
    for data in datas:
        comp_zyzb["总股本(万股)"] = data['ZGB']
        comp_zyzb["总市值(万元)"] = data['ZSZ']
        comp_zyzb["流通股本(万股)"] = data['LTG']
        comp_zyzb["流通市值(万元)"] = data['LTSZ']
        comp_zyzb["市盈率TTM"] = data['PETTM']
        comp_zyzb["市净率(MRQ)"] = data['PBMRQ']
        comp_zyzb["融资增发实施次数"] = data['ISSUETIMES']
        comp_zyzb["累计融资额(万元)"] = data['ISSUEAMT']
        comp_zyzb["近3月实际成交天数占比(%)"] = data['TRADEDAYS_PER']
        comp_zyzb["挂牌以来违规次数"] = data['ILLEGALCISHUTIMES']
    company_info["重要指标"] = comp_zyzb

    # 股东列表(公司)（异步加载）
    sdgd_url = "http://xinsanban.eastmoney.com/api/F10/HomeIndex/GetShareholder?code={}&rank=1".format(code_id)
    r = requests.get(sdgd_url, headers={'Accept': 'application/json'})
    datas = json.loads(r.text)['result']
    gd_list = []
    for data in datas:
        gd_dict = {}
        gd_dict["股东名称"] = data['SHAREHDNAME']
        gd_dict["股东性质"] = data['SHAREHDNATURE']
        gd_dict["持股数量(股)"] = data['SHAREHDNUM']
        gd_dict["持股比例(%)"] = data['SHAREHDNUMPER']
        gd_list.append(gd_dict)
    company_info["股东列表"] = gd_list

    # 高管列表（异步加载）
    gglb_url = "http://xinsanban.eastmoney.com/api/F10/CompanyInfo/GetCompanyExecutives?code={}&page=1&pagesize=20&sortType=STR_PLEVEL&sortRule=1".format(code_id)
    r = requests.get(gglb_url, headers={'Accept': 'application/json'})
    datas = json.loads(r.text)['result']
    gg_list = []
    for data in datas:
        gg_dict = {}
        gg_dict["姓名"] = data['STR_NAME']
        gg_dict["职务"] = data['POSITION']
        gg_dict["性别"] = data['SEX']
        gg_dict["学历"] = data['HIGHESTDEGREE']
        gg_dict["年龄"] = data['AGE']
        gg_dict["持股数量(万股)"] = data['HOLDSHARE']
        gg_dict["简历"] = data['CLB_RESUME']
        gg_list.append(gg_dict)
    company_info["高管列表"] = gg_list
    
    company_name = comp_gszl["公司全称"]
    all_company_info[company_name] = company_info
save_to_json(all_company_info, SAVE_PATH)