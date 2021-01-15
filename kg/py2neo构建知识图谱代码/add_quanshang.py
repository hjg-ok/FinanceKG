import json
from py2neo import Node, Relationship, Graph
graph = Graph("bolt://localhost:7687",username="Graph",password="2333")

data_path = "../data/quanshangliebiao_xsb.json"
with open(data_path, 'r', encoding = 'utf-8') as fp:
    datas_quanshang_xsb = json.load(fp)     
# print(comp_xsb['上海中城联盟投资管理股份有限公司'].keys())

ts  = graph.begin()
cnt = 0
for comp in datas_quanshang_xsb.values():
#     if(cnt > 10):
#         break
    cnt += 1
    print(cnt)
    comp_jbxx = comp["基本信息"]
    node = Node('证券公司',name = comp_jbxx["公司名称"])
    for kv in comp_jbxx.items():
        prop_key = kv[0]
        prop_val = kv[1]
        node[prop_key] = prop_val
    node["成交统计"] = str(comp["成交统计"])
    node["重要指标"] = str(comp["重要指标"])
#     node.__primarylabel__ = "证券公司"
#     node.__primarykey__ = "name"
    ts.create(node)
ts.commit()
    
print("finished")

