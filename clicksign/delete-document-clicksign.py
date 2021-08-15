import requests, json


def handler(event, context):
    url = "https://{}.clicksign.com/api/v1/{}?access_token={}".format(event['stage'], event['file_token'],
                                                                      event['access_token'])
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Host': 'sandbox.clicksign.com',
        'Accept': 'application/json'
    }

    response = requests.request("DELETE", url, headers=headers, data=payload)
    return json.loads(json.dumps(response.text.encode('utf8')))
