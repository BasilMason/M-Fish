import time
import datetime
import Bitstamp
import Order

# setup output file
t = int(time.time())
d = datetime.datetime.today().strftime('%Y-%m-%d')
p = "Logs\Fishlog-%s-%s.txt" % (d,t)
f = open(p,'w')

# bot config
pair = 'btcusd'
scrum = 2
qty = 1.0
depth = 5
interval = 0.005
buy_down_interval = 0.003
profit_interval = 0.005
straddle = profit_interval + buy_down_interval
running = True
og = Order.OrderIdentifer()
ob = Order.Orderbook()


def output_to_log(s):
    print(s)
    f = open(p, 'a')
    f.write(">> %s\n" % s)
    f.close()


# bot intro
intro = '----------------------------------------------------------------------------\n'\
        '*  __  __     ___ _    _     // / /, // ,/, /, // ,/// / /, // ,/, /, // ,/*\n'\
        '* |  \/  |___| __(_)__| |_   ,, ,/, // ,/ /, //, /,/,, ,/, // ,/ /, //, /,/*\n'\
        '* | |\/| |___| _|| (_-< \' \  / ////, // ,/,/, // ///// ///  /,,/,/, ///, //*\n'\
        '* |_|  |_|   |_| |_/__/_||_| / ,,///, // ,/,/, // , / ////, // ,/,/, // ///*\n'\
        '*                            // ///  /,,/,/, ///, //, // ,/, //, ///, // ,/*\n'\
        '*--------------PREDICT RAIN. , // ,/, //, ///, // ,/// ///  /,,/,/, ///, //*\n'

f.write("%s\n" % intro)
f.write("Log generated on %s at %s\n" % (d,time.strftime('%H:%M:%S', time.localtime())))
f.close()

# Stage 1 - opening orders

output_to_log("Placing opening orders\n")
output_to_log("Bids:")

bids = Bitstamp.get_bids(pair, depth)
for b in bids:
    output_to_log("\t\tbids: %s, amount: %s" % (b[0], b[1]))

buy_price = float(bids[scrum][0])
buy_order = Order.Order(og.next_id(), Order.Ordertype.OB, buy_price, qty)
ob.add_order(buy_order)

output_to_log("Asks:")

asks = Bitstamp.get_asks(pair, depth)
for a in asks:
    output_to_log("\t\tasks: %s, amount: %s" % (a[0], a[1]))

sell_price = float(asks[scrum][0])
sell_order = Order.Order(og.next_id(), Order.Ordertype.OS, sell_price, qty)
ob.add_order(sell_order)


def get_orders():
    for o in ob.orders:
        output_to_log(o)


def check_orders():

    output_to_log("Checking order statuses.")

    price = float(Bitstamp.get_price(pair))

    output_to_log("Current price:\t%.4f" % price)

    for o in ob.orders:

        if o.type == Order.Ordertype.OB or o.type == Order.Ordertype.BDI or o.type == Order.Ordertype.BPI:

            if price <= o.price:
                o.status = 'EXECUTED'
                output_to_log(str(o))

        elif o.type == Order.Ordertype.OS or o.type == Order.Ordertype.SDI or o.type == Order.Ordertype.SPI:

            if price >= o.price:
                o.status = 'EXECUTED'
                output_to_log(str(o))

    return price


def order_event_handler(price):

    output_to_log("Handling order events.")

    for o in ob.orders:

        if o.status == 'EXECUTED':

            if o.type == Order.Ordertype.OB:

                # cancel opening sell, no longer required.

                output_to_log("Cancelling opening SELL, no longer required.")

                for oo in ob.orders:

                    if oo.type == Order.Ordertype.OS:

                        oo.status = 'CANCELLED'

                # place buy down interval order

                output_to_log("Placing BUY at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BDI, price - (price * (buy_down_interval * ob.buy_count)), qty))

                # place sell at profit interval

                output_to_log("Placing SELL at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SPI, price + (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.OS:

                # cancel opening buy, no longer required.

                output_to_log("Cancelling opening BUY, no longer required.")

                for oo in ob.orders:

                    if oo.type == Order.Ordertype.OB:

                        oo.status = 'CANCELLED'

                # place sell down interval order

                output_to_log("Placing SELL at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SDI, price + (price * (buy_down_interval * ob.sell_count)), qty))

                # place buy at profit interval

                output_to_log("Placing BUY at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BPI, price - (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.BDI:

                # place buy down interval order

                output_to_log("Placing BUY at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BDI, price - (price * (buy_down_interval * ob.buy_count)), qty))

                # place sell at profit interval

                output_to_log("Placing SELL at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SPI, price + (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.SDI:

                # place sell down interval order

                output_to_log("Placing SELL at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SDI, price + (price * (buy_down_interval * ob.sell_count)), qty))

                # place buy at profit interval

                output_to_log("Placing BUY at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BPI, price - (price * profit_interval), qty))

                get_orders()


def clean_order_book():

    ob.remove_cancelled_orders()
    ob.remove_executed_orders()

# Stage 2 - main loop

output_to_log("Starting main processing...\n")
get_orders()

while running:

    time.sleep(1)
    order_event_handler(check_orders())
    clean_order_book()