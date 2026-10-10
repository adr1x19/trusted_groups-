import requests
from locust import HttpUser, between, task, events

# Global variables
SHARED_CART_ID = None
SHARED_USER_NUMBER = "111111"

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Runs once before any simulated users spawn. 
    Creates the single cart we will hammer.
    """
    global SHARED_CART_ID
    host = environment.host or "http://127.0.0.1:8000"
    
    response = requests.post(f"{host}/cart/create", json={
        "contactNumber": "9522596411",
        "name": "Global Test Cart",
        "timer": 3600
    })
    
    if response.status_code == 200:
        SHARED_CART_ID = response.json().get("cartID")
        print(f"\n--- CREATED GLOBAL CART: {SHARED_CART_ID} ---\n")
    else:
        print("Failed to create global cart!")


class APIUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8000"

    def on_start(self):
        self.cart_id = SHARED_CART_ID
        
        # EVERY user acts as the exact same person to force the race condition
        self.client.post(f"/cart/{self.cart_id}/join", json={
            "contactNumber": SHARED_USER_NUMBER,
            "name": "Race Condition Tester"
        })

    @task
    def add_item(self):
        # All users add 1 quantity of the exact same product at the exact same time
        payload = {
            "contactNumber": SHARED_USER_NUMBER,
            "name": "Race Condition Tester",
            "itemToBeAdded": {
                "groceryObject": {
                    "productId": "564119",
                    "name": "Test Milk",
                    "image": "http://example.com/milk.png",
                    "price": 50
                },
                "quantity": 1
            }
        }
        
        self.client.post(
            f"/cart/{self.cart_id}/upsert",
            json=payload,
            name="/cart/[id]/upsert"
        )