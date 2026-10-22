class LayerNode:
    def __init__(self, layer:str):
        self.layer = layer
        self.next = None

class LayerStack:
    def __init__(self):
        self.top:LayerNode | None = None
        self.size = 0

    def is_empty(self):
        return self.size == 0

    def push(self, layer:str):
        new_node = LayerNode(layer)
        new_node.next = self.top
        self.top = new_node
        self.size += 1

    def pop(self):
        if self.top is None:
            return None
        layer = self.top.layer
        self.top = self.top.next
        self.size -= 1
        return layer

    def peek(self):
        if self.top is None:
            return None
        return self.top.layer

    # from the top to the base, the stack is not modified
    def to_list(self):
        current = self.top
        layers = []
        while current is not None:
            layers.append(current.layer)
            current = current.next
        return layers
