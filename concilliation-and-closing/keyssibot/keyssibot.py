import pandas as pd, os, boto3, json
from locale import setlocale, LC_NUMERIC, atof

setlocale(LC_NUMERIC, 'pt_BR.UTF-8')

s3client = boto3.client('s3')

try:
    os.system('rm /tmp/*')
except:
    pass


# File operations
def handler(event, context):
    model = "commission"

    file = event['key'].split('/')[-1]
    tempfile = "/tmp/.~temp." + file

    s3client.download_file(event['bucket'], event['key'], "/tmp/" + file)

    sheet = pd.read_excel("/tmp/" + file, encode='utf-8', dtype=str).set_index('CCB')
    sheet.to_excel(tempfile, engine='auto')  # Write file without formulas
    sheet = pd.read_excel(tempfile, encode='utf-8', dtype=str).set_index('CCB')

    for column in list(sheet.columns):
        if 'CPF' in column or 'CNPJ' in column:
            sheet[column] = sheet[column].apply(lambda value: value.replace(".", "").replace("-", "").replace("/", ""))
            try:
                sheet[column] = sheet[column].apply(
                    lambda value: "{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}".format(value[0], value[1],
                                                                            value[2], value[3],
                                                                            value[4], value[5],
                                                                            value[6], value[7],
                                                                            value[8], value[9],
                                                                            value[10], value[11],
                                                                            value[12], value[13]))
            except:
                sheet[column] = sheet[column].apply(
                    lambda value: "{}{}{}.{}{}{}.{}{}{}-{}{}".format(value[0], value[1],
                                                                     value[2], value[3],
                                                                     value[4], value[5],
                                                                     value[6], value[7],
                                                                     value[8], value[9],
                                                                     value[10]))

    sheet.fillna(0, inplace=True)
    for column in list(sheet.columns):
        try:
            sheet[column] = sheet[column].astype(str).apply(lambda value: atof(value.replace(".", ",")))
        except:
            pass

    if model == "commission":
        comm_p = 0.008 if 'xxx' in file else 0.008 if 'xxxx' in file else 0.004 if 'xxxxx' in file else 0

        if 'comission' not in list(sheet.columns):
            sheet['comission'] = (sheet['financial_amount'] + sheet['fintech_amount']) / sheet['Liquid amount']

        if 'financial_amount' not in list(sheet.columns):
            sheet['financial_amount'] = sheet['Liquid amount'] * comm_p
        if 'fintech_amount' not in list(sheet.columns):
            sheet['fintech_amount'] = (sheet['comission'] / 100 - comm_p) * sheet['Liquid amount']

        sheet['commission_amount'] = sheet['fintech_amount'] + sheet['financial_amount']
        liquid_total = sheet['Liquid amount'].sum(axis=0)
        fintech_total = sheet['fintech_amount'].sum(axis=0)
        financial_total = sheet['financial_amount'].sum(axis=0)
        commission_total = sheet['commission_amount'].sum(axis=0)
    elif model == "spread":
        venal_total = sheet['venal_amount'].sum(axis=0)
        financied_total = sheet['financied_amount'].sum(axis=0)
        spread_total = sheet['spread_amount'].sum(axis=0)

    if 'xxx' in file:
        minimal = 9000
    elif 'xxxx' in file:
        minimal = 2000 + financial_total
    elif 'xxxxx' in file:
        minimal = 15000
    elif 'xxxxxx' in file:
        minimal = 15000

    if model == "commission":
        if financial_total < minimal:
            diff = commission_total - minimal
            retention = minimal
            Sym = "(-) Custo fixo"
        else:
            diff = commission_total - financial_total
            retention = financial_total
            Sym = ""
        rate = diff / commission_total
        sheet['updated_commission'] = sheet['commission_amount'].apply(lambda x: x * rate)
        new_total = sheet['updated_commission'].sum(axis=0)
        totals = pd.DataFrame(
            [[None, "TOTAL", round(liquid_total, 2), round(fintech_total, 2), round(financial_total, 2),
              round(commission_total, 2), round(new_total, 2)]],
            columns=['CCB', 'Favorecido', 'Liquid amount', 'fintech_amount',
                     'financial_amount', 'commission_amount', 'updated_commission']).set_index('CCB')
        footer_row = pd.DataFrame([[None, "FINAL", round(diff, 2), round(retention, 2), Sym, rate]],
                                  columns=['CCB', 'Favorecido', 'fintech_amount', 'financial_amount',
                                           'commission_amount', 'updated_commission']).set_index('CCB')
    elif model == "spread":
        if spread_total < minimal:
            diff = venal_total - minimal
            retention = minimal
        else:
            diff = venal_total - spread_total
            retention = spread_total
        rate = diff / financied_total
        sheet['updated_financied'] = sheet['financied_amount'].apply(lambda x: x * rate)
        new_total = sheet['updated_financied'].sum(axis=0)
        totals = pd.DataFrame([[None, "TOTAL", round(venal_total, 2), round(financied_total, 2), round(spread_total, 2),
                                round(new_total, 2)]],
                              columns=['CCB', 'Favorecido', 'venal_amount', 'financied_amount',
                                       'spread_amount', 'updated_financied']).set_index('CCB')
        footer_row = pd.DataFrame([[None, "FINAL", round(diff, 2), round(retention, 2), "(-) Custo fixo", rate]],
                                  columns=['CCB', 'Favorecido', 'financied_amount', 'spread_amount', 'venal_amount',
                                           'updated_financied']).set_index('CCB')

    sheet = sheet.sort_values(by='Favorecido', axis=0, ascending=True).append(totals).append(footer_row)

    filename = "Fechamento_" + file
    folder = event['key'].split("/")[0:-1]
    path = ""
    for key in folder:
        path += key + "/"

    filename = filename.replace(".xlsx", "_2020.xlsx")
    sheet.to_excel("/tmp/" + filename, engine='auto')

    s3client.upload_file('/tmp/' + filename, 'parati-teste', path + filename)
    return json.loads(json.dumps({"bucket": event['bucket'],
                                  "path": path + filename}))
