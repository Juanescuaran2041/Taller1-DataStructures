from models.Order import Order

class OrderNode:
    def __init__(self, order:Order):
        self.order = order
        self.next = None
        
class OrderQueue:
    def __init__(self, capacity:int):
        self.head:OrderNode | None = None
        self.tail:OrderNode | None = None
        self.size = 0
        self.capacity = capacity
        
    def is_full(self):
        return self.size >= self.capacity
    
    def enqueue(self, order:Order) -> bool:
        new_order = OrderNode(order)
        
        if (self.tail is None):
            self.head = new_order
            self.tail = new_order
        else:
            self.tail.next = new_order
            self.tail = new_order
            
        self.size +=1
        
    def dequeue(self):
        if self.head is None:
            return None
        
        removed = self.head
        self.head = removed.next
        
        if (self.head is None):
            self.tail = None
        
        self.size -=1
        return removed.order
        
    