import requests, json


def handler(event, context):
    url = "https://{}.clicksign.com/api/v1/notify_by_whatsapp?access_token={}".format(event['api']['stage'],
                                                                                      event['api']['access_token'])

    payload = {"request_signature_key": event['request_signature_key']}
    headers = {
        'Content-Type': 'application/json',
        'Host': '{}.clicksign.com'.format(event['api']['stage']),
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    try:
        return json.loads(response.text.encode('utf8'))
    except json.decoder.JSONDecodeError:
        return "SUCCESS"