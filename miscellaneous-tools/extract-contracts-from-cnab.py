import pandas as pd, json

with open("file.rem") as cnab:
    cnab_string = str(cnab.read())
    cnab_string = cnab_string.replace(" ", "")
    cnab_string = cnab_string.split("\n")
    contracts = [token[10:16] for token in cnab_string[1:-1]]
    contracts = list(set(contracts))
    output = json.dumps(contracts)
    print(output)