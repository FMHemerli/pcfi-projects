import pandas as pd, unicodedata
from locale import setlocale, LC_ALL
import xmltodict

setlocale(LC_ALL, 'pt_BR.UTF-8')

with open("consolidated.xml") as UN_list:
    xml = UN_list.read()
    fop_dict = xmltodict.parse(xml)

fop_list = pd.DataFrame.from_dict(fop_dict['CONSOLIDATED_LIST']['INDIVIDUALS']['INDIVIDUAL'], orient='columns', dtype=str)[['DATAID', 'FIRST_NAME', 'SECOND_NAME', 'THIRD_NAME', 'FOURTH_NAME']]
fop_list.to_csv("fop_list")
for name in ['FIRST_NAME', 'SECOND_NAME', 'THIRD_NAME', 'FOURTH_NAME']:
    fop_list[name] = fop_list[name].apply(lambda value: str(unicodedata.normalize('NFKD', str(value)).encode('ASCII', 'ignore').decode('UTF-8').upper()))
fop_list['Name'] = fop_list['FIRST_NAME'] + " " + fop_list['SECOND_NAME'] + " " + fop_list['THIRD_NAME'] + " " + fop_list['FOURTH_NAME']
fop_list['Name'] = fop_list['Name'].apply(lambda value: value.replace(" NAN", "").replace(" NA", "").replace(" NONE", ""))
fop_list = fop_list[['DATAID', 'Name']]
print(fop_list)

client_list = pd.read_json("parati_clients.json", orient='records')

x = [""]*len(client_list['results'])
for i in range(len(x)):
    if 'documents' in client_list['results'][i]:
        x[i] = (client_list['results'][i]['general']['name']['first']) + " " + client_list['results'][i]['general']['name']['last']
client_list = pd.DataFrame({'Name': x})
client_list['Name'] = client_list['Name'].apply(lambda value: str(unicodedata.normalize('NFKD', value).encode('ASCII', 'ignore').decode('UTF-8').upper()))

comparison = client_list[client_list['Name'].isin(fop_list['Name'])]
print(comparison)

comparison.to_csv("Analise_FOP_base_clientes_Parati.csv", encoding='utf-8', sep=";", index=False)