import json, os, boto3
from datetime import datetime as dt2

s3client = boto3.client("s3")

try:
    os.system("rm -rf /tmp/")
except:
    pass

def handler(event, context):
    if event['event'] == "save":
        filename = "output_{}.json".format(str(event['index']))
        try:
            os.system("rm -rf /tmp/{}".format(filename))
        except:
            pass

        os.mknod("/tmp/{}".format(filename))
        with open("/tmp/{}".format(filename), 'wb') as file:
            file.write(bytes(json.dumps(event['content']), 'utf8'))
        file.close()

        s3client.upload_file("/tmp/" + filename, event['bucket'], "cache/" + filename)
        response = {
            "key": "cache/{}".format(filename),
            "bucket": event['bucket'],
            "fragment": event['index']
        }
        return json.loads(json.dumps(response))
    elif event['event'] == "concat":
        for fragment in event['content']:
            print(fragment)
            print(fragment['bucket'], fragment['key'], fragment['key'].replace("cache/", "/tmp/"))
            s3client.download_file(fragment['bucket'], fragment['key'], fragment['key'].replace("cache/", "/tmp/"))

        filename = "MapOutput_{}.json".format(event['execution_name']+str(dt2.now().strftime("%Y%m%d")))
        try:
            os.system("rm -rf /tmp/{}".format(filename))
        except:
            pass

        os.mknod("/tmp/{}".format(filename))
        with open("/tmp/{}".format(filename), "wb") as output:
            output.write(bytes("[", 'utf8'))
            for fragment in range(len(event['content'])):
                with open("/tmp/output_{}.json".format(fragment),"r") as next_output:
                    data = next_output.read()
                    output.write(bytes("{},".format(str(data)), 'utf8'))
                next_output.close()
            output.write(bytes("\n{\"status\": \"finished\"}]", 'utf8'))
        output.close()

        s3client.upload_file("/tmp/{}".format(filename), event['bucket'], "cache/{}".format(filename))
        response = {
            "key": "cache/{}".format(filename),
            "bucket": event['bucket']
        }
        return json.loads(json.dumps(response))