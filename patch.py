with open("frontend/index.html", "r") as f:
    text = f.read()

start_idx = text.find("async function pushToBlinkit()")
end_idx = text.find("</script>", start_idx)

replacement = """function copyFullCartId() {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(currentCartID);
            showToast("Cart ID copied for extension!");
        } else {
            const textArea = document.createElement("textarea");
            textArea.value = currentCartID;
            textArea.style.position = "fixed";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                showToast("Cart ID copied for extension!");
            } catch (err) {
                showToast("Failed to copy");
            }
            document.body.removeChild(textArea);
        }
    }
"""

new_text = text[:start_idx] + replacement + text[end_idx:]

with open("frontend/index.html", "w") as f:
    f.write(new_text)
