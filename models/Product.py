from enum import Enum

class State (Enum):
    IN_QUEUE = "IN_QUEUE"
    IN_ASSEMBLY  = "IN_ASSEMBLY"
    READY = "READY"
    CANCELED = "CANCELED"


class Product:
    def __init__(self, code: str, recipe):
        self.code = code
        self.recipe = recipe