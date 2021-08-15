import pandas as pd, json, os

dataset = pd.read_csv("data.csv", dtype=str)
# print(dataset)
columns = list(dataset.columns)[0]
payload = json.dumps(list(dataset[columns]))
print(payload, len(dataset))

try:
    os.system("rm -rf output.json")
except:
    pass

os.mknod("output.json")
with open("output.json", 'w') as file:
    file.write(payload)