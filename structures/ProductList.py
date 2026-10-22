from models.Product import Product

class ProductNode:
    def __init__(self, product:Product):
        self.product = product
        self.next = None

class ProductCatalog:
    def __init__(self):
        self.firstProduct:ProductNode | None = None
        self.lastProduct: ProductNode | None = None
        self.total = 0


    def register_product (self, code:str):
        new_product = Product(code)

        new_node = ProductNode(new_product)

        if self.firstProduct is None:
            self.firstProduct = new_node
            self.lastProduct = new_node
        else:
            self.lastProduct.next = new_node
            self.lastProduct = new_node

        self.total +=1

    def is_empty (self):
        return self.total == 0

    def to_array (self):
        current = self.firstProduct
        products = []

        while current is not None:
            products.append(current.product)
            current = current.next

        return products

    def remove_product (self, code:str) -> bool:
        current = self.firstProduct
        prev = None

        while current is not None:
            if current.product.code == code:
                # if first is current product
                if prev is None:
                    self.firstProduct = current.next
                else:
                    # if its in the middle
                    prev.next = current.next
                # if current is in the last one this is the product    
                if current is self.lastProduct:
                    self.lastProduct = prev
                self.total -=1
                return True
            #modyfiers
            prev = current
            current = current.next

        return False    
