from enum import Enum

class Status(Enum):
    AVAILABLE = "AVAILABLE"
    EN_ROUTE = "EN_ROUTE"

class DeliveryMan:
    def __init__(self, code:str, status:Status, deliveries:int):
        self.code = code
        self.status = status
        self.deliveries = deliveries
        
    def get_status(self):
        return self.status
    
    def set_status(self, status:Status):
        self.status = status
        
    