# 添加港股数据
import json
import csv
from py2neo import Node, Relationship, Graph
graph = Graph("bolt://localhost:7687",username="Graph",password="2333")

data_path_2 = "../data/ganggu2.json"
with open(data_path_2, 'r', encoding = 'utf-8') as fp:
    agu_json = json.load(fp)     
print(agu_json['长江和记实业有限公司'])

data_path_1 = "../data/ganggu1.csv"
with open(data_path_1, 'r', encoding = 'utf-8') as fp:
    agu_csv = csv.reader(fp)  
    header = next(agu_csv)
    num_p = len(header)
    print(header)
    for row in agu_csv:
        name = row[3]
#         print(name)
        if(name == "公司名称"):
            continue
        if(name not in agu_json):
            agu_json[name] = {}
        agu_json[name]['公司名称'] = name
        for i in range(1,num_p):
            field_name = header[i]
            field = row[i]
            if(field_name not in agu_json[name]):
                agu_json[name][field_name] = field
print(agu_json['长江和记实业有限公司'])
               
ts  = graph.begin()
cnt = 0
for comp in agu_json.values():
#     if(cnt > 10):
#         break
    cnt += 1
    print(cnt)
    node = Node('港股',name = comp["公司名称"])
    for kv in comp.items():
        prop_key = kv[0]
        prop_val = kv[1]
        node[prop_key] = prop_val
#     node.__primarylabel__ = "证券公司"
#     node.__primarykey__ = "name"
    ts.create(node)
ts.commit()
    
print("finished")

