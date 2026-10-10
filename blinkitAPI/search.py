from curl_cffi import requests

#may include proxies.. 
USER_AGENT="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0"
LAT="17.5454217"
LON="78.5705673"
AUTH_KEY="c761ec3633c22afad934fb17a66385c1c06c5472b4898b866b7306186d0bb477"


from curl_cffi import requests


url = "https://blinkit.com/v1/layout/search"

#try to create a rotating auth key scraper 
headers = {
    "auth_key": AUTH_KEY,
    "lat": "17.5454217",
    "lon": "78.5705673",
    "app_client": "consumer_web"
}


def search(query:str, offset:int=0, limit:int=48):
    payload = {
        "offset": offset,
        "limit": limit,
        "actual_query": query,
        "last_snippet_type": "product_card_snippet_type_2",
        "last_widget_type": "listing_container",
        "page_index": 1,
        "q": query,
        "search_count": 49,
        "search_method": "basic",
        "search_type": "type_to_search",
        "tab_position": 0,
        "total_entities_processed": 1,
        "total_pagination_items": 49
    }
    with requests.Session(impersonate="chrome", headers=headers) as session:

        try:
            response = session.post(url, params=payload)
            data = response.json()
            snippets = data.get('response', {}).get('snippets', [])
            results = []
            #could further optimize this 
            for item in snippets:
                item_data = item.get('data', {})
                
                name = item_data.get('name', {}).get('text')
                price = item_data.get('normal_price', {}).get('text')
                image_url = item_data.get('image', {}).get('url')
                
                if name and price:
                    # blinkit product snippet sometimes stores id in 'id' or 'product_id'
                    product_id = item_data.get('product_id') or item_data.get('id') or ""
                    results.append({
                        "name": name,
                        "price": price,
                        "image_url": image_url,
                        "product_id": str(product_id)
                    })
            
            return results
            
        except Exception as e:
            print(f"Search API error: {e}")
            return []






if __name__=="__main__":
    search("555855")