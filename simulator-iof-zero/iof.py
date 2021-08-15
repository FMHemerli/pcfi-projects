import json
def iof(x, y):
    iof = y/100
    k = (iof/(1-iof)) * x

    response = {
        "requested_amount": "R$ {:.2f}".format(x).replace(".", ","),
        "iof": "{:.2f} %".format(y),
        "iof_amount": "R$ {:.2f}".format(k).replace(".", ","),
        "financed_amount": "R$ {:.2f}".format(x + k).replace(".", ","),
        "match": (x + k) - (x + k)*iof - x >= 0
    }
    return json.dumps(response, indent=2)

x = iof(1000, 1.8)
print(x)