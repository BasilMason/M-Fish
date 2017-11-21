import hmac
import hashlib
import time

import settings

import requests



class BitstampService:
    def _url_order_book(self, pair):
        return 'https://www.bitstamp.net/api/v2/order_book/' + pair + '/'

    def _url_price(self, pair):
        return 'https://www.bitstamp.net/api/v2/ticker/' + pair + '/'

    def get_bids(self, pair, depth):
        url = self._url_order_book(pair)
        resp = requests.get(url).json()
        return resp['bids'][:depth]

    def get_asks(self, pair, depth):
        url = self._url_order_book(pair)
        resp = requests.get(url).json()
        return resp['asks'][:depth]

    def get_price(self, pair):
        url = self._url_price(pair)
        resp = requests.get(url).json()
        return float(resp['last'])


# authentication
customer_id = settings.BITSTAMP_CUSTOMER_ID
api_key = settings.BITSTAMP_API_KEY
api_secret = settings.BITSTAMP_API_SECRET
nonce = int(time.time())

def generate_signature():
    message = str(nonce).encode() + customer_id.encode() + api_key.encode()
    signature = hmac.new(
        api_secret.encode(),
        msg=message,
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    return signature

values = {'key' : api_key,
          'signature' : generate_signature(),
          'nonce' : nonce}

# bitstamp
pairs = ['btcusd', 'btceur', 'eurusd', 'xrpusd', 'xrpeur', 'xrpbtc', 'ltcusd'
        , 'ltceur', 'ltcbtc', 'ethusd', 'etheur', 'ethbtc']

# get urls
url_trading_pairs = 'https://www.bitstamp.net/api/v2/trading-pairs-info/'





# post urls
url_balance_all = 'https://www.bitstamp.net/api/v2/balance/'
url_balance_pair = 'https://www.bitstamp.net/api/v2/balance/' + pairs[5] + '/'
url_open_orders_all = 'https://www.bitstamp.net/api/v2/open_orders/all/'
url_open_orders_pair = 'https://www.bitstamp.net/api/v2/open_orders/' + pairs[5] + '/'
url_cancel_orders_all = 'https://www.bitstamp.net/api/cancel_all_orders/'
url_cancel_order = 'https://www.bitstamp.net/api/v2/cancel_order/'
url_order_status = 'https://www.bitstamp.net/api/order_status/'


def url_buy_limit_order(pair):
    return 'https://www.bitstamp.net/api/v2/buy/' + pair + '/'


def url_sell_limit_order(pair):
    return 'https://www.bitstamp.net/api/v2/sell/' + pair + '/'

# post values
values_balance = {'key' : api_key, 'signature' : generate_signature(), 'nonce' : nonce}


def values_order(order_id):
    return {'key' : api_key, 'signature' : generate_signature(), 'nonce' : nonce, 'id' : order_id}


def values_order_limit(amount, price, limit_price):
    return {'key' : api_key, 'signature' : generate_signature(), 'nonce' : nonce, 'amount' : amount
            , 'price' : price, 'limit_price' : limit_price}


def get_url(url):
    data = requests.get(url).json()

    return data


def post_url(url, values):
    data = requests.get(url, params=values).json()

    return data


def show_bids(pair, qty):
    url = url_order_book(pair)
    resp = get_url(url)
    bids = resp['bids'][:qty]
    for b in bids:
        print("bid: %s, amount: %s" % (b[0], b[1]))


def show_asks(pair, qty):
    url = url_order_book(pair)
    resp = get_url(url)
    asks = resp['asks'][:qty]
    for a in asks:
        print("ask: %s, amount: %s" % (a[0], a[1]))







def place_order():
    url = url_sell_limit_order(pairs[5])
    order = post_url(url, values_order_limit(55,2,1))

    if 'status' in order:
        print("Status: %s, Error: %s" % (order['status'], order['reason']))
    else:
        print("Order: %s" % (order['id']))


def cancel_order(order_id):
    url = url_cancel_order
    order = post_url(url, values_order(order_id))

    if 'error' in order:
        print("Error: %s" % (order['error']))
    else:
        print("Cancelled order: %s" % (order['id']))


def get_order_status(order_id):
    url = url_order_status
    order = post_url(url, values_order(order_id))

    if 'error' in order:
        print("Error: %s" % (order['error']))
    else:
        print("Status: %s" % (order['status']))




def get_price_all(pair):
    url = url_price(pair)
    resp = get_url(url)

    return "%s,%s,%s,%s,%s,%s,%s,%s" % (resp['last'] ,resp['high'], resp['low'], resp['vwap'], resp['volume'], resp['bid'], resp['ask'], resp['open'])


def find_trend(price_list):

    if not price_list:
        print("No prices")
    else:

        macro = ''
        micro = ''

        open_price = price_list[0]
        price = price_list[-1] if len(price_list) > 1 else price_list[0]
        last_price = price_list[-2] if len(price_list) > 2 else price_list[-1]

        if open_price > price:
            macro = 'DOWN'
        elif open_price == price:
            macro = 'FLAT'
        else:
            macro = 'UP'

        if price > last_price:
            micro = 'UP'
        elif price == last_price:
            micro = 'FLAT'
        else:
            micro = 'DOWN'

        print("Micro: %s, Macro: %s" % (micro, macro))
