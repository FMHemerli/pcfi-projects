import requests, json, boto3

s3client = boto3.client('s3')


def handler(event, context):
    url = "https://{}.clicksign.com/api/v1/documents/{}?access_token={}".format(event['stage'], event['document_key'], event['access_token'])

    payload = {}
    headers = {
        'Host': '{}.clicksign.com'.format(event['stage']),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    link = json.loads(response.text.encode('utf8'))['document']['downloads']['signed_file_url']

    doc = requests.get(link)
    try:
        filename = "/tmp/" + event['document_key'] + ".pdf"
        open(filename, 'wb').write(doc.content)
        bucket = event['bucket']
        key = event['stage'] + "/" + event['correspondent'] + "/ccb/signed/" + filename.replace("/tmp/", "")
        s3client.upload_file(filename, bucket, key)

        json_obj = {
            "bucket": bucket,
            "key": key,
            "proposal": event['filename'].replace(".pdf", "")
        }
    except KeyError:
        json_obj = {
            "token": event['filename'].replace(".pdf", "")
        }

    return json.loads(json.dumps(json_obj))
