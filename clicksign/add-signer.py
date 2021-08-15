import requests, json


def handler(event, context):
    url = "https://{}.clicksign.com/api/v1/signers?access_token={}".format(event['api']['stage'],
                                                                           event['api']['access_token'])

    payload = {
        "signer": {
            "email": event['signer']['email'],
            "phone_number": event['signer']['phone_number'],
            "auths": ["whatsapp"],
            "name": event['signer']['name'],
            "documentation": event['signer']['document'],
            "birthday": event['signer']['birth_date'],
            "has_documentation": True
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return json.loads(response.text.encode("utf8"))['signer']['key']