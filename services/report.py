from datetime import datetime
import pandas as pd


def aggregation(group):
    return group['price']


def generate_cashflow_report(orders_df):
    df = orders_df.reset_index(drop=True)

    df['date'] = pd.to_datetime(df['date'], utc=True, format='ISO8601')
    grouped_data = df.groupby([pd.Grouper(key='date', freq='ME'), 'side'])

    summary_per_month = grouped_data.apply(aggregation)

    indexes = sorted(
        set(map(lambda x: datetime.strptime(str(x[0]), '%Y-%m-%d %H:%M:%S%z'), summary_per_month.index)))

    running_total = 0.0
    data = []
    for index in indexes:
        summary = summary_per_month[index]

        credit = 0.0
        debit = 0.0

        if 'sell' in summary:
            credit = round(summary['sell'].sum(), 2)

        if 'buy' in summary:
            debit = -(round(summary['buy'].sum(), 2))

        net = credit + debit
        running_total = running_total + net
        data.append([index.strftime("%m-%Y"), debit, credit, net, running_total])

    df = pd.DataFrame(data, columns=['Month', 'buy', 'sell', 'net', 'total'])
    df = df.set_index('Month')
    print(df)


def generate_cost_basis_report(transfers):
    deposited = 0.0
    withdrawn = 0.0
    for transfer in transfers:
        if transfer['state'] == 'completed' or transfer['state'] == 'pending':
            details = transfer['details']
            if 'direction' in details:
                match(details['direction']):
                    case 'deposit':
                        deposited = deposited + float(transfer['amount'])
                    case 'withdraw':
                        withdrawn = withdrawn + float(transfer['amount'])

    print('Total deposited: %s' % deposited)
    print('Total withdrawn: %s' % withdrawn)
    print('------------------------------')
    print('Net Cost Basis: %s' % (deposited - withdrawn))
