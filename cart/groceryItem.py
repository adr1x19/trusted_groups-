from dataclasses import dataclass

@dataclass
class groceryItem:
    productId:str
    name:str
    image:str # will be a link to the grofers cdn network
    price:int



@dataclass
class cartItem:
    groceryObject:groceryItem
    quantity:int