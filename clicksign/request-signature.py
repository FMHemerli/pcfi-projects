import requests, json


def handler(event, context):
    url = "https://{}.clicksign.com/api/v1/batches?access_token={}".format(event['api']['stage'], event['api']['access_token'])

    payload = {
        "batch": {
            "signer_key": event['signer']['clicksign']['signature'],
            "document_keys": event['documents'],
            "summary": True
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Host": "{}.clicksign.com".format(event['api']['stage']),
        "Accept": "application/json"
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return json.loads(response.text.encode("utf8"))['batch']['request_signature_key']