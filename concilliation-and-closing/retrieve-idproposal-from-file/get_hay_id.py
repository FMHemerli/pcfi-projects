import pandas as pd, json

keys = pd.read_excel("xxx.xlsx", dtype=str, encoding='utf8')
print(keys)
print(list(keys['id proposal']))
with open("keys.json") as file:
    data = json.load(file)
json = pd.DataFrame.from_dict(data['results'], orient='columns', dtype=str)
keys['hay id'] = ['']*len(keys['id proposal'])
for id in range(len(keys['id proposal'])):
    for hay_id in range(len(json['_id'])):
        if keys['id proposal'][id] in json['tied_up_documents'][hay_id]:
            keys['hay id'][id] = json['_id'][hay_id]

keys.to_excel("xxx.xlsx", engine='auto', index=False)