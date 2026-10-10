from curl_cffi import requests

headers = {
    "auth_key": "c761ec3633c22afad934fb17a66385c1c06c5472b4898b866b7306186d0bb477",
    "app_client": "consumer_web",
    "app_version": "1010101011",
    "lat": "17.5454217",
    "lon": "78.5705673",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:156.0) Gecko/20100101 Firefox/156.0",
    "Accept": "*/*",
    "Origin": "https://blinkit.com"
}

def checkStockByID(targetProductID: str) -> str:
    url = f"https://blinkit.com/v1/layout/product/{targetProductID}"
    
    with requests.Session(impersonate="chrome", headers=headers) as session:
        try:
            response = session.post(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Helper function to recursively search the JSON for specific keys
                def find_key(obj, target_key):
                    if isinstance(obj, dict):
                        if target_key in obj: 
                            return obj[target_key]
                        for k, v in obj.items():
                            result = find_key(v, target_key)
                            if result is not None: 
                                return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_key(item, target_key)
                            if result is not None: 
                                return result
                    return None

                # Extract the stock values no matter where they are nested
                inventory = find_key(data, 'inventory')
                is_sold_out = find_key(data, 'is_sold_out')
                
                # Evaluate stock condition
                if inventory is not None and inventory > 0 and is_sold_out is False:
                    return "success"
                else:
                    return "fail"
            else:
                return "fail"
                
        except Exception:
            return "fail"

if __name__ == "__main__":
    result = checkStockByID("564119")
    print(result)