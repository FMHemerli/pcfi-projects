import numpy as np, numpy_financial as npf, json, locale
from dateutil.relativedelta import relativedelta as rd
from datetime import datetime as dt


def handler(event, context):
    # Inputted variables
    ## Amounts
    request_amount = float(event['amount'])
    ## Dates
    operation_date = np.datetime64(event['operation_date'], 'D')
    first_installment = np.datetime64(event['first_due'], 'D')
    terms = int(event['number_installments'])
    ## Rates
    contract_rate = float(event['rate_month']) / 100
    tax = [float(event['discounts'][tax]['percent']) if 'percent' in event['discounts'][tax] else 0 for tax in
           event['discounts']]
    tax = sum(x / 100 * request_amount for x in tax)

    # Calculated variables
    monthly_contract_rate = contract_rate
    annual_rate = (1 + monthly_contract_rate) ** 12 - 1
    daily_contract_rate = (1 + monthly_contract_rate) ** (1 / 30) - 1
    financed_amount = request_amount + tax
    grace = (first_installment - operation_date).astype(int) - 31
    anniversary_value = financed_amount * ((1 + daily_contract_rate) ** grace)

    # Financial calculations
    payment = -npf.pmt(monthly_contract_rate, terms, anniversary_value, 0, 0)
    payment_matrix = np.array([[first_installment, 0, round(payment, 2)]] * terms)
    for npar in range(terms):
        payment_matrix[npar][0] = np.datetime64(payment_matrix[npar][0].astype(dt) + rd(days=30) * npar)
        if operation_date >= payment_matrix[npar][0]:
            payment_matrix[npar][1] = 0
        else:
            payment_matrix[npar][1] = (payment_matrix[npar][0].astype(dt) - operation_date.astype(dt)).days
            payment_matrix[npar][0] = np.datetime64(payment_matrix[npar][0].astype(dt) - rd(days=30) * npar + rd(months=1) * npar)
        payment_matrix[npar][0] = np.datetime_as_string(payment_matrix[npar][0], 'auto')
    current_value = np.sum(payment_matrix, axis=0)[2]

    last_due = first_installment.astype(dt) + rd(months=terms-1)
    total_days = (last_due - first_installment.astype(dt)).days
    cet = npf.irr(np.array([-request_amount] + [payment] * terms))
    cet_year = (1 + cet) ** 12 - 1

    report = {
        "amount": request_amount,
        "number_installments": terms,
        "pay_day": int(dt.strftime(first_installment.astype(dt), "%d")),
        "accepted_at": operation_date.astype(dt).strftime('%Y-%m-%d'),
        "operation_date": operation_date.astype(dt).strftime('%Y-%m-%d'),
        "first_due": first_installment.astype(dt).strftime('%Y-%m-%d'),
        "carency": int(grace),
        "rate_month": round(monthly_contract_rate * 100, 2),
        "rate_year": round(annual_rate * 100, 2),
        "type": event['type'],
        "discounts": {
            key: {
                value: event['discounts'][key][value] for value in event['discounts'][key]
            } for key in event['discounts']
        },
        "installment_amount": round(payment, 2),
        "iof_amount": int(
            event['discounts']['iof']['percent'] * financed_amount / 100 if 'percent' in event['discounts'][
                'iof'] else 0),
        "iof": 0,
        "financed_amount": round(financed_amount, 2),
        "liquid_amount": request_amount,
        "cet_year": round(cet_year * 100, 2),
        "cet": round(cet * 100, 2),
        "installments": [{
            "due_date": payment_matrix[npar][0],
            "amount": "{:.2f}".format(payment_matrix[npar][2])
        } for npar in range(terms)],
        "amount_total": round(current_value, 2)
    }

    for key in report['discounts']:
        report['discounts'][key]['financed'] = True
        report['discounts'][key]['PV'] = True
        report['discounts'][key]['base'] = 'fianced_amount' if key == 'iof' else 'amount'
        report['discounts'][key]['baseValue'] = request_amount if key == 'iof' else financed_amount
        report['discounts'][key]['value'] = round((float(
            report['discounts'][key]['percent']) * request_amount / 100 if 'percent' in report['discounts'][
            key] else 0), 2)

    return json.loads(json.dumps(report))