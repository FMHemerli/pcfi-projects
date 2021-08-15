import numpy as np, numpy_financial as npf, json, locale
from dateutil.relativedelta import relativedelta as rd
from datetime import datetime as dt

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def handler(event, context):
    # Inputted variables
    ## Amounts
    request_amount = np.array([float(event['associated_tax']),
                               float(event['liquid_amount']),
                               float(event['discharge'])])
    ## Dates
    sales_date = np.datetime64(event['sales_date'], 'D')
    operation_date = np.datetime64(event['operation_date'], 'D')
    first_installment = np.datetime64(event['first_due'], 'D')
    terms = int(event['installments'])
    ## Rates
    contract_rate = float(event['contract_rate']) / 100
    tax = float(event['iof'])
    financed_amount = request_amount + tax

    # Calculated variables
    monthly_contract_rate = contract_rate
    daily_contract_rate = (1 + monthly_contract_rate) ** (1 / 30) - 1
    annual_contract_rate = ((1 + monthly_contract_rate) ** 12) - 1

    indexer = float(event['percent_indexer']) / 100
    venal_rate = annual_contract_rate * indexer
    monthly_venal_rate = (1 + venal_rate) ** (1 / 12) - 1
    daily_venal_rate = (1 + monthly_venal_rate) ** (1 / 30) - 1

    financed_amount = sum(request_amount) + tax
    grace = (first_installment - operation_date).astype(float) - 30
    anniversary_value = financed_amount * ((1 + daily_contract_rate) ** grace)

    # Financial calculations
    payment = npf.pmt(monthly_contract_rate, terms, anniversary_value, 0, 0)
    payment_matrix = np.array([[first_installment, 0, payment, 0., 0., first_installment]] * terms)
    for npar in range(terms):
        payment_matrix[npar][0] = np.datetime64(payment_matrix[npar][0].astype(dt) + rd(days=30) * npar)
        payment_matrix[npar][5] = np.datetime64(payment_matrix[npar][0].astype(dt) - rd(days=30) * npar + rd(months=1) * npar)
        payment_matrix[npar][1] = (payment_matrix[npar][0].astype(dt) - sales_date.astype(dt)).days - 2
        #if sales_date >= payment_matrix[npar][5] or (payment_matrix[npar][5] - sales_date).astype(int) <= 15:
        if sales_date >= payment_matrix[npar][5]:
            pass
        else:
            payment_matrix[npar][1] = (payment_matrix[npar][0].astype(dt) - sales_date.astype(dt)).days - 2
            # payment_matrix[npar][0] = np.datetime64(payment_matrix[npar][0].astype(dt) - rd(days=30) * npar + rd(months=1) * npar)
            payment_matrix[npar][3] = npf.pv(daily_contract_rate, payment_matrix[npar][1], 0, payment, 0)
            payment_matrix[npar][4] = npf.pv(daily_venal_rate, payment_matrix[npar][1], 0, payment, 0)
        payment_matrix[npar][0] = payment_matrix[npar][5]
        payment_matrix[npar][0] = np.datetime_as_string(payment_matrix[npar][0], 'auto')
        payment_matrix[npar][5] = payment_matrix[npar][0]
    # print(payment_matrix)
    current_value = np.sum(payment_matrix, axis=0)[3]
    venal_value = np.sum(payment_matrix, axis=0)[4]
    report = {"current_value": "{:.2f}".format(current_value),
              "venal_value": "{:.2f}".format(venal_value),
              "installments": [{}] * terms}

    for npar in range(terms):
        report['installments'][npar] = {
            "installment_number": str(npar + 1),
            "date": payment_matrix[npar][0],
            "current_value": "{:.2f}".format(payment_matrix[npar][3]),
            "venal_value": "{:.2f}".format(payment_matrix[npar][4])
        }
    # print(json.dumps(report, indent=2))
    return json.loads(json.dumps(report))

# with open("input.json") as x:
#     data = json.loads(x.read())
# x.close()
#
# print(json.dumps(handler(data, 0), indent=2))
