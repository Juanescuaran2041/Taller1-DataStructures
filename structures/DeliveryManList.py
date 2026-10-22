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

                
    def currnet_delivery (self):
        if self.is_empty():
            return None
        return self.current_courier
    
    def remove(self, code):
        deliver = self.find(code)
        
        if deliver is None:
            return None
        
        if deliver.next == deliver:
            self.current_courier = None
        else:
            deliver.prev.next = deliver.next
            deliver.next.prev = deliver.prev

            if deliver == self.current_courier:
                self.current_courier = deliver.next
        
        return True
    
    def to_list (self):
        deliveries = []
        if self.is_empty():
            return None
        deliveries.append(self.current_courier.delivery_man)
        
        current:DeliverNode = self.current_courier.next
        
        while (current != self.current_courier):
            deliveries.append(current)
            current = current.next
            
        return deliveries
            