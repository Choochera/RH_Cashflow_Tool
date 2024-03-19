import robin_stocks.robinhood as rh
import os

try:
    rh.login(
        username=os.environ.get("robinhood_username"),  # Username
        password=os.environ.get("robinhood_password"),  # Password
        expiresIn=86400,  # Time until login expiration
        store_session=True  # Save login authorization
    )
except Exception as ex:
    print("RH client failed to login with given credentials due to %s" % ex)


async def get_all_option_orders():
    return rh.get_all_option_orders()


async def get_all_stock_orders():
    return rh.get_all_stock_orders()


async def get_all_crypto_orders():
    return rh.get_all_crypto_orders()


async def get_all_dividends():
    return rh.get_dividends()


async def get_option_events():
    return rh.request_get(
        'https://api.robinhood.com/options/events/?account_numbers=543840045&page_size=10',
        dataType='pagination',
        jsonify_data=True)


async def get_bank_transfer():
    return rh.request_get(
        'https://bonfire.robinhood.com/paymenthub/unified_transfers/?entity_type=rhs_account&page_size=10',
        dataType='pagination',
        jsonify_data=True)
