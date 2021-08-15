import json


def handler(event, context):
    try:
        lot_id = event[1]['results'][0]['_id']
    except:
        lot_id = ""

    try:
        correspondent_key = event[0]['results'][0]['correspondent']
    except:
        correspondent_key = ""

    try:
        transaction_key = event[0]['results'][0]['payment']['transaction_key']
    except:
        transaction_key = ""

    output = {
        "lot_id": lot_id,
        "correspondent_key": correspondent_key,
        "transaction_key": transaction_key
    }

    return json.loads(json.dumps(output))