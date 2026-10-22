from models.DeliveryMan import DeliveryMan

class DeliverNode:
    def __init__(self, deliver_man:DeliveryMan):
        self.delivery_man = deliver_man
        self.next = None
        self.prev = None
        
class CourierRing:
    def __init__(self):
        self.current_courier = None
        
    def add_at_end(self, deliver_man:DeliveryMan):
        new_delivery = DeliverNode(deliver_man)
        
        if self.current_courier == None:
            self.current_courier = new_delivery
            new_delivery.next = new_delivery
            new_delivery.prev = new_delivery
        else:
            last = self.current_courier
            last.next = new_delivery
            
            new_delivery.next = self.current_courier
            new_delivery.prev = last
            
            self.current_courier.prev = new_delivery
        
    def is_empty(self):
        return self.current_courier is None
    
    def find(self, code:str):
        if self.is_empty():
            return None

        current = self.current_courier
        while True:
            if current.delivery_man.code == code:
                return current
            current = current.next
            if (current is self.current_courier):
                return None