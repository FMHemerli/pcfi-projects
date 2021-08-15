import json
from datetime import datetime as dt2, timedelta as td

with open("translate-input-contract.json") as data:
    file = json.loads(data.read())
    for contract in file:
        contract['contrato']['clientepessoafisica']['cpf'] = contract['contrato']['clientepessoafisica']['cpf'].replace(".", "").replace("-", "")
        contract['contrato']['datacontrato'] = contract['contrato']['datacontrato'].replace(" 00:00:00", "")
        contract['contrato']['dataprimeirovencto'] = contract['contrato']['dataprimeirovencto'].replace(" 00:00:00", "")
        contract['contrato']['dataultimovencto'] = contract['contrato']['dataultimovencto'].replace(" 00:00:00", "")
        contract['contrato']['clientepessoafisica']['rg']['dataexpedicao'] = contract['contrato']['clientepessoafisica']['rg']['dataexpedicao'].replace(" 00:00:00", "")
        contract['operacao']['dataoperacao'] = contract['operacao']['dataoperacao'].replace(" 00:00:00", "")
        contract['contrato']['clientepessoafisica']['residencia']['endereco']['cep']=contract['contrato']['clientepessoafisica']['residencia']['endereco']['cep'].replace(".", "").replace("-", "")
        contract['contrato']['diapadraovencto'] = contract['contrato']['diapadraovencto'].replace(" 00:00:00", "")
        contract['contrato']['diapadraovencto'] = dt2.strftime(dt2.strptime(contract['contrato']['dataprimeirovencto'], "%Y-%m-%d"), "%d")
        contract['contrato']['plano'] = "9018"
        contract['contrato']['valorfinanciado'] = str(float(contract['contrato']['valorsolicitado']) + float(
            contract['contrato']['iof']))
        contract['contrato']['diascarencia'] = str((dt2.strptime(
            contract['contrato']['dataprimeirovencto'].replace(" 00:00:00", ""),
            "%Y-%m-%d"
        ) - dt2.strptime(
            contract['operacao']['dataoperacao'].replace(" 00:00:00", ""),
            "%Y-%m-%d"
        ) - td(days=30)).days)
data.close()

with open("translate-input-contract.json", 'w') as data:
    data.write(str(json.dumps(file, indent=2)))
data.close()