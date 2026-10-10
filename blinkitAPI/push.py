from curl_cffi import requests

def pushToBlinkitCart(auth_key: str, product_id: int, quantity: int) -> bool:
    """
    Pushes an item directly into the user's real Blinkit Cart using curl_cffi 
    to bypass TLS fingerprinting blocks.
    """
    url = "https://blinkit.com/v5/carts" 
    
    headers = {
        "auth_key": auth_key,
        "app_client": "consumer_web",
        "app_version": "52434333",
        "access_token": "null",
        "device_id": "1a995b495d91ec81",
        "Content-Type": "application/json",
        "lat": "17.5454217",
        "lon": "78.5705673",
        "platform": "mobile_web",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0"
    }
    
    payload = {
        "items": [
            {
                "product_id": product_id,
                "quantity": quantity
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, impersonate="chrome")
        
        print(f"[BLINKIT PUSH] -> HTTP {response.status_code}")
        print(f"[BLINKIT RESPONSE] -> {response.text[:200]}")
        
        if response.status_code == 429:
            print("[CLOUDFLARE BLOCK] -> Got 429 Too Many Requests")
            return False
            
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"[BLINKIT PUSH ERROR] -> {e}")
        return False
