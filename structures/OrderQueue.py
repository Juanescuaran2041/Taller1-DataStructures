from models.Order import Order

class OrderNode:
    def __init__(self, order:Order):
        self.order = order
        self.next = None
        
class OrderQueue:
    def __init__(self, capacity:int = 4):
        self.head:OrderNode | None = None
        self.tail:OrderNode | None = None
        self.size = 0
        self.capacity = capacity
        
    def is_full(self):
        return self.size >= self.capacity
    
    def is_empty(self):
        return self.size == 0

    def peek(self):
        if self.head is None:
            return None
        return self.head.order

    def to_list(self):
        current = self.head
        orders = []
        while current is not None:
            orders.append(current.order)
            current = current.next
        return orders

    def enqueue(self, order:Order) -> bool:
        # R7: a full queue rejects the order
        if self.is_full():
            return False
        new_order = OrderNode(order)

        if (self.tail is None):
            self.head = new_order
            self.tail = new_order
        else:
            self.tail.next = new_order
            self.tail = new_order
            
        self.size +=1
        return True

    def dequeue(self):
        if self.head is None:
            return None
        
        removed = self.head
        self.head = removed.next
        
        if (self.head is None):
            self.tail = None
        
        self.size -=1
        return removed.order
        
    