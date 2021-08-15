import pandas as pd, numpy as np, boto3, os, json
from locale import atof, setlocale, LC_NUMERIC

setlocale(LC_NUMERIC, 'pt_BR.UTF-8')

s3client = boto3.client('s3')
try:
    os.system('rm -rf /tmp/*')
except:
    pass

def handler(event, context):
    s3client.download_file(event['bucket'], event['file1'], '/tmp/sheet1')
    s3client.download_file(event['bucket'], event['file2'], '/tmp/sheet2')

    sheet1 = pd.read_excel('/tmp/sheet1', encoding='utf-8').sort_index()
    sheet2 = pd.read_excel('/tmp/sheet2', encoding='utf-8').sort_index()

    for column in list(sheet1.columns):
        for i in range(len(sheet1[column])):
            sheet1[column][i] = str(sheet1[column][i])
            sheet2[column][i] = str(sheet2[column][i])

    for column in ['Liquid amount', 'Amount total', 'iof amount', 'Amount', 'Number installments', 'Rate month',
                   'Rate year', 'Installment', 'Cet', 'Cet year', 'financied_amount', 'iof']:
        for i in range(len(sheet1[column])):
            try:
                sheet1[column][i] = atof(sheet1[column][i])
                sheet2[column][i] = atof(sheet2[column][i])
            except:
                pass

    for data in list(sheet1.columns):
        sheet1[data] = np.where(sheet1[data] != sheet2[data], 'MISMATCH: ' + sheet1[data].astype(str), sheet1[data])
    filename = 'match_{}-{}.xlsx'.format(event['file1'], event['file2']).replace('.xlsx', '')
    sheet1.to_excel('/tmp/' + filename, engine='xlsxwriter')
    s3client.upload_file('/tmp/' + filename, event['bucket'], filename)
    return json.loads(json.dumps({'bucket':event['bucekt'], 'result_file': filename}))

