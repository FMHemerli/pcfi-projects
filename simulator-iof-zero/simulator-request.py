import requests, json

url = "https://api.paratifinanceira.com/simulate"

payload = {
    "amount": 100,
    "first_due": "2020-08-06",
    "number_installments": 10,
    "rate_month": 2.2,
    "type": "PF",
    "operation_date": "2020-07-06",
    "discounts": {
        "iof": {
            "financed": True
        }
    }
}
headers = {
    'Content-Type': 'application/json',
    'Content-Type': 'text/plain'
}

response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
x = json.dumps(json.loads(response.text), indent=2)
print(x)
