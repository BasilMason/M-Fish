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

        print(str(self))

    @property
    def status(self):
        return self._status

    def open(self):
        self._status = OrderStatus.OPEN
        print(str(self))

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
p
        self.orders = [o for o in self.orders if not o.status == OrderStatus.EXECUTED]


