import time
import datetime
import Bitstamp
import Order

# setup output file
t = int(time.time())
d = datetime.datetime.today().strftime('%Y-%m-%d')
action_log = "Logs\Actionlog-%s-%s.txt" % (d,t)
data_log = "Logs\Datalog-%s-%s.txt" % (d,t)
fa = open(action_log,'w')
fd = open(data_log,'w')

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
order_depth = 0
last_order = ''


def output_to_log(s):
    print(s)
    f = open(action_log, 'a')
    f.write(">> %s\n" % s)
    f.close()


def output_data(s):
    f = open(data_log, 'a')
    f.write("%s\n" % s)
    f.close()


# bot intro
intro = '----------------------------------------------------------------------------\n'\
        '*  __  __     ___ _    _     // / /, // ,/, /, // ,/// / /, // ,/, /, // ,/*\n'\
        '* |  \/  |___| __(_)__| |_   ,, ,/, // ,/ /, //, /,/,, ,/, // ,/ /, //, /,/*\n'\
        '* | |\/| |___| _|| (_-< \' \  / ////, // ,/,/, // ///// ///  /,,/,/, ///, //*\n'\
        '* |_|  |_|   |_| |_/__/_||_| / ,,///, // ,/,/, // , / ////, // ,/,/, // ///*\n'\
        '*                            // ///  /,,/,/, ///, //, // ,/, //, ///, // ,/*\n'\
        '*--------------PREDICT RAIN. , // ,/, //, ///, // ,/// ///  /,,/,/, ///, //*\n'

fa.write("%s\n" % intro)
fa.write("Action Log generated on %s at %s\n" % (d,time.strftime('%H:%M:%S', time.localtime())))
fa.close()

fd.write("%s\n" % intro)
fd.write("Data Log generated on %s at %s\n" % (d,time.strftime('%H:%M:%S', time.localtime())))
fd.close()

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

    log = ''

    output_to_log("Checking order statuses.")

    price = float(Bitstamp.get_price(pair))

    log += "%.4f" % price
    log += ','

    output_to_log("Current price:\t%.4f" % price)

    for o in ob.orders:

        log += str(o.id)
        log += ';'
        log += "%.4f" % o.price
        log += ','

        if o.type == Order.Ordertype.OB or o.type == Order.Ordertype.BDI or o.type == Order.Ordertype.BPI:

            if price <= o.price:
                o.status = 'EXECUTED'
                output_to_log(str(o))

        elif o.type == Order.Ordertype.OS or o.type == Order.Ordertype.SDI or o.type == Order.Ordertype.SPI:

            if price >= o.price:
                o.status = 'EXECUTED'
                output_to_log(str(o))

    output_data(log)

    return price


def order_event_handler(price):

    global order_depth
    global last_order

    output_to_log("Handling order events.")

    for o in ob.orders:

        if o.status == 'EXECUTED':

            if o.type == Order.Ordertype.OB:

                order_depth += 1
                last_order = 'BUY'

                # cancel opening sell, no longer required.

                output_to_log("Cancelling opening SELL, no longer required.")

                for oo in ob.orders:

                    if oo.type == Order.Ordertype.OS:

                        oo.status = 'CANCELLED'

                # place buy down interval order

                output_to_log("Placing BUY at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BDI, price - (price * (buy_down_interval * order_depth)), qty))

                # place sell at profit interval

                output_to_log("Placing SELL at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SPI, price + (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.OS:

                order_depth += 1
                last_order = 'SELL'

                # cancel opening buy, no longer required.

                output_to_log("Cancelling opening BUY, no longer required.")

                for oo in ob.orders:

                    if oo.type == Order.Ordertype.OB:

                        oo.status = 'CANCELLED'

                # place sell down interval order

                output_to_log("Placing SELL at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SDI, price + (price * (buy_down_interval * order_depth)), qty))

                # place buy at profit interval

                output_to_log("Placing BUY at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BPI, price - (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.BDI:

                if last_order == 'BUY':
                    order_depth += 1
                elif last_order == 'SELL':
                    order_depth -= 1

                last_order = 'BUY'

                # place buy down interval order

                output_to_log("Placing BUY at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BDI, price - (price * (buy_down_interval * order_depth)), qty))

                # place sell at profit interval

                output_to_log("Placing SELL at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SPI, price + (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.SDI:

                if last_order == 'SELL':
                    order_depth += 1
                elif last_order == 'BUY':
                    order_depth -= 1

                last_order = 'SELL'

                # place sell down interval order

                output_to_log("Placing SELL at down interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SDI, price + (price * (buy_down_interval * order_depth)), qty))

                # place buy at profit interval

                output_to_log("Placing BUY at profit interval.")

                ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BPI, price - (price * profit_interval), qty))

                get_orders()

            elif o.type == Order.Ordertype.BPI:

                last_order = 'BUY'

                if order_depth == 1:

                    # place buy down interval order

                    output_to_log("Placing BUY at down interval.")

                    ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BDI, price - (price * (buy_down_interval * order_depth)), qty))

                    # place sell at profit interval

                    output_to_log("Placing SELL at profit interval.")

                    ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SPI, price + (price * profit_interval), qty))

                    get_orders()

                elif order_depth > 1:

                    # previous buy exists

                    # cancel outer SDI with SPI

                    ob.orders[-1].status = 'CANCELLED'

                    output_to_log("Cancelling outer SDI.")
                    output_to_log("Placing SELL at profit interval.")

                    ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SPI, price - (price * profit_interval), qty))

            elif o.type == Order.Ordertype.SPI:

                last_order = 'SELL'

                if order_depth == 1:

                    # place sell down interval order

                    output_to_log("Placing SELL at down interval.")

                    ob.add_order(Order.Order(og.next_id(), Order.Ordertype.SDI, price + (price * (buy_down_interval * order_depth)), qty))

                    # place buy at profit interval

                    output_to_log("Placing BUY at profit interval.")

                    ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BPI, price - (price * profit_interval), qty))

                    get_orders()

                elif order_depth > 1:

                    # previous sell exists

                    # cancel outer BDI with BPI

                    ob.orders[-1].status = 'CANCELLED'

                    output_to_log("Cancelling outer BDI.")
                    output_to_log("Placing BUY at profit interval.")

                    ob.add_order(Order.Order(og.next_id(), Order.Ordertype.BPI, price - (price * profit_interval), qty))


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