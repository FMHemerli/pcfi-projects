import pandas as pd, unicodedata
from locale import setlocale, LC_ALL

setlocale(LC_ALL, 'pt_BR.UTF-8')

pep_list = pd.read_csv("202001_PEP.csv", encoding='iso-8859-1', dtype=str, sep=';')[['CPF', 'Nome_PEP']]
pep_list['CPF'] = pep_list['CPF'].apply(lambda value: str(value).replace("*", "").replace("\n", ""))
pep_list['Name'] = pep_list['Nome_PEP']
pep_list['Name'] = pep_list['Name'].apply(lambda value: str(unicodedata.normalize('NFKD', value).encode('ASCII', 'ignore').decode('UTF-8').upper()))
pep_list = pep_list[['CPF', 'Name']]
client_list = pd.read_json("pcfi_clients.json", orient='records')

x = [""]*len(client_list['results'])
y = [""]*len(client_list['results'])

for i in range(len(x)):
    if 'documents' in client_list['results'][i]:
        x[i] = (client_list['results'][i]['general']['name']['first']) + " " + client_list['results'][i]['general']['name']['last']
        y[i] = str(client_list['results'][i]['documents'][0]['number'])
        y[i] = "{}{}{}.{}{}{}.{}{}{}-{}{}".format(y[i][0], y[i][1], y[i][2], y[i][3], y[i][4], y[i][5], y[i][6], y[i][7], y[i][8],
                                                  y[i][9], y[i][10])

client_list = pd.DataFrame({'CPF': y, 'Name': x})
client_list['Name'] = client_list['Name'].apply(lambda value: str(unicodedata.normalize('NFKD', value).encode('ASCII', 'ignore').decode('UTF-8').upper()))
client_list['Masked CPF'] = client_list['CPF'].apply(lambda value: value[3:12])
client_list['Comparison'] = client_list['Masked CPF'] + client_list['Name']
pep_list['Comparison'] = pep_list['CPF'] + pep_list['Name']
comparison = client_list[client_list['Comparison'].isin(pep_list['Comparison'])]

comparison = comparison[['Name', 'CPF']]
print(comparison)
comparison.to_csv("Analise_PEP_base_clientes_Parati.csv", encoding='utf-8', sep=",", index=False)