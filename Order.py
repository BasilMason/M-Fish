from enum import Enum


class Order:

    id = 0
    type = ''
    price = 0.00
    qty = 0.00
    status = 'NEW'

    def __init__(self, id, type, price, qty):
        self.id = id
        self.type = type
        self.price = price
        self.qty = qty

        print("%s order %d placed for %.4f @ %.4f, status: %s" % (self.type.value, self.id, self.qty, self.price, self.status))

    def __str__(self):
        return "%s order %d for %.4f @ %.4f, status: %s" % (self.type.value, self.id, self.qty, self.price, self.status)


class Ordertype(Enum):
    OB = 'OB'
    OS = 'OS'
    BDI = 'BDI'
    SDI = 'SDI'
    BPI = 'BPI'
    SPI = 'SPI'


class Orderbook:

    orders = []
    buy_count = 0
    sell_count = 0

    def __init__(self):
        pass

    def add_order(self, order):
        order.status = 'OPEN'

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

            if o.status == 'CANCELLED':

                if o.type == Ordertype.OB or o.type == Ordertype.BDI or o.type == Ordertype.BPI:
                    self.buy_count -= 1
                elif o.type == Ordertype.OS or o.type == Ordertype.SDI or o.type == Ordertype.SPI:
                    self.sell_count -= 1

        self.orders = [o for o in self.orders if not o.status == 'CANCELLED']

    def remove_executed_orders(self):

        for o in self.orders:

            if o.status == 'EXECUTED':

                if o.type == Ordertype.OB or o.type == Ordertype.BDI or o.type == Ordertype.BPI:
                    self.buy_count -= 1
                elif o.type == Ordertype.OS or o.type == Ordertype.SDI or o.type == Ordertype.SPI:
                    self.sell_count -= 1

        self.orders = [o for o in self.orders if not o.status == 'EXECUTED']


class OrderIdentifer:

    id_gen = 1

    def __init__(self):
        pass

    def next_id(self):
        self.id_gen += 1
        return self.id_gen