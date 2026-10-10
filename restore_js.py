with open("frontend/index.html", "r") as f:
    html = f.read()
    
start = html.find('<script>')
end = html.find('</script>') + 9

with open("full_script.txt", "r") as f:
    js_code = f.read()
    
if start != -1 and end != -1:
    new_html = html[:start] + js_code + html[end:]
    with open("frontend/index.html", "w") as f:
        f.write(new_html)
    print("JS Restored successfully.")
else:
    print("Tags not found.")
