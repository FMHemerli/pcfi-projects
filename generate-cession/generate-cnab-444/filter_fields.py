import json, locale, datetime as dt, pandas as pd, os

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")

months = {
    "1": "janeiro",
    "2": "fevereiro",
    "3": "março",
    "4": "abril",
    "5": "maio",
    "6": "junho",
    "7": "julho",
    "8": "agosto",
    "9": "setembro",
    "10": "outubro",
    "11": "novembro",
    "12": "dezembro"
}
today = dt.datetime.now()
date = dt.datetime.strftime(today, "%d%m%y")
current_month = str(today.month)
today = dt.datetime.strftime(today, "%d de {} de %Y".format(months[current_month]))


def frmt_n(x, vtype):
    if vtype == "money":
        x = locale.currency(float(x), grouping=True, symbol=False)
    elif vtype == "date":
        x = dt.datetime.strftime(dt.datetime.strptime(x, "%Y-%m-%d 00:00:00"), "%d/%m/%Y")
    else:
        pass
    return x


with open("input.json", 'r') as map_file:
    payload = json.loads(map_file.read())
map_file.close()

key_list = ['name', 'document_number', 'final_amount', 'last_due', 'venal_value', 'ccb']
inquiry_keys = ['ccb', 'contract']

output = []
inquiry_output = []
for contract in payload:
    ccb = contract['ccb']
    token = contract['contract']

    contract['venal_value'] = contract['values']['venal_value']
    contract = {key: contract[key] for key in contract if key != 'values'}
    contract = {key: contract[key] for key in key_list}
    contract['charges'] = str(
        round(
            float(contract['final_amount']) - float(contract['venal_value']), 2
        )
    )

    output.append(contract)
    inquiry_output.append({"ccb": ccb, "token_fintech": token})

contract_value = round(sum([float(contract['venal_value']) for contract in output]), 2)
contract_value = frmt_n(contract_value, "money")

for contract in output:
    contract['final_amount'] = frmt_n(contract['final_amount'], "money")
    contract['venal_value'] = frmt_n(contract['venal_value'], "money")
    contract['charges'] = frmt_n(contract['charges'], "money")
    contract['last_due'] = frmt_n(contract['last_due'], "date")

output_2 = {"document_value": contract_value, "date": today, "contracts": output}
output = pd.DataFrame.from_dict(output, orient="columns", dtype=str)
# output = output[['name', 'document_number', 'ccb', 'final_amount', 'charges', 'last_due', 'venal_value']]

sheet = pd.DataFrame()
sheet[
    [
        'Devedor',
        'CPF/CNPJ',
        'Nº da CCB',
        'Valor de Face (em R$)',
        'Encargos',
        'Vencimento',
        'Preço de Aquisição (em R$)'
    ]] = output[
    [
        'name',
        'document_number',
        'ccb',
        'final_amount',
        'charges',
        'last_due',
        'venal_value'
    ]]

footer_row = pd.DataFrame(
    [
        ["Preço de Aquisição dos Créditos: ",
         output_2['document_value']]
    ],
    columns=[
        'Vencimento',
        'Preço de Aquisição (em R$)'
    ]
)

sheet = sheet.append(footer_row, ignore_index=True).fillna("")

index = list(range(1, len(sheet.index) + 1))
sheet.index = index

sheet.to_excel("CONTRATOSTERMOCESSAO{}.xlsx".format(date), engine='auto')

print(json.dumps(output_2, indent=2))
print(json.dumps(inquiry_output, indent=2))