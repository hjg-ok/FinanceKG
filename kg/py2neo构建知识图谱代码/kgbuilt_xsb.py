import json
from py2neo import Node, Relationship, Graph
graph = Graph("bolt://localhost:7687",username="Graph",password="2333")
graph.delete_all()


data_path = "../data/shangshigongsichigu_xsb.json"
with open(data_path, 'r', encoding = 'utf-8') as fp:
    datas_comp_xsb = json.load(fp)     
# print(comp_xsb['上海中城联盟投资管理股份有限公司'].keys())

ts  = graph.begin()
cnt = 0
for comp in datas_comp_xsb.values():
#     if(cnt > 10):
#         break
    cnt += 1
    print(cnt)
    comp_gszl = comp["公司资料"]
    node = Node('新三板',name = comp_gszl["公司全称"])
    for kv in comp_gszl.items():
        prop_key = kv[0]
        prop_val = kv[1]
        node[prop_key] = prop_val
    node["证券资料"] = str(comp["证券资料"])
    node["财务政要"] = str(comp["财务政要"])
    node["重要指标"] = str(comp["重要指标"])
#     node.__primarylabel__ = "新三板"
#     node.__primarykey__ = "name"
    qs_node = Node("券商",name = comp["证券资料"]["持续督导券商"])
    qs_rel = Relationship(node,"督导券商",qs_node)
    ts.create(qs_rel)
    
    # 股东关系
    comp_gdlb = comp["股东列表"] # list
    for gudong in comp_gdlb:
        gd_node = Node(gudong["股东性质"],name = gudong["股东名称"])
        gd_rel = Relationship(node, '股东', gd_node)
        gd_rel["持股数量(股)"] = gudong["持股数量(股)"]
        gd_rel["持股比例(%)"] = gudong["持股比例(%)"]
        ts.create(gd_rel)
    
    # 高管关系
    comp_gglb = comp["高管列表"]
    for gaoguan in comp_gglb:
        gg_node = Node("个人",name = gaoguan["姓名"])
        for kv in gaoguan.items():
            key,val = kv[0],kv[1]
            gg_node[key] = val
        gg_node["姓名"] = None
        gg_node["职务"] = None
        gg_node["持股数量(万股)"] = None
        gg_rel = Relationship(node, '高管', gg_node)
        gg_rel["职务"] = gaoguan["职务"]
        if(gaoguan["持股数量(万股)"] != ""):
            gg_rel["持股数量(股)"] = gaoguan["持股数量(万股)"]
        ts.create(gg_rel) 
            
ts.commit()
    
print("finished")

