import json, boto3, pandas as pd, os
from locale import atof, setlocale, LC_NUMERIC

setlocale(LC_NUMERIC, 'pt_BR.UTF-8')

s3client = boto3.client('s3')
try:
    os.system('rm -rf /tmp/*')
except:
    pass


def handler(event, context):
    s3client.download_file(event['bucket'], event['key'], '/tmp/sheet')
    obj = pd.read_excel('/tmp/sheet', encoding='utf-8', dtype=str)

    if event['type'] == "hay":
        obj = obj.drop_duplicates(subset='hay id', keep="first", ignore_index=True)
        ids = [id for id in obj['id proposal']]
    elif event['type'] == "proposal":
        ids = [id for id in obj['id proposal']]
    id_list = {'_id': ids}

    if 'Rendimento' in event and 'hay id' in event['Rendimento'][0]:
        obj['hay id'] = pd.DataFrame.from_dict(event['Rendimento'], orient='columns', dtype=str)['hay id']

    try:
        rendimento = pd.DataFrame.from_dict(event['Rendimento'], orient='columns', dtype=str)
        obj['valorEfetivacao'] = rendimento['ValorEfetivacao'].apply(lambda value: float(value.replace("'", "").replace(",", ".")))
        obj['Autenticacao'] = rendimento['Autenticacao']
        obj['hay id'] = rendimento['hay_id']

        obj['Liquid amount'] = obj['Liquid amount'].apply(lambda value: float(value.replace("'", "").replace(",", ".")))
        if event['type'] == "proposal":
            obj['status'] = abs(obj['Liquid amount'] - obj['valorEfetivacao'])
            obj['status'] = ['OK' if value <= 0.09 else 'NOT OK' for value in obj['status']]

        elif event['type'] == "hay":
            unique_id = list(obj['hay id'])
            oobj = pd.read_excel('/tmp/sheet', encoding='utf-8', dtype=str)
            oobj['Liquid amount'] = oobj['Liquid amount'].apply(lambda value: float(value.replace("'", "").replace(",", ".")))
            obj = oobj.merge(obj, how='inner', on='hay id', suffixes=("", "_y"))
            obj = obj.drop([x for x in list(obj.columns) if "_y" in x], axis=1)

            # unique_id = list(set(list(obj['hay id']))); print(unique_id)
            slices_list = [pd.DataFrame({'0': ''}, index=[0])] * len(unique_id)
            obj['hay amount'] = [0.] * len(obj['Liquid amount'])
            sum_list = [0.] * len(unique_id)
            for some_id in range(len(unique_id)):
                slices_list[some_id] = obj.loc[obj['hay id'] == unique_id[some_id]]
                sum_list[some_id] = slices_list[some_id]['Liquid amount'].sum(axis=0)
                for rows in range(len(slices_list[some_id]['hay id'])):
                    slices_list[some_id]['hay amount'] = sum_list[some_id]

            for i in range(len(unique_id)):
                if i == 0:
                    cframe = slices_list[i]
                else:
                    cframe = cframe.append(slices_list[i], ignore_index=True)
            cframe = cframe.reset_index().sort_index()

            obj['hay amount'] = cframe['hay amount']
            obj['status'] = abs(obj['hay amount'] - obj['valorEfetivacao'])
            obj['status'] = ['OK' if value <= 0.09 else 'NOT OK' for value in obj['status']]
            print(obj)

        filename = event['key'].split("/")[-1]
        folder = event['key'].split("/")[0:-1]
        path = "/".join([key for key in folder]) + "/"
        new_filename = 'review_' + filename

        obj.to_excel('/tmp/' + new_filename, engine="xlsxwriter", encoding='utf-8', index=False)
        s3client.upload_file('/tmp/' + new_filename, 'xxx', path + new_filename)
        return path + new_filename
    except KeyError:
        return json.loads(json.dumps(id_list))