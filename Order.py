from enum import Enum


class OrderStatus(Enum):
    NEW = 'NEW'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    CANCELLED = 'CANCELLED'
    EXECUTED = 'EXECUTED'


class OrderIdentifer:

    id_gen = 1

    @classmethod
    def next_id(cls):
        cls.id_gen += 1
        return cls.id_gen


class Order:

    def __init__(self, type, price, qty):
        self._status = OrderStatus.NEW
        self.id = OrderIdentifer.next_id()
        self.type = type
        self.price = price
        self.qty = qty

        #print(str(self))

    @property
    def status(self):
        return self._status

    def open(self):
        self._status = OrderStatus.OPEN
        #print(str(self))

    def execute(self):
        self._status = OrderStatus.EXECUTED
        print(str(self))

    def cancel(self):
        self._status = OrderStatus.CANCELLED
        print(str(self))

    def __str__(self):
        return "%s order %d for %.4f @ %.4f, status: %s" % (self.type.value, self.id, self.qty, self.price, self.status.value)


class Ordertype(Enum):
    OB = 'OB'
    OS = 'OS'
    BDI = 'BDI'
    SDI = 'SDI'
    BPI = 'BPI'
    SPI = 'SPI'


class Orderbook:

    def __init__(self):
        self.orders = []
        self.buy_count = 0
        self.sell_count = 0

    def add_order(self, order):
        order.open()

        if order.type == Ordertype.OB or order.type == Ordertype.BDI or order.type == Ordertype.BPI:
            self.buy_count += 1
        elif order.type == Ordertype.OS or order.type == Ordertype.SDI or order.type == Ordertype.SPI:
            self.sell_count += 1

        self.orders.append(order)
 
    def remove_order(self, order):

        if order.type == Ordertype.OB or order.type == Ordertype.BDI or order.type == Ordertype.BPI:
            self.buy_count -= 1
        elif order.type == Ordertype.OS or order.type == Ordertype.SDI or order.type == Ordertype.SPI:
            self.sell_count -= 1

        self.orders.remove(order)

    def remove_cancelled_orders(self):

        for o in self.orders:

            if o.status == OrderStatus.CANCELLED:

                if o.type == Ordertype.OB or o.type == Ordertype.BDI or o.type == Ordertype.BPI:
                    self.buy_count -= 1
                elif o.type == Ordertype.OS or o.type == Ordertype.SDI or o.type == Ordertype.SPI:
                    self.sell_count -= 1

        self.orders = [o for o in self.orders if not o.status == OrderStatus.CANCELLED]

    def remove_executed_orders(self):

        for o in self.orders:

            if o.status == OrderStatus.EXECUTED:

                if o.type == Ordertype.OB or o.type == Ordertype.BDI or o.type == Ordertype.BPI:
                    self.buy_count -= 1
                elif o.type == Ordertype.OS or o.type == Ordertype.SDI or o.type == Ordertype.SPI:
                    self.sell_count -= 1

        self.orders = [o for o in self.orders if not o.status == OrderStatus.EXECUTED]

    def cancel_all_orders(self):
        self.orders = []

    def __str__(self):

        s = "| TYPE\t\t| PRICE\t\t| QTY\t\t| STATUS\t|\n"
        s += "-------------------------------------------------\n"

        for o in self.orders:

            s += "| %s\t\t| %s\t\t| %s\t\t| %s\t\t|\n" % (o.type.value, o.price, o.qty, o.status.value)

        return s


class Currency(Enum):
    USD = 'USD'
    BTC = 'BTC'
    XRP = 'XRP'
    LTC = 'LTC'
    ETH = 'ETH'


class Coin:

    def __init__(self, currency, price):
        self.currency = currency
        self.price = price

    def update(self, price):
        self.price = price

    def __str__(self):
        return "%s : %s" % (self.currency.value, str(self.price))


class Wallet:

    def __init__(self):
        self.wallet = {}

    def add_coin(self, coin):
        self.wallet[coin] = 0.00

    def add_balance(self, coin, qty):
        self.wallet[coin] += qty

    def sub_balance(self, coin, qty):
        self.wallet[coin] -= qty

    def get_balance(self, coin):
        return self.wallet[coin]

    def __str__(self):

        s = "| COIN\t\t| QTY\t\t| PRICE\t\t\t| VALUE\t\t\t|\n"
        s += "------------------------------------------------------\n"

        for k, v in self.wallet.items():

            s += "| %s\t\t| %s\t\t| %s\t\t| %s\t\t|\n" % (k.currency.value, str(v), k.price, v * k.price)

        return s