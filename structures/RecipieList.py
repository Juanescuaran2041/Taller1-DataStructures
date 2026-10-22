class RecipeNode:
    def __init__(self, ingridient:str):
        self.ingridient = ingridient
        self.next = None
        self.prev = None

class RecipeDoubleList:
    def __init__(self):
        self.base = None
        self.top = None
        self.size = 0

    def prepend_ingredient(self, ingredient:str):
        new_node = RecipeNode(ingredient)
        if self.base is None:
            self.base = new_node
            self.top = new_node
        else:
            new_node.next = self.base
            self.base.prev = new_node
            self.base = new_node
        self.size += 1
        
    def append_ingredient (self, ingredient:str):
        new_node = RecipeNode(ingredient)
        
        if self.top == None:
            self.top = new_node
            self.base = new_node
        else:
            new_node.prev = self.top
            self.top.next = new_node
            self.top = new_node
        self.size +=1
    
    def to_list (self):
        current = self.base
        ingredients = []
        
        while (current is not None):
            ingredients.append(current.ingridient)
            current = current.next
            
        return ingredients
    
    def to_list_reversed (self):
        current = self.top
        ingredients = []
        
        while (current is not None):
            ingredients.append(current.ingridient)
            current = current.prev
            
        return ingredients
    
    def is_empty (self):
        return self.size == 0
    