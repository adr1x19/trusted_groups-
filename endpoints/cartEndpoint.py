from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from utils.verification import verifyEmailAddress, generateAndSendOtp, verifyOtp
from cartManager.cartManager import cartManagerSingleton
from cart.groceryItem import cartItem
from blinkitAPI.search import search as blinkitSearch

class otpRequest(BaseModel):
    email: str

class otpVerify(BaseModel):
    email: str
    otp: str

class joinCartRequest(BaseModel):
    email: str
    name: str

class createCartRequest(joinCartRequest):
    timer:int=3600

class upsertCartRequest(joinCartRequest):
    itemToBeAdded:cartItem

    
cartRouter = APIRouter(prefix="/cart",tags=["cart"])

@cartRouter.post("/create")
def createCart(request: createCartRequest):
    if verifyEmailAddress(request.email):
        newCartID=str(uuid.uuid4())
        cartManagerSingleton.createCart(newCartID,request.email,request.timer,request.name)
        frontendURL = f"https://myapp.com/join/{newCartID}"
        return {                                                           
                "message": "Cart created successfully!",                       
                "cartID": newCartID,                                            
                "shareableLink": frontendURL                              
            }                                                                  
    else:
        raise HTTPException(status_code=400,detail="Invalid Phone Number !")

@cartRouter.post("/request-otp")
def requestOtp(request: otpRequest):
    if not verifyEmailAddress(request.email):
        raise HTTPException(status_code=400, detail="Invalid Phone Number!")
        
    generateAndSendOtp(request.email)
    return {"message": "OTP sent successfully"}

@cartRouter.post("/verify-otp")
def verifyUserOtp(request: otpVerify):
    isValid = verifyOtp(request.email, request.otp)
    
    if not isValid:
        raise HTTPException(status_code=401, detail="Invalid or Expired OTP")
        
    return {"message": "User authenticated successfully!"}

search_cache = {}

@cartRouter.get("/search")
def searchProducts(q: str, offset: int = 0, limit: int = 5):
    # Caching on the backend because Blinkit API ignores custom offsets/limits
    if q not in search_cache or offset == 0:
        results = blinkitSearch(q, offset=0, limit=48)
        search_cache[q] = results
    else:
        results = search_cache.get(q, [])
        
    paginated_results = results[offset : offset + limit]
    
    if not paginated_results and offset == 0:
        raise HTTPException(status_code=404, detail="No products found or search failed.")
        
    return {"results": paginated_results, "total": len(results)}

@cartRouter.get("/{cartID}")
def displayCart(cartID: str):
    cartData = cartManagerSingleton.getCart(cartID)
    if cartData is None:
        raise HTTPException(status_code=404, detail="Cart not found or has expired.")
    return cartData

@cartRouter.post("/{cartID}/upsert")
def upsertToCart(cartID: str, request: upsertCartRequest):
    result = cartManagerSingleton.upsertToCart(
        cartID=cartID, 
        item=request.itemToBeAdded, 
        userContactNumber=request.email
    )
    
    if "error" in result:
        statusCode = result.get("code", 400)
        raise HTTPException(status_code=statusCode, detail=result["error"])
        
    return {"message": "Item added successfully"}

@cartRouter.post("/{cartID}/delete")
def deleteFromCart(cartID: str, request: upsertCartRequest):
    request.itemToBeAdded.quantity = -abs(request.itemToBeAdded.quantity)
    
    result = cartManagerSingleton.upsertToCart(
        cartID=cartID, 
        item=request.itemToBeAdded, 
        userContactNumber=request.email
    )
    
    if "error" in result:
        statusCode = result.get("code", 400)
        raise HTTPException(status_code=statusCode, detail=result["error"])
        
    return {"message": "Item reduced/removed successfully"}

@cartRouter.post("/{cartID}/join")
def joinCart(cartID: str, request: joinCartRequest):
    result = cartManagerSingleton.addUserToCart(
        cartID=cartID,
        userContactNumber=request.email,
        userName=request.name
    )
    
    if "error" in result:
        statusCode = result.get("code", 400)
        raise HTTPException(status_code=statusCode, detail=result["error"])
        
    return {"message": "Joined cart successfully"}


@cartRouter.get("/{cartID}/checkout")
def checkoutCart(cartID: str):
    cart = cartManagerSingleton.getCart(cartID)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")
        
    master_list = {}
    grand_total = 0
    total_items = 0
    
    for phone, user_items in cart.userItems.items():
        for product_id, cart_item in user_items.items():
            if product_id not in master_list:
                master_list[product_id] = {
                    "product_id": product_id,
                    "name": cart_item.groceryObject.name,
                    "price": cart_item.groceryObject.price,
                    "quantity": 0,
                    "total": 0
                }
            master_list[product_id]["quantity"] += cart_item.quantity
            master_list[product_id]["total"] += (cart_item.groceryObject.price * cart_item.quantity)
            
            grand_total += (cart_item.groceryObject.price * cart_item.quantity)
            total_items += cart_item.quantity
            
    consolidated_items = list(master_list.values())
    
    return {
        "cartID": cartID,
        "hostEmail": cart.hostEmail,
        "totalItems": total_items,
        "grandTotal": grand_total,
        "consolidatedItems": consolidated_items
    }

class PushToBlinkitRequest(BaseModel):
    authKey: str

@cartRouter.post("/{cartID}/push")
def pushCartToBlinkitEndpoint(cartID: str, req: PushToBlinkitRequest):
    cart = cartManagerSingleton.getCart(cartID)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")
        
    master_list = {}
    
    # Aggregate items just like the checkout endpoint
    for email, user_items in cart.userItems.items():
        for product_id, cart_item in user_items.items():
            if product_id not in master_list:
                master_list[product_id] = 0
            master_list[product_id] += cart_item.quantity
            
    # Import the push function
    from blinkitAPI.push import pushToBlinkitCart
    
    successful_pushes = 0
    failed_pushes = 0
    
    for product_id, total_qty in master_list.items():
        # Sequentially push to Blinkit
        success = pushToBlinkitCart(req.authKey, int(product_id), total_qty)
        if success:
            successful_pushes += 1
        else:
            failed_pushes += 1
            
    return {
        "message": "Push process complete",
        "successful_items": successful_pushes,
        "failed_items": failed_pushes,
        "total_attempted": len(master_list)
    }