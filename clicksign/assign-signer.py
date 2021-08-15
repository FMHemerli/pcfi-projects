import requests, json


def handler(event, context):
    url = "https://{}.clicksign.com/api/v1/lists?access_token={}".format(event['stage'], event['access_token'])
    sign_as = "sign" if 'sign_as' not in event else event['sign_as']

    payload = {
        "list": {
            "document_key": event['document'],
            "signer_key": event['signer'],
            "sign_as": sign_as
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Host": "{}.clicksign.com".format(event['stage']),
        "Accept": "application/json"
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    return json.loads(response.text.encode("utf8"))['list']['document_key'] if "sign_as" not in event else \
    json.loads(response.text.encode("utf8"))['list']['request_signature_key']
