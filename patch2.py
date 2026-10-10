with open("chrome_extension/popup.js", "r") as f:
    text = f.read()

# Replace the persistRoot cleanup with the correct Blinkit localStorage cleanup
old_cleanup = """            try {
                const persistRoot = JSON.parse(localStorage.getItem('persist:root'));
                if (persistRoot && persistRoot.cart) {
                    delete persistRoot.cart;
                    localStorage.setItem('persist:root', JSON.stringify(persistRoot));
                }
            } catch(e) {}"""

new_cleanup = """            // Wipe the local React memory so it doesn't overwrite our injection!
            localStorage.removeItem('cart');
            localStorage.removeItem('checkout');"""

text = text.replace(old_cleanup, new_cleanup)

# Re-enable the redirect/reload
text = text.replace('// window.location.href = "https://blinkit.com/cart";', 'window.location.href = "https://blinkit.com/cart";')

with open("chrome_extension/popup.js", "w") as f:
    f.write(text)
