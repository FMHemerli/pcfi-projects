import json
from datetime import datetime as dt2, timedelta as td

with open("translate-input-contract.json") as data:
    file = json.loads(data.read())
    for contract in file:
        contract['cont']['clientpf']['cpf'] = contract['cont']['clientpf']['cpf'].replace(".", "").replace("-", "")
        contract['cont']['dtcont'] = contract['cont']['dtcont'].replace(" 00:00:00", "")
        contract['cont']['dtfirstdue'] = contract['cont']['dtfirstdue'].replace(" 00:00:00", "")
        contract['cont']['dtlastdue'] = contract['cont']['dtlastdue'].replace(" 00:00:00", "")
        contract['cont']['clientpf']['idn']['dtexp'] = contract['cont']['clientpf']['idn']['dtexp'].replace(" 00:00:00", "")
        contract['op']['dtop'] = contract['op']['dtop'].replace(" 00:00:00", "")
        contract['cont']['clientpf']['resid']['adr']['cep']=contract['cont']['clientpf']['resid']['adr']['cep'].replace(".", "").replace("-", "")
        contract['cont']['daystddue'] = contract['cont']['daystddue'].replace(" 00:00:00", "")
        contract['cont']['daystddue'] = dt2.strftime(dt2.strptime(contract['cont']['dtfirstdue'], "%Y-%m-%d"), "%d")
        contract['cont']['plan'] = ""
        contract['cont']['amntfincd'] = str(float(contract['cont']['amntsolicit']) + float(
            contract['cont']['iof']))
        contract['cont']['dayscarencia'] = str((dt2.strptime(
            contract['cont']['dtfirstdue'].replace(" 00:00:00", ""),
            "%Y-%m-%d"
        ) - dt2.strptime(
            contract['op']['dtop'].replace(" 00:00:00", ""),
            "%Y-%m-%d"
        ) - td(days=30)).days)
data.close()

with open("translate-input-contract.json", 'w') as data:
    data.write(str(json.dumps(file, indent=2)))
data.close()