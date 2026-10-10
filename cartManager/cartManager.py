from cart.cart import cart, cartStatus
from cart.groceryItem import cartItem
from user.user import user
from utils.instock import itemIsInStock
import time

class cartManager():
    def __init__(self):
        self.globalRegistry:dict[str,cart]={}

    def addUserToCart(self, cartID: str, userContactNumber: str, userName: str):
        cartObj = self.getCart(cartID)
        if not cartObj:
            return {"error": "Cart not found", "code": 404}
            
        cartState = cartObj.getCurrentStatus()
        if cartState == cartStatus.LOCKED:
            return {"error": "Cart is locked by the host.", "code": 403}
        elif cartState == cartStatus.EXPIRED:
            return {"error": "The timer for this cart has expired.", "code": 403}
            
        if userContactNumber not in cartObj.participants:
            cartObj.participants[userContactNumber] = userName
            cartObj.userItems[userContactNumber] = {}
            
        return {"success": True}

    def upsertToCart(self, cartID: str, item: cartItem, userContactNumber: str):
        cartObj = self.getCart(cartID)
        if not cartObj:
            return {"error": "Cart not found", "code": 404}
            
        cartState = cartObj.getCurrentStatus()
        if cartState == cartStatus.LOCKED:
            return {"error": "Cart is locked by the host.", "code": 403}
        elif cartState == cartStatus.EXPIRED:
            return {"error": "The timer for this cart has expired.", "code": 403}
            
        # --- REMOVED BLINKIT API FOR TESTING ---
        # if not itemIsInStock(item.groceryObject.productId):
        #     return {"error": "Item is out of stock !", "code": 400}
        
        if userContactNumber not in cartObj.userItems:
            return {"error": "User has not joined this cart.", "code": 403}
            
        userCartItems = cartObj.userItems[userContactNumber]
        productId = item.groceryObject.productId
        
        # --- THE RACE CONDITION TRAP ---
        if productId in userCartItems:
            # 1. Read the current quantity
            current_quantity = userCartItems[productId].quantity 
            
            # 2. Simulate the OS forcibly ripping the GIL away mid-calculation
            time.sleep(0.01) 
            
            # 3. Calculate and Write
            newQuantity = current_quantity + item.quantity
        else:
            newQuantity = item.quantity
            
        if newQuantity <= 0:
            if productId in userCartItems:
                del userCartItems[productId]
        else:
            item.quantity = newQuantity
            userCartItems[productId] = item
            
        return {"success": True}

    def createCart(self,newCartID:str, newHostContactNumber:str,newTimer:int, newHostName:str):
        newCart=cart(
            cartID=newCartID,
            hostEmail=newHostContactNumber,
            timer=newTimer,       
        )
        self.globalRegistry[newCartID]=newCart
        newCart.participants[newHostContactNumber]=newHostName
        newCart.userItems[newHostContactNumber]={}

        return newCartID

    def getCart(self, cartID: str):
        if cartID not in self.globalRegistry:
            return None
        return self.globalRegistry[cartID]

    def saveCart(self):
        pass

cartManagerSingleton= cartManager()