from enum import Enum

class Channel(Enum):
    COUNTER = "MOSTRADOR"
    DELIVERY = "DOMICILIO"

class State(Enum):
    IN_QUEUE = "EN_COLA"
    IN_ASSEMBLY = "EN_ARMADO"
    READY = "LISTO"
    DELIVERED = "ENTREGADO"
    CANCELED = "CANCELADO"

class Order:
    def __init__(self, number:int, channel:Channel, product_code:str, without:list, minute:int):
        self.number = number
        self.channel = channel
        self.product_code = product_code
        # layers the client asked to omit
        self.without = without
        self.minute = minute
        self.state = State.IN_QUEUE
        # minute when it was marked READY (R8)
        self.ready_minute = None
        # assembly errors (R5)
        self.errors = 0
