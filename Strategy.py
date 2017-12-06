import time
import datetime
import Bitstamp
import Botlog
import Order


class BitstampStrategy:
    def __init__(self, service, order_book, wallet, pair, logger):
        raise NotImplementedError

    def execute(self, *args, **kwargs):
        raise NotImplementedError


class BitstampMarketMaker:
    def __init__(self, service, order_book, wallet, pair, logger):
        self._service = service
        self._order_book = order_book
        self._wallet = wallet
        self._pair = pair
        self._logger = logger

        self._running = False
        self._last_price = 0.0
        self._current_price = 0.0
        self._depth = 5
        self._scrum = 2
        self._order_depth = 0
        self._last_order = ''
        self._qty = 0.2
        self._buy_down_interval = 0.002
        self._profit_interval = 0.004
        self._straddle = self._buy_down_interval + self._profit_interval
        self._parity_balance = 1.0


    def execute(self):
        self._logger.log_action("Starting main processing...\n")
        self._running = True

        self._opening_orders()

        self._get_orders()

        counter = 0

        while self._running:
            if counter % 20 == 0:
                print(self._wallet)
                print(self._order_book)

            time.sleep(0.5)
            self._order_event_handler(self._check_orders())
            self._clean_order_book()

            counter += 1


    def _get_orders(self):
        for order in self._order_book.orders:
            self._logger.log_action(order)


    def _check_orders(self):
        log = ''

        self._last_price = self._current_price
        self._current_price = self._service.get_price(self._pair)

        self._wallet.set_price_usd(Order.Currency.BTC, self._current_price)

        #if self._current_price != self._last_price:
        #    self._logger.log_action("Current price:\t%.4f" % self._current_price)

        for order in self._order_book.orders:

            if order.type in {Order.Ordertype.OB, Order.Ordertype.BDI, Order.Ordertype.BPI}:
                if self._current_price <= order.price:
                    order.execute()

            if order.type in {Order.Ordertype.OS, Order.Ordertype.SDI, Order.Ordertype.SPI}:
                if self._current_price >= order.price:
                    order.execute()

        # data log

        log += "%.4f" % self._current_price
        log += ','

        max_oid = max([o.id for o in self._order_book.orders])

        for x in range(1, max_oid + 1):
            found = False
            for o in self._order_book.orders:
                if o.id == x:
                    log += str(o.id)
                    log += ';'
                    log += "%.4f" % o.price
                    log += ','
                    found = True
                    break

            if not found:
                log += str(x)
                log += ';'
                log += ','

        self._logger.log_data(log)

        return self._current_price

    def _clean_order_book(self):
        self._order_book.remove_cancelled_orders()
        self._order_book.remove_executed_orders()

    def _order_event_handler(self, price):
        for order in self._order_book.orders:
            if order.status == Order.OrderStatus.EXECUTED:
                if order.type == Order.Ordertype.OB:
                    self._order_depth += 1
                    self._last_order = 'OB'  # TODO: use enums

                    self._wallet.add_balance(Order.Currency.BTC, self._qty)  # TODO: also enums?
                    self._wallet.sub_balance(Order.Currency.USD, self._qty * order.price)

                    # cancel opening sell, no longer required.

                    self._logger.log_action("Cancelling opening SELL, no longer required.")

                    for sub_order in self._order_book.orders:
                        if sub_order.type == Order.Ordertype.OS:
                            sub_order.cancel()

                    # place buy down interval order

                    self._logger.log_action("Placing BUY at down interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.BDI,
                            price - (price * (self._buy_down_interval * self._order_depth)),
                            self._qty))

                    # place buy at profit interval

                    self._logger.log_action("Placing SELL at profit interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.SPI,
                            price + (price * self._profit_interval),
                            self._qty))

                    self._get_orders()

                elif order.type == Order.Ordertype.OS:
                    self._order_depth += 1
                    self._last_order = 'OS'

                    self._wallet.sub_balance(Order.Currency.BTC, self._qty)
                    self._wallet.add_balance(Order.Currency.USD, self._qty * order.price)

                    # cancel opening buy, no longer required.

                    self._logger.log_action("Cancelling opening BUY, no longer required.")

                    for sub_order in self._order_book.orders:

                        if sub_order.type == Order.Ordertype.OB:

                            sub_order.cancel()

                    # place sell down interval order

                    self._logger.log_action("Placing SELL at down interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.SDI,
                            price + (price * (self._buy_down_interval * self._order_depth)),
                            self._qty))

                    # place buy at profit interval

                    self._logger.log_action("Placing BUY at profit interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.BPI,
                            price - (price * self._profit_interval),
                            self._qty))

                    self._get_orders()

                elif order.type == Order.Ordertype.BDI:
                    self._wallet.add_balance(Order.Currency.BTC, self._qty)
                    self._wallet.sub_balance(Order.Currency.USD, self._qty * order.price)

                    self._order_depth += 1

                    self._last_order = 'BDI'

                    # place buy down interval order

                    self._logger.log_action("Placing BUY at down interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.BDI,
                            price - (price * (self._buy_down_interval * self._order_depth)),
                            self._qty))

                    # place sell at profit interval

                    self._logger.log_action("Placing SELL at profit interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.SPI,
                            price + (price * self._profit_interval),
                            self._qty))

                    self._get_orders()

                elif order.type == Order.Ordertype.SDI:
                    self._wallet.sub_balance(Order.Currency.BTC, self._qty)
                    self._wallet.add_balance(Order.Currency.USD, self._qty * order.price)

                    self._order_depth += 1

                    self._last_order = 'SDI'

                    # place sell down interval order

                    self._logger.log_action("Placing SELL at down interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.SDI,
                            price + (price * (self._buy_down_interval * self._order_depth)),
                            self._qty))

                    # place buy at profit interval

                    self._logger.log_action("Placing BUY at profit interval.")

                    self._order_book.add_order(
                        Order.Order(
                            Order.Ordertype.BPI,
                            price - (price * self._profit_interval),
                            self._qty))

                    self._get_orders()

                elif order.type == Order.Ordertype.BPI:

                    self._wallet.add_balance(Order.Currency.BTC, self._qty)
                    self._wallet.sub_balance(Order.Currency.USD, self._qty * order.price)

                    if self._wallet.get_balance(Order.Currency.BTC) == self._parity_balance:
                        self._order_depth = 0
                        self._order_book.cancel_all_orders()
                        self._opening_orders()

                    elif self._last_order in {'OS', 'SPI'}:

                        # redundant? vs. parity reset?

                        self._order_depth -= 1

                        for sub_order in self._order_book.orders[::-1]:

                            if sub_order.type == Order.Ordertype.SDI:
                                sub_order.cancel()
                                break

                        # place buy down interval order

                        self._logger.log_action("Placing BUY at down interval.")

                        self._order_book.add_order(
                            Order.Order(
                                Order.Ordertype.BDI,
                                price - (price * (self._buy_down_interval * self._order_depth)),
                                self._qty))

                        # place sell at profit interval

                        self._logger.log_action("Placing SELL at profit interval.")

                        self._order_book.add_order(
                            Order.Order(
                                Order.Ordertype.SPI,
                                price + (price * self._profit_interval),
                                self._qty))

                        self._get_orders()

                    elif self._last_order in {'SDI', 'BPI'}:

                        self._order_depth -= 1

                        # previous buy exists

                        # cancel outer SDI with SPI

                        for sub_order in self._order_book.orders[::-1]:

                            if sub_order.type == Order.Ordertype.SDI:
                                sub_order.cancel()
                                break

                        self._logger.log_action("Cancelling outer SDI.")
                        self._logger.log_action("Placing SDI+ at profit interval.")

                        self._order_book.add_order(
                            Order.Order(
                                Order.Ordertype.SDI,
                                price + (price * self._profit_interval),
                                self._qty))

                    self._last_order = 'BPI'

                elif order.type == Order.Ordertype.SPI:

                    self._wallet.sub_balance(Order.Currency.BTC, self._qty)
                    self._wallet.add_balance(Order.Currency.USD, self._qty * order.price)

                    if self._wallet.get_balance(Order.Currency.BTC) == self._parity_balance:
                        self._order_depth = 0
                        self._order_book.cancel_all_orders()
                        self._opening_orders()

                    elif self._last_order in {'OB', 'BPI'}:

                        self._order_depth -= 1

                        for sub_order in self._order_book.orders[::-1]:

                            if sub_order.type == Order.Ordertype.BDI:
                                sub_order.cancel()
                                break

                        # place sell down interval order

                        self._logger.log_action("Placing SELL at down interval.")

                        self._order_book.add_order(
                            Order.Order(
                                Order.Ordertype.SDI,
                                price + (price * (self._buy_down_interval * self._order_depth)),
                                self._qty))

                        # place buy at profit interval

                        self._logger.log_action("Placing BUY at profit interval.")

                        self._order_book.add_order(
                            Order.Order(
                                Order.Ordertype.BPI,
                                price - (price * self._profit_interval),
                                self._qty))

                        self._get_orders()

                    elif self._last_order in {'SDI', 'SPI'}:

                        self._order_depth -= 1

                        # previous sell exists

                        # cancel outer BDI with BPI

                        for sub_order in self._order_book.orders[::-1]:

                            if sub_order.type == Order.Ordertype.BDI:
                                sub_order.cancel()
                                break

                        self._logger.log_action("Cancelling outer BDI.")
                        self._logger.log_action("Placing BDI+ at profit interval.")

                        self._order_book.add_order(
                            Order.Order(
                                Order.Ordertype.BDI,
                                price - (price * self._profit_interval),
                                self._qty))

                    self._last_order = 'SPI'

    def _opening_orders(self):
        bought_in = False

        self._logger.log_action("Placing opening orders\n")

        while not bought_in:

            time.sleep(0.5)
            self._logger.log_action("Bids:")

            bids = self._service.get_bids(self._pair, self._depth)
            for bid in bids:
                self._logger.log_action("\t\tbids: %s, amount: %s" % (bid[0], bid[1]))

            buy_price = float(bids[self._scrum][0])

            self._logger.log_action("Asks:")

            asks = self._service.get_asks(self._pair, self._depth)
            for ask in asks:
                self._logger.log_action("\t\tasks: %s, amount: %s" % (ask[0], ask[1]))

            sell_price = float(asks[self._scrum][0])

            self._logger.log_action("Current: %.4f" % sell_price)

            cur_price = self._service.get_price(self._pair)

            if cur_price - buy_price > 5 and sell_price - cur_price > 5:
                buy_order = Order.Order(Order.Ordertype.OB, buy_price, self._qty)
                self._order_book.add_order(buy_order)
                sell_order = Order.Order(Order.Ordertype.OS, sell_price, self._qty)
                self._order_book.add_order(sell_order)
                bought_in = True
