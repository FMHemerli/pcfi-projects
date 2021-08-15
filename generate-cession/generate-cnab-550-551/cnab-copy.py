mport pandas as pd, json, os, boto3, unicodedata
from datetime import datetime as dt2

today = dt2.strftime(dt2.now(), "%d%m%y")

s3client = boto3.client('s3')

with open("xxx.json", 'r') as map_file:
    payload = json.loads(map_file.read())[0:-1]
map_file.close()

contract_value = round(sum([float(contract['values']['venal_value']) for contract in payload]), 2)
cnab = pd.DataFrame({})
file = pd.DataFrame({})
for contract in payload:
    table = pd.DataFrame.from_dict(contract['values']['installments'], orient='columns', dtype=str)
    table['installment_number'] = table['installment_number'].apply(lambda x: x.zfill(3))
    table['date'] = table['date'].apply(lambda x: dt2.strftime(dt2.strptime(x, "%Y-%m-%d"), "%d%m%y"))
    table['installments'] = str(len(table['installment_number'])).zfill(3)
    cnab[['installment_number', 'date', 'installments']] = table[['installment_number', 'date', 'installments']]
    cnab['operation_date'] = dt2.strftime(dt2.strptime(contract['operation_date'], "%Y-%m-%d 00:00:00"), "%d%m%y")
    cnab['document_number'] = contract['document_number'].replace(".", "").replace("-", "").zfill(14)
    cnab['name'] = contract['name'].ljust(40)
    cnab['contract'] = contract['contract'].zfill(12)
    cnab['address'] = contract['address'].ljust(40)
    cnab['zip_code'] = contract['zip_code'].replace("-", "").replace(".", "")
    cnab['date_birth'] = dt2.strftime(dt2.strptime(contract['date_birth'], "%Y-%m-%d 00:00:00"), "%d%m%y")
    cnab['classificacaoRiscoSacado'] = "A "
    cnab['amount_total'] = contract['final_amount'].replace(".", "").zfill(13)
    cnab['cnpjFidc'] = "20217189000186"
    cnab['portion'] = contract['portion'].replace(".", "").zfill(11)
    cnab['identificacaoArqRemessa'] = "1"
    cnab['digitoVerificador'] = "1"
    cnab['valorTarifaFundo'] = "0000000"
    cnab['valorTarifaRepasse'] = "0000000"
    cnab['valorSeguro'] = "0000000"
    cnab['venal_value'] = table['venal_value'].apply(lambda x: x.replace(".", "").zfill(11) if x != "0.00" else "  DELETE!  ")
    cnab['contract_rate'] = contract['contract_rate'].replace(".", "").zfill(8)
    cnab['codigoIndexador'] = "00"
    cnab['percentIndexer'] = "00860000"
    cnab['blank83'] = "".rjust(83)
    cnab['blank3'] = "".rjust(3)
    cnab['blank8'] = "".rjust(8)
    cnab['blank17'] = "".rjust(17)
    cnab['blank4'] = "".rjust(4)
    cnab['blank26'] = "".rjust(26)
    cnab['blank20'] = "".rjust(20)
    cnab['blank6'] = "".rjust(6)
    cnab['blank11'] = "".rjust(11)
    cnab['blank7'] = "".rjust(7)
    cnab['blank7_2'] = "".rjust(7)
    cnab['blank7_3'] = "".rjust(7)
    cnab['blank19'] = "".rjust(19)
    cnab['blank12'] = "".rjust(12)
    cnab['blank3_2'] = "".rjust(3)
    cnab['blank8_2'] = "".rjust(8)
    cnab['CNPJConvenioEmpresaConsignado'] = "00489828000236"
    cnab['blank47'] = "".rjust(47)
    cnab['blank4_2'] = "".rjust(4)
    cnab['CS'] = "CS00"
    cnab['DocType'] = "CRT"
    #cnab.drop(cnab[cnab['venal_value'] == "  DELETE!  "].index, axis=0, inplace=True)
    cnab['installment_number'] = [str(n).zfill(3) for n in range(1, len(cnab['CS']) + 1)]
    file = file.append(cnab)

cnab = file[
    [
        'identificacaoArqRemessa', 'DocType', 'contract', 'CS', 'installment_number', 'installments', 'operation_date',
        'date', 'amount_total',
        'cnpjFidc', 'digitoVerificador', 'document_number', 'name', 'address', 'zip_code', 'date_birth',
        'classificacaoRiscoSacado', 'portion',
        'valorTarifaFundo', 'valorTarifaRepasse', 'valorSeguro', 'venal_value', 'contract_rate', 'codigoIndexador',
        'percentIndexer', 'blank83',
        'blank3', 'blank8', 'blank17', 'blank4', 'blank26', 'blank20', 'blank6', 'blank11', 'blank7', 'blank7_2',
        'blank7_3', 'blank19', 'blank12',
        'blank3_2', 'blank8_2', 'CNPJConvenioEmpresaConsignado', 'blank47', 'blank4_2'
    ]
]
del file

cnab.set_index(pd.Series(range(1, len(cnab['date']) + 1)).apply(lambda x: str(x).zfill(6)), inplace=True)
cnab['name'].apply(
    lambda value: str(unicodedata.normalize('NFKD', str(value)).encode('ASCII', 'ignore').decode('UTF-8').upper()))
cnab['address'].apply(
    lambda value: str(unicodedata.normalize('NFKD', str(value)).encode('ASCII', 'ignore').decode('UTF-8').upper()))

cnab.drop(cnab[cnab['venal_value'] == "  DELETE!  "].index, axis=0, inplace=True)

fline = "01{0}{0}0xxxxxx".format(
    today).ljust(543)
#lline = "20" + str(sum([float(n['values']['venal_value']) for n in payload])).replace(".", "").zfill(11).ljust(541)
lline = "20" + str(contract_value).replace(".", "").zfill(11).ljust(541)

cnab550 = fline + "000001" + "\n" + "\n".join(
    ["".join([cnab[column][row] for column in cnab.columns]) + str(row + 2).zfill(6) for row in
     range(len(cnab['CS']))]) + "\n" + lline + str(len(cnab['CS']) + 2).zfill(6)
cnab551 = fline + " 000001" + "\n" + "\n".join(
    ["".join([cnab[column][row] for column in cnab.columns]) + " " + str(row + 2).zfill(6) for row in
     range(len(cnab['CS']))]) + "\n" + lline + " " + str(len(cnab['CS']) + 2).zfill(6)
csv = "\n".join([";".join([cnab[column][row] for column in cnab.columns]) + ";" + str(row + 2).zfill(6) + ";" for row in
                 range(len(cnab['CS']))])

filename_cnab550 = "xxxx_{}_0001.rem".format(today)
filename_cnab551 = "xxxx_{}_0001.rem".format(today)
filename_csv = "xxxx_{}_0001.txt".format(today)
del cnab
try:
    os.system("rm -rf {}".format(filename_cnab550))
    os.system("rm -rf {}".format(filename_cnab551))
    os.system("rm -rf {}".format(filename_csv))
except:
    pass

os.mknod("" + filename_cnab550)
os.mknod("" + filename_cnab551)
os.mknod("" + filename_csv)

with open("" + filename_cnab550, 'wb') as cm550:
    cm550.write(bytes(cnab550, 'utf8'))
    cm550.close()

with open("" + filename_cnab551, 'wb') as cm551:
    cm551.write(bytes(cnab551, 'utf8'))
    cm551.close()

with open("" + filename_csv, 'wb') as cm550csv:
    cm550csv.write(bytes(csv, 'utf8'))
    cm550csv.close()
