import time
import Bitstamp
import Botlog
import Order

# setup output file
l = Botlog.Botlog()

# bot config
pair = 'btcusd'
scrum = 2
qty = 0.2
depth = 5
buy_down_interval = 0.002
profit_interval = 0.004
straddle = profit_interval + buy_down_interval
running = True
ob = Order.Orderbook()
order_depth = 0
last_order = ''
last_price = 0.00
current_price = 0.00
parity_balance = 1.0

# wallet setup
btc = Order.Coin(Order.Currency.BTC, 8400.00)
usd = Order.Coin(Order.Currency.USD, 1.00)
w = Order.Wallet()
w.add_coin(btc)
w.add_coin(usd)
w.add_balance(btc, 1)
w.add_balance(usd, 8400)

# instantiate bitstamp service
bitstamp = Bitstamp.BitstampService()


def opening_orders():

    global ob
    global pair
    global depth
    global scrum

    bought_in = False

    l.log_action("Placing opening orders\n")

    while not bought_in:

        time.sleep(1)
        l.log_action("Bids:")

        bids = bitstamp.get_bids(pair, depth)
        for b in bids:
            l.log_action("\t\tbids: %s, amount: %s" % (b[0], b[1]))

        buy_price = float(bids[scrum][0])

        l.log_action("Asks:")

        asks = bitstamp.get_asks(pair, depth)
        for a in asks:
            l.log_action("\t\tasks: %s, amount: %s" % (a[0], a[1]))

        sell_price = float(asks[scrum][0])

        l.log_action("Current: %.4f" % sell_price)

        cur_price = bitstamp.get_price(pair)

        if cur_price - buy_price > 5 and sell_price - cur_price > 5:
            buy_order = Order.Order(Order.Ordertype.OB, buy_price, qty)
            ob.add_order(buy_order)
            sell_order = Order.Order(Order.Ordertype.OS, sell_price, qty)
            ob.add_order(sell_order)
            bought_in = True

opening_orders()


def get_orders():
    for o in ob.orders:
        l.log_action(o)


def check_orders():

    global last_price
    global current_price

    log = ''

    last_price = current_price
    current_price = bitstamp.get_price(pair)

    btc.update(current_price)

    log += "%.4f" % current_price
    log += ','

    if current_price != last_price:
        l.log_action("Current price:\t%.4f" % current_price)

    for o in ob.orders:

        log += str(o.id)
        log += ';'
        log += "%.4f" % o.price
        log += ','

        if o.type == Order.Ordertype.OB or o.type == Order.Ordertype.BDI or o.type == Order.Ordertype.BPI:

            if current_price <= o.price:
                o.execute()

        elif o.type == Order.Ordertype.OS or o.type == Order.Ordertype.SDI or o.type == Order.Ordertype.SPI:

            if current_price >= o.price:
                o.execute()

    l.log_data(log)

    return current_price


