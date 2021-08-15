import requests, json, hmac, hashlib

#informações sensíveis foram ocultadas da função Lambda
def handler(event, context):
    url = "https://{}.clicksign.com/api/v1/sign?access_token={}".format(event['stage'], event['access_token'])

    if event['signer'] == "":
        api_secret = ""
    elif event['signer'] == "":
        api_secret = ""

    secret_hmac = hmac.new(bytes(api_secret, 'ascii'), msg=bytes(str(event['request_signature_key']), 'ascii'),
                           digestmod=hashlib.sha256).hexdigest()

    payload = {
        "request_signature_key": event['request_signature_key'],
        "secret_hmac_sha256": secret_hmac
    }
    headers = {
        'Content-Type': 'application/json',
        'Host': '{}.clicksign.com'.format(event['stage']),
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    try:
        return json.loads(response.text.encode('utf8'))
    except json.decoder.JSONDecodeError:
        return "SUCCESS!"
