from models.Order import Order

class DispatchNode:
    def __init__(self, order:Order):
        self.order = order
        self.next = None
        self.prev = None

class DispatchList:
    def __init__(self):
        self.head:DispatchNode | None = None
        self.tail:DispatchNode | None = None
        self.size = 0

    def is_empty(self):
        return self.size == 0

    def append(self, order:Order):
        new_node = DispatchNode(order)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def find(self, number:int):
        current = self.head
        while current is not None:
            if current.order.number == number:
                return current
            current = current.next
        return None

    def remove(self, number:int) -> bool:
        node = self.find(number)
        if node is None:
            return False
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        self.size -= 1
        return True

    # head to tail
    def to_list(self):
        current = self.head
        orders = []
        while current is not None:
            orders.append(current.order)
            current = current.next
        return orders

    # tail to head, without reversing the list
    def to_list_reversed(self):
        current = self.tail
        orders = []
        while current is not None:
            orders.append(current.order)
            current = current.prev
        return orders