def order_event_handler(price):

    global order_depth
    global last_order

    for o in ob.orders:

        if o.status == Order.OrderStatus.EXECUTED:

            if o.type == Order.Ordertype.OB:

                order_depth += 1
                last_order = 'OB'

                w.add_balance(btc, qty)
                w.sub_balance(usd, qty * o.price)

                # cancel opening sell, no longer required.

                l.log_action("Cancelling opening SELL, no longer required.")

                for oo in ob.orders:

                    if oo.type == Order.Ordertype.OS:

                        oo.cancel()

                # place buy down interval order

                l.log_action("Placing BUY at down interval.")

                ob.add_order(Order.Order(Order.Ordertype.BDI, price - (price * (buy_down_interval * order_depth)), qty))

                # place sell at profit interval

                l.log_action("Placing SELL at profit interval.")

                ob.add_order(Order.Order(Order.Ordertype.SPI, price + (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.OS:

                order_depth += 1
                last_order = 'OS'

                w.sub_balance(btc, qty)
                w.add_balance(usd, qty * o.price)

                # cancel opening buy, no longer required.

                l.log_action("Cancelling opening BUY, no longer required.")

                for oo in ob.orders:

                    if oo.type == Order.Ordertype.OB:

                        oo.cancel()

                # place sell down interval order

                l.log_action("Placing SELL at down interval.")

                ob.add_order(Order.Order(Order.Ordertype.SDI, price + (price * (buy_down_interval * order_depth)), qty))

                # place buy at profit interval

                l.log_action("Placing BUY at profit interval.")

                ob.add_order(Order.Order(Order.Ordertype.BPI, price - (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.BDI:

                w.add_balance(btc, qty)
                w.sub_balance(usd, qty * o.price)

                order_depth += 1

                last_order = 'BDI'

                # place buy down interval order

                l.log_action("Placing BUY at down interval.")

                ob.add_order(Order.Order(Order.Ordertype.BDI, price - (price * (buy_down_interval * order_depth)), qty))

                # place sell at profit interval

                l.log_action("Placing SELL at profit interval.")

                ob.add_order(Order.Order(Order.Ordertype.SPI, price + (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.SDI:

                w.sub_balance(btc, qty)
                w.add_balance(usd, qty * o.price)

                order_depth += 1

                last_order = 'SDI'

                # place sell down interval order

                l.log_action("Placing SELL at down interval.")

                ob.add_order(Order.Order(Order.Ordertype.SDI, price + (price * (buy_down_interval * order_depth)), qty))

                # place buy at profit interval

                l.log_action("Placing BUY at profit interval.")

                ob.add_order(Order.Order(Order.Ordertype.BPI, price - (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.BPI:

                w.add_balance(btc, qty)
                w.sub_balance(usd, qty * o.price)

                if w.get_balance(btc) == parity_balance:
                    order_depth = 0
                    ob.cancel_all_orders()
                    opening_orders()

                elif last_order == 'OS' or last_order == 'SPI':

                    # redundant? vs. parity reset?

                    order_depth -= 1

                    for oo in ob.orders[::-1]:

                        if oo.type == Order.Ordertype.SDI:
                            oo.cancel()
                            break

                    # place buy down interval order

                    l.log_action("Placing BUY at down interval.")

                    ob.add_order(Order.Order(Order.Ordertype.BDI, price - (price * (buy_down_interval * order_depth)), qty))

                    # place sell at profit interval

                    l.log_action("Placing SELL at profit interval.")

                    ob.add_order(Order.Order(Order.Ordertype.SPI, price + (price * profit_interval), qty))

                    get_orders()

                elif last_order == 'SDI':

                    order_depth -= 1

                    # previous buy exists

                    # cancel outer SDI with SPI

                    for oo in ob.orders[::-1]:

                        if oo.type == Order.Ordertype.SDI:
                            oo.cancel()
                            break

                    l.log_action("Cancelling outer SDI.")
                    l.log_action("Placing SDI+ at profit interval.")

                    ob.add_order(Order.Order(Order.Ordertype.SDI, price + (price * profit_interval), qty))

                last_order = 'BPI'

            elif o.type == Order.Ordertype.SPI:

                w.sub_balance(btc, qty)
                w.add_balance(usd, qty * o.price)

                if w.get_balance(btc) == parity_balance:
                    order_depth = 0
                    ob.cancel_all_orders()
                    opening_orders()

                elif last_order == 'OB' or last_order == 'BPI':

                    order_depth -= 1

                    for oo in ob.orders[::-1]:

                        if oo.type == Order.Ordertype.BDI:
                            oo.cancel()
                            break

                    # place sell down interval order

                    l.log_action("Placing SELL at down interval.")

                    ob.add_order(Order.Order(Order.Ordertype.SDI, price + (price * (buy_down_interval * order_depth)), qty))

                    # place buy at profit interval

                    l.log_action("Placing BUY at profit interval.")

                    ob.add_order(Order.Order(Order.Ordertype.BPI, price - (price * profit_interval), qty))

                    get_orders()

                elif last_order == 'SDI':

                    order_depth -= 1

                    # previous sell exists

                    # cancel outer BDI with BPI

                    for oo in ob.orders[::-1]:

                        if oo.type == Order.Ordertype.BDI:
                            oo.cancel()
                            break

                    l.log_action("Cancelling outer BDI.")
                    l.log_action("Placing BDI+ at profit interval.")

                    ob.add_order(Order.Order(Order.Ordertype.BDI, price - (price * profit_interval), qty))

                last_order = 'SPI'


def clean_order_book():

    ob.remove_cancelled_orders()
    ob.remove_executed_orders()

# Stage 2 - main loop

l.log_action("Starting main processing...\n")
get_orders()

counter = 1

while running:

    counter += 1

    time.sleep(1)
    order_event_handler(check_orders())
    clean_order_book()

    if counter % 20 == 0:
        print(w)
        print(ob)
