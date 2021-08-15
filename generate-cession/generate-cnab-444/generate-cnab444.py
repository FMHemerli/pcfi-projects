import pandas as pd, json, os, boto3, unicodedata
from datetime import datetime as dt2

day = dt2.strftime(dt2.now(), "%d")
month = dt2.strftime(dt2.now(), "%m")
today = dt2.strftime(dt2.now(), "%d%m%y")

with open("input.json", 'r') as map_file:
    payload = json.loads(map_file.read())
map_file.close()

cnab = pd.DataFrame({}, dtype=str)
for contract in payload:
    contract['current_value'] = contract['values']['current_value']
    contract['venal_value'] = contract['values']['venal_value']
    contract = {key: contract[key] for key in contract if key != 'values'}

cnab = pd.DataFrame.from_dict(payload, orient='columns', dtype=str)
del payload

cnab['indetificacaoRegistro'] = "1"
cnab['debitoAutomaticoCC'] = "".ljust(19)
cnab['coobrigacao'] = "02"  # variavel obrigatoria item n 3
cnab['caracteristicaEspecial'] = "".zfill(2)
cnab['modalidadeOp'] = "".zfill(4)
cnab['naturezaOp'] = "".zfill(2)
cnab['origemRecurso'] = "".zfill(4)
cnab['classeRisco'] = "A "
cnab['zero'] = "0"
cnab['controleParticipante'] = cnab['contract'].apply(lambda x: x.ljust(25))  # variavel obrigatoria item n 10
cnab['bank'] = "".zfill(3)  # variavel obrigatoria item n 11
cnab['zeros'] = "".zfill(5)
cnab['tituloBanco'] = "".zfill(11)
cnab['nossoNumero'] = "".ljust(1)
cnab['valorPago'] = "".zfill(10)
cnab['condicaoEmissao'] = "".zfill(1)
cnab['debitoAutomaticoID'] = "".ljust(1)
cnab['dataLiquidacao'] = "".zfill(6)
cnab['bancoOpID'] = "".ljust(4)
cnab['rateioCredito'] = "".ljust(1)
cnab['endAvisoDebitoAutomatico'] = "".zfill(1)
cnab['blank2'] = "".ljust(2)
cnab['ocorrenciaID'] = "01"  # varival obrigatoria sessao 4.1 item n 23
cnab['ccb'] = cnab['ccb'].apply(lambda x: x.zfill(10))  #cnab['ccb'].apply(lambda x: x.ljust(10)  #variavel obrigatoria item n 24
cnab['last_due'] = cnab['last_due'].apply(lambda x: dt2.strftime(dt2.strptime(x, "%Y-%m-%d 00:00:00"), "%d%m%y")) # variavel obrigatora item n 25
cnab['valorTitulo'] = cnab['final_amount'].apply(lambda x: x.replace(".", "").zfill(13))  # variavel obrigatoria item n 26
cnab['bancoEncarregado'] = "".zfill(3)
cnab['agenciaDepositaria'] = "".zfill(5)
cnab['especieTitulo'] = "60"  # contrato
cnab['identificacao'] = "".ljust(1)
cnab['cnab_date'] = cnab['contract_date'].apply(lambda x: dt2.strftime(dt2.strptime(x, "%Y-%m-%d 00:00:00"), "%d%m%y"))
cnab['primeiraInstr'] = "".zfill(2)
cnab['segundaInstr'] = "".zfill(1)
cnab['tipoCedente'] = "02"  # PJ
cnab['zeros11'] = "".zfill(12)  # item 35 com erro, sao 12 zeros e nao 11
cnab['numeroTermoCessao'] = "02".ljust(19)  #cnab['cession'].apply(lambda x: x.ljust(19)
cnab['current_value'] = cnab['venal_value'].apply(lambda x: x.replace(".", "").zfill(13))
cnab['valorAbatimento'] = "".zfill(13)
cnab['tipoInscricaoSacado'] = "01"  # PF
cnab['document_number'] = cnab['document_number'].apply(lambda x: x.replace(".", "").replace("-", "").zfill(14))
cnab['name'] = cnab['name'].apply(lambda x: x.ljust(40))
cnab['address'] = cnab['address'].apply(lambda x: x.ljust(40))
cnab['numeroNfDuplicata'] = "".ljust(9)
cnab['numeroNfDuplicataSerie'] = "".ljust(3)
cnab['zip_code'] = cnab['zip_code'].apply(lambda x: x.replace("-", "").replace(".", ""))
cnab['cedente'] = ("xxxx" + "xxxx").ljust(60)
cnab['chaveNf'] = "".zfill(44)

cnab = cnab[
    [
        'indetificacaoRegistro', 'debitoAutomaticoCC', 'coobrigacao', 'caracteristicaEspecial', 'modalidadeOp',
        'naturezaOp', 'origemRecurso', 'classeRisco', 'zero', 'controleParticipante', 'bank', 'zeros',
        'tituloBanco', 'nossoNumero', 'valorPago', 'condicaoEmissao', 'debitoAutomaticoID', 'dataLiquidacao',
        'bancoOpID', 'rateioCredito', 'endAvisoDebitoAutomatico', 'blank2', 'ocorrenciaID', 'ccb',
        'last_due', 'valorTitulo', 'bancoEncarregado', 'agenciaDepositaria', 'especieTitulo','identificacao',
        'cnab_date', 'primeiraInstr', 'segundaInstr', 'tipoCedente', 'zeros11', 'numeroTermoCessao', 'current_value',
        'valorAbatimento', 'tipoInscricaoSacado', 'document_number', 'name', 'address', 'numeroNfDuplicata',
        'numeroNfDuplicataSerie', 'zip_code', 'cedente', 'chaveNf'
    ]
]

cnab.set_index(pd.Series(range(1, len(cnab.index) + 1)), inplace=True)
cnab['name'].apply(
    lambda value: str(unicodedata.normalize('NFKD', str(value)).encode('ASCII', 'ignore').decode('UTF-8').upper()))
cnab['address'].apply(
    lambda value: str(unicodedata.normalize('NFKD', str(value)).encode('ASCII', 'ignore').decode('UTF-8').upper()))

fund_name = "xxxxxx"
fund_name = str(unicodedata.normalize('NFKD', str(fund_name)).encode('ASCII', 'ignore').decode('UTF-8').upper())
header_fund_name = fund_name[0:30] if len(fund_name) > 30 else fund_name.ljust(30)

fline = "01xxx{}xxxx{}xxxxx{}".format(
    header_fund_name, today, "".ljust(321))
lline = "9" + "".ljust(437)

cnab440 = fline + "000001" + "\n" + "\n".join(
    ["".join([cnab[column][row] for column in cnab.columns]) + str(row + 1).zfill(6) for row in
     cnab.index]) + "\n" + lline + str(len(cnab.index) + 2).zfill(6)
del cnab

num = [str(x) for x in range(10)]
lett = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
itr = num + lett
for i in itr:
    for j in itr[1:-1]:
        try:
            filename_cnab444 = " CB{}{}{}.REM".format(day, month, i+j)
            # os.system("rm -rf {}".format(filename_cnab444))
            os.mknod(filename_cnab444)
            with open(filename_cnab444, 'wb') as cm550:
                cm550.write(bytes(cnab440, 'utf8'))
                cm550.close()
            break
        except:
            continue
    else:
        continue
    break