let blinkitSession = null;

// Load memory
chrome.storage.local.get(['savedBlinkitCartId'], (result) => {
    if (result.savedBlinkitCartId) {
        document.getElementById('blinkitCartId').value = result.savedBlinkitCartId;
    }
});
document.getElementById('blinkitCartId').addEventListener('input', (e) => {
    chrome.storage.local.set({ savedBlinkitCartId: e.target.value.trim() });
});

function extractBlinkitData() {
    let data = { authKey: null, lat: "0", lon: "0", accessToken: "null" };
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith('gr_1_accessToken=')) data.accessToken = decodeURIComponent(c.substring(17));
        if (c.startsWith('gr_1_lat=')) data.lat = c.substring(9);
        if (c.startsWith('gr_1_lon=')) data.lon = c.substring(9);
    }
    try {
        const dump = JSON.stringify(localStorage).replace(/\\/g, '');
        const authMatch = dump.match(/["']auth_?key["']\s*:\s*["']([a-f0-9]{64})["']/i);
        if (authMatch) data.authKey = authMatch[1];
    } catch(e) {}
    return data;
}

chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0].url.includes('blinkit.com')) {
        document.getElementById('status').innerText = "Error: Please open blinkit.com first!";
        return;
    }
    chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        func: extractBlinkitData,
    }, (results) => {
        if (results && results[0] && results[0].result) {
            blinkitSession = results[0].result;
            if (blinkitSession.authKey) {
                document.getElementById('status').innerText = `✅ Session tokens detected!`;
                document.getElementById('status').style.color = "#C8F04A";
            }
        }
    });
});

document.getElementById('injectBtn').addEventListener('click', async () => {
    const cartId = document.getElementById('cartId').value.trim();
    const targetBlinkitCart = document.getElementById('blinkitCartId').value.trim();
    
    if (!cartId || !targetBlinkitCart) return;
    if (!blinkitSession || !blinkitSession.authKey) {
        alert("No Blinkit auth tokens found! Are you logged in?");
        return;
    }

    const status = document.getElementById('status');
    status.innerText = "Fetching Trusted Groups cart...";
    
    try {
        const res = await fetch(`http://127.0.0.1:8000/cart/${cartId}/checkout`);
        const data = await res.json();
        
        status.innerText = `Injecting ${data.totalItems} items...`;

        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: injectCartViaFetch,
            args: [data.consolidatedItems, blinkitSession, targetBlinkitCart]
        });

    } catch (e) {
        status.innerText = "Error connecting to local server.";
    }
});

async function injectCartViaFetch(items, session, targetCartId) {
    console.log("[TRUSTED GROUPS] Starting Target Cart Injection...");
    
    const url = `https://blinkit.com/v5/carts/${targetCartId}`;
    
    const payloadItems = items.map(item => ({
        product_id: parseInt(item.product_id),
        quantity: item.quantity
    }));
    
    try {
        const response = await fetch(url, {
            method: "PUT",
            headers: {
                "auth_key": session.authKey,
                "access_token": session.accessToken,
                "app_client": "consumer_web",
                "app_version": "52434333",
                "platform": "mobile_web",
                "device_id": "a8932f8c4700ba23",
                "lat": session.lat,
                "lon": session.lon,
                "Content-Type": "application/json",
                "accept": "*/*"
            },
            body: JSON.stringify({ items: payloadItems })
        });
        
        if (response.ok) {
            console.log(`[TRUSTED GROUPS SUCCESS]\n`, JSON.stringify(await response.json(), null, 2));
            alert(`Trusted Groups: Successfully injected into Cart #${targetCartId}! Opening Cart...`);
            window.location.href = "https://blinkit.com/cart";
        } else {
            console.error(`[TRUSTED GROUPS ERROR] -> HTTP ${response.status}:`, await response.text());
            alert("Injection failed. Check console.");
        }
    } catch(e) {
        console.error("[TRUSTED GROUPS EXCEPTION]", e);
    }
}
