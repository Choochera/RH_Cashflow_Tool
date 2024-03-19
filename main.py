import pandas as pd
import services.robinhood as rh
import services.report as generator
import asyncio

columns = ['date', 'side', 'price']


async def collect_transaction_data():
    print('Collecting account transaction data...')
    transaction_coroutines = [
        rh.get_all_stock_orders(),
        rh.get_option_events(),
        rh.get_all_option_orders(),
        rh.get_all_crypto_orders(),
        rh.get_all_dividends(),
        rh.get_bank_transfer()
    ]
    transactions = await asyncio.gather(*transaction_coroutines)
    return {
        'stock_orders': transactions[0],
        'option_events': transactions[1],
        'option_orders': transactions[2],
        'crypto_orders': transactions[3],
        'dividends': transactions[4],
        'transfers': transactions[5]
    }


def generate_options_report(all_orders):
    print('\nOption Report\n')
    simplified_orders = []
    for order in all_orders:
        for leg in order['legs']:
            for execution in leg['executions']:
                simplified_orders.append([
                    execution['timestamp'],
                    leg['side'],
                    (float(execution['quantity']) * float(execution['price'])) * 100
                ])
    completed_option_orders = pd.DataFrame(simplified_orders, columns=columns)
    generator.generate_cashflow_report(completed_option_orders)


def generate_stock_report(all_orders, option_events):

    print('\nStock Report\n')
    simplified_orders = []
    for order in all_orders:
        for execution in order['executions']:
            simplified_orders.append([
                execution['timestamp'],
                order['side'],
                float(execution['quantity']) * float(execution['price'])
            ])

    for event in option_events:
        equity_components = event['equity_components']
        for component in equity_components:
            option_event = [
                event['created_at'],
                component['side'],
                float(component['price']) * float(component['quantity'])
            ]
            simplified_orders.append(option_event)

    completed_stock_orders = pd.DataFrame(simplified_orders, columns=columns)
    generator.generate_cashflow_report(completed_stock_orders)


def generate_crypto_report(all_orders):
    print('\nCrypto Report\n')
    simplified_orders = []
    for order in all_orders:
        for execution in order['executions']:
            simplified_orders.append([
                execution['timestamp'],
                order['side'],
                float(execution['quantity']) * float(execution['effective_price'])
            ])
    completed_crypto_orders = pd.DataFrame(simplified_orders, columns=columns)
    generator.generate_cashflow_report(completed_crypto_orders)


def generate_dividends_report(all_dividends):
    dividends_paid = 0.0
    for dividend in all_dividends:
        if dividend['state'] == 'paid':
            dividends_paid = dividends_paid + float(dividend['amount'])

    print('Total dividends received: $%s' % round(dividends_paid, 2))


def generate_cost_basis_report(all_transfers):
    generator.generate_cost_basis_report(all_transfers)


if __name__ == '__main__':
    # RH considers transfers/withdrawals as credits/debits in ALL chart. This is how much you actually have made/lost
    # not considering transfers/RH fees/interest/dividends/cash card expenses

    transaction_map = asyncio.run(collect_transaction_data())
    print('\nData collected successfully! Generating reports...\n')

    generate_stock_report(transaction_map['stock_orders'], transaction_map['option_events'])
    generate_options_report(transaction_map['option_orders'])
    generate_crypto_report(transaction_map['crypto_orders'])
    generate_dividends_report(transaction_map['dividends'])
    generate_cost_basis_report(transaction_map['transfers'])
