with open("chrome_extension/popup.js", "r") as f:
    text = f.read()

# Replace the previous hijack block with the exact structure from the user's dump
old_hijack = """            // HIJACK LOCAL STORAGE TO FORCE REACT TO RENDER OUR ITEMS
            try {
                let cartStr = localStorage.getItem('cart');
                if (cartStr) {
                    let cart = JSON.parse(cartStr);
                    
                    if(!cart.items) cart.items = {};
                    if(!cart.cartItems) cart.cartItems = {};
                    
                    for (let item of items) {
                        let pidStr = item.product_id.toString();
                        let productObj = {
                            product_id: parseInt(item.product_id),
                            price: item.price,
                            image_url: "https://cdn.grofers.com/app/images/products/full_screen/pro_392652.jpg", // Placeholder image
                            unit: "1 unit",
                            mrp: item.price,
                            name: item.name
                        };
                        
                        let cartItemObj = {
                            product: productObj,
                            quantity: item.quantity
                        };
                        
                        cart.items[pidStr] = cartItemObj;
                        cart.cartItems[pidStr] = cartItemObj;
                    }
                    
                    // Recalculate totals so the UI math matches
                    let newTotal = 0;
                    let newCount = 0;
                    for (let pid in cart.items) {
                        newTotal += (cart.items[pid].product.price * cart.items[pid].quantity);
                        newCount += cart.items[pid].quantity;
                    }
                    cart.total = newTotal;
                    cart.count = newCount;
                    cart.uniqueSkuInCart = Object.keys(cart.items).length;
                    
                    localStorage.setItem('cart', JSON.stringify(cart));
                    console.log("[TRUSTED GROUPS] Successfully hijacked Local Storage!");
                }
            } catch(e) {
                console.error("Failed to hijack local storage", e);
            }"""

new_hijack = """            // HIJACK LOCAL STORAGE EXACTLY AS BLINKIT EXPECTS
            try {
                let cartStr = localStorage.getItem('cart');
                let cart = cartStr ? JSON.parse(cartStr) : {};
                
                if(!cart.items) cart.items = {};
                if(!cart.cartItems) cart.cartItems = {};
                
                for (let item of items) {
                    let pidStr = item.product_id.toString();
                    
                    // Construct exact Blinkit product object
                    let productObj = {
                        product_id: parseInt(item.product_id),
                        price: item.price || 0, // Fallback if API doesn't have it
                        name: item.name || "Trusted Groups Item",
                        image_url: "https://cdn.grofers.com/app/images/products/full_screen/pro_392652.jpg",
                        unit: "1 pc",
                        mrp: item.price || 0,
                        group_id: parseInt(item.product_id),
                        isCurrentVariant: true
                    };
                    
                    let cartItemObj = {
                        product: productObj,
                        quantity: item.quantity
                    };
                    
                    cart.items[pidStr] = cartItemObj;
                    cart.cartItems[pidStr] = cartItemObj;
                }
                
                // Recalculate totals precisely
                let newTotal = 0;
                let newCount = 0;
                for (let pid in cart.items) {
                    let itemPrice = cart.items[pid].product.price || 0;
                    let itemQty = cart.items[pid].quantity || 0;
                    newTotal += (itemPrice * itemQty);
                    newCount += itemQty;
                }
                
                cart.total = newTotal;
                cart.count = newCount;
                cart.uniqueSkuInCart = Object.keys(cart.items).length;
                cart.cart_state = "valid";
                
                localStorage.setItem('cart', JSON.stringify(cart));
                console.log("[TRUSTED GROUPS] Successfully hijacked Local Storage with exact structure!");
            } catch(e) {
                console.error("[TRUSTED GROUPS] Failed to hijack local storage", e);
            }"""

text = text.replace(old_hijack, new_hijack)

with open("chrome_extension/popup.js", "w") as f:
    f.write(text)
