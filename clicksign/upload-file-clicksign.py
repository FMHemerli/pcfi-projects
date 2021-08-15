import requests, json, base64, boto3

s3client = boto3.client('s3')

try:
    os.system("rm -rf /tmp/*")
except:
    pass


def handler(event, context):
    file = event['key'].split('/')[-1]
    s3client.download_file(event['bucket'], event['key'], "/tmp/" + file)

    with open("/tmp/" + file, "rb") as pdf:
        b64 = "data:application/pdf;base64,{}".format(base64.b64encode(pdf.read()).decode("ascii"))

    url = "https://{}.clicksign.com/api/v1/documents?access_token={}".format(event['stage'],
                                                                           event['access_token'])

    payload = {
        "document": {
            "path": "/" + file,
            "content_base64": b64,
            "auto_close": True,
            "locale": "pt-BR",
            "deadline": "2020-04-27T14:30:59-03:00",
            "sequence_enabled": False
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Host": "{}.clicksign.com".format(event['stage']),
        "Accept": "application/json"
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return json.loads(response.text.encode("utf8"))['document']['key']
