        const API_URL = "http://127.0.0.1:8000/cart";
        const urlParams = new URLSearchParams(window.location.search);
        let currentCartID = urlParams.get('cartID');
        let currentUserEmail = "";
        let currentUserName = "";
        let searchTimeout = null;
        let previousItemCount = -1;

        if (currentCartID) {
            showJoinForm(currentCartID);

        // --- TOAST LOGIC ---
        function showToast(message) {
            const t = document.getElementById('toast');
            t.innerText = message;
            t.classList.remove('hidden');
            setTimeout(() => t.classList.add('show'), 10);
            setTimeout(() => {
                t.classList.remove('show');
                setTimeout(() => t.classList.add('hidden'), 300);

        function copyInviteLink() {
            const url = window.location.protocol + "//" + window.location.host + window.location.pathname + '?cartID=' + currentCartID;
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(url);
                showToast("Invite link copied!");
                // Fallback for non-HTTPS local dev
                const textArea = document.createElement("textarea");
                textArea.value = url;
                textArea.style.position = "fixed";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    showToast("Invite link copied!");
                    showToast("Failed to copy link");
                document.body.removeChild(textArea);

        function showJoinForm(cartId = null) {
            if(!cartId) {
                const code = document.getElementById('joinCode').value;
                if(code.length < 4) { showToast("Invalid code"); return; }
                showToast("Use invite link for full join. Code entry mocked.");
                return;
            document.getElementById('landingScreen').classList.add('hidden');
            document.getElementById('joinFormScreen').classList.remove('hidden');
            document.getElementById('joinRoomLabel').innerText = "Room: " + cartId.substring(0,4).toUpperCase();

        // --- OTP LOGIC ---
        async function requestOtp(emailInputId, nextDivId, btnId) {
            const email = document.getElementById(emailInputId).value;
            if(!email.endsWith("@hyderabad.bits-pilani.ac.in")) { 
                showToast("Only BITS Pilani Hyderabad emails are allowed!"); 
                return; 
            
            document.getElementById(btnId).innerText = "[ SENDING... ]";
            const res = await fetch(`${API_URL}/request-otp`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email })
            if(res.ok) {
                showToast("OTP sent to your email!");
                document.getElementById(nextDivId).classList.remove("hidden");
                document.getElementById(btnId).innerText = "[ RESEND OTP ]";
                document.getElementById(btnId).style.background = "transparent";
                document.getElementById(btnId).style.color = "var(--text-muted)";
                document.getElementById(btnId).style.border = "1px solid var(--border)";
                showToast("Error sending OTP"); 
                document.getElementById(btnId).innerText = "[ TRY AGAIN ]";

        async function verifyOtpAPI(email, otp) {
            const res = await fetch(`${API_URL}/verify-otp`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email, otp: otp })
            return res.ok;

        // --- CREATE / JOIN LOGIC ---
        async function verifyAndCreate() {
            currentUserEmail = document.getElementById("hostEmail").value;
            currentUserName = document.getElementById("hostName").value || "Host";
            const otp = document.getElementById("hostOtp").value;

            if(!await verifyOtpAPI(currentUserEmail, otp)) { showToast("Invalid OTP"); return; }

            const res = await fetch(`${API_URL}/create`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: currentUserEmail, name: currentUserName, timer: 3600 })

            if (res.ok) {
                const data = await res.json();
                currentCartID = data.cartID;
                showDashboard();
                
                const newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + "?join=" + currentCartID;
                document.getElementById("modalLinkDisplay").innerText = newurl;
                document.getElementById("inviteModal").classList.remove("hidden");
                startPolling();
                startTimer();
                

        async function verifyAndJoin() {
            currentUserEmail = document.getElementById("joinEmail").value;
            currentUserName = document.getElementById("joinName").value || "Guest";
            const otp = document.getElementById("joinOtp").value;

            if(!await verifyOtpAPI(currentUserEmail, otp)) { showToast("Invalid OTP"); return; }

            const res = await fetch(`${API_URL}/${currentCartID}/join`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: currentUserEmail, name: currentUserName })

            if (res.ok) { 
                showToast(`Joined as ${currentUserName}`);
                showDashboard(); 
                startPolling();

        function showDashboard() {
            document.getElementById('landingScreen').classList.add('hidden');
            document.getElementById('joinFormScreen').classList.add('hidden');
            document.getElementById('activeCartScreen').classList.remove('hidden');
            document.getElementById('displayCode').innerText = currentCartID.substring(0,4).toUpperCase();
            
            const newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?cartID=' + currentCartID;
            window.history.pushState({path:newurl},'',newurl);

            fetchCart();
            setInterval(fetchCart, 3000);

        // --- SEARCH LOGIC ---
        let currentSearchOffset = 0;
        let currentSearchQuery = "";
        const SEARCH_LIMIT = 5;

        function debounceSearch() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => searchProducts(false), 500);

        async function searchProducts(isPagination = false) {
            const query = document.getElementById('searchInput').value;
            const resultsDiv = document.getElementById('searchResults');
            
            if(!query) { resultsDiv.innerHTML = ""; return; }
            
            if(!isPagination) {
                currentSearchOffset = 0;
                currentSearchQuery = query;
                resultsDiv.innerHTML = `<div style="padding: 10px; color: var(--text-muted); font-family: 'JetBrains Mono'; font-size:12px;">Searching...</div>`;

            const res = await fetch(`${API_URL}/search?q=${currentSearchQuery}&offset=${currentSearchOffset}&limit=${SEARCH_LIMIT}`);

            if(res.ok) {
                const data = await res.json();
                
                // Always clear the results div to replace old items
                resultsDiv.innerHTML = "";

                data.results.forEach(product => {
                    const item = document.createElement('div');
                    item.className = "search-result-item";
                    item.innerHTML = `
                        <div style="display:flex; align-items:center; gap:15px;">
                            <span style="font-size:20px;">+</span>
                            <span style="font-weight:600; font-size:14px;">${product.name}</span>
                        </div>
                        <div style="font-family:'JetBrains Mono'; color:var(--accent);">₹${product.price}</div>
                    `;
                    item.onclick = () => {
                        addToCart(product);
                        document.getElementById('searchInput').value = "";
                        resultsDiv.innerHTML = "";
                    resultsDiv.appendChild(item);

                // Next/Prev Buttons
                const paginationControls = document.createElement('div');
                paginationControls.style = "display: flex; justify-content: space-between; align-items: center; padding: 10px 5px; margin-top: 5px; border-top: 1px solid var(--border-light);";
                
                const currentPage = Math.floor(currentSearchOffset / SEARCH_LIMIT) + 1;
                
                let controlsHtml = ``;
                if (currentSearchOffset > 0) {
                    controlsHtml += `<button onclick="paginate(-1)" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-family:'JetBrains Mono'; font-size:11px;">← PREV</button>`;
                    controlsHtml += `<div style="width: 50px;"></div>`;

                controlsHtml += `<span style="font-family:'JetBrains Mono'; font-size:11px; color:var(--text-muted);">PAGE ${currentPage}</span>`;

                if (data.results.length === SEARCH_LIMIT && (currentSearchOffset + SEARCH_LIMIT) < data.total) {
                    controlsHtml += `<button onclick="paginate(1)" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-family:'JetBrains Mono'; font-size:11px;">NEXT →</button>`;
                    controlsHtml += `<div style="width: 50px;"></div>`;
                
                paginationControls.innerHTML = controlsHtml;
                resultsDiv.appendChild(paginationControls);

                if(!isPagination) resultsDiv.innerHTML = `<div style="padding: 10px; color: #ef4444;">Failed to load.</div>`;

        function paginate(direction) {
            currentSearchOffset += (direction * SEARCH_LIMIT);
            searchProducts(true);

        // --- CART LOGIC ---
        async function addToCart(product) {
            const parsedPrice = parseInt(product.price.toString().replace(/\D/g, '')) || 0;
            showToast(`Added ${product.name}`);

            const payload = {
                contactNumber: currentUserEmail,
                name: currentUserName,
                itemToBeAdded: {
                    groceryObject: {
                        productId: product.product_id,
                        name: product.name,
                        image: product.image_url,
                        price: parsedPrice
                    quantity: 1

            await fetch(`${API_URL}/${currentCartID}/upsert`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            fetchCart(); 

        async function deleteFromCart(productId, name, image, price) {
            const payload = {
                contactNumber: currentUserEmail,
                name: currentUserName,
                itemToBeAdded: {
                    groceryObject: {
                        productId: productId,
                        name: name,
                        image: image,
                        price: price
                    quantity: 1

            await fetch(`${API_URL}/${currentCartID}/delete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            fetchCart();

        async function fetchCart() {
            if(!currentCartID) return;
            const res = await fetch(`${API_URL}/${currentCartID}`);
            if(!res.ok) return;
            const cartData = await res.json();
            
            // Populate Participants
            const participantsDiv = document.getElementById('participantsDiv');
            participantsDiv.innerHTML = "";
            
            for (const [phone, name] of Object.entries(cartData.participants)) {
                const role = phone === cartData.hostPhone ? "HOST" : "JOINED";
                participantsDiv.innerHTML += `
                    <div class="participant">
                        <div class="participant-name">👤 ${name}</div>
                        <div class="participant-role">${role}</div>
                    </div>
                `;

            // Populate Cart Items
            const cartDiv = document.getElementById('cartContents');
            cartDiv.innerHTML = "";
            
            let totalItems = 0;
            let totalPrice = 0;

            for (const [phone, itemsObj] of Object.entries(cartData.userItems)) {
                const userName = cartData.participants[phone] || phone;
                
                for (const [productId, itemData] of Object.entries(itemsObj)) {
                    totalItems += itemData.quantity;
                    totalPrice += (itemData.groceryObject.price * itemData.quantity);
                    
                    const safeName = itemData.groceryObject.name.replace(/'/g, "\\'");
                    const safeImage = itemData.groceryObject.image ? itemData.groceryObject.image.replace(/'/g, "\\'") : '';
                    const isOwner = phone === currentUserEmail;
                    
                    cartDiv.innerHTML += `
                        <div class="cart-item">
                            <div class="item-details">
                                <div>
                                    <div class="item-name">${itemData.groceryObject.name} <span style="color:var(--text-muted); font-weight:normal;">×${itemData.quantity}</span></div>
                                    <div class="item-owner">Added by ${userName}</div>
                                </div>
                            </div>
                            <div style="display:flex; align-items:center; gap: 15px;">
                                <div class="item-price">₹${itemData.groceryObject.price * itemData.quantity}</div>
                                ${isOwner ? `<button onclick="deleteFromCart('${productId}', '${safeName}', '${safeImage}', ${itemData.groceryObject.price})" class="remove-btn">Remove</button>` : ''}
                            </div>
                        </div>
                    `;
            
            if (totalItems === 0) {
                cartDiv.innerHTML = `<div style="padding: 20px 0; color: var(--text-muted); font-style: italic;">Cart is empty. Search below to add items.</div>`;

            document.getElementById('itemCount').innerText = totalItems;
            document.getElementById('totalPrice').innerText = `₹${totalPrice}`;
            
            
            // Social presence toast
            if (previousItemCount !== -1 && totalItems > previousItemCount) {
                // showToast("Someone updated the cart"); // Could be noisy, omitting unless specifically requested
            previousItemCount = totalItems;

        let checkoutMasterText = "";

        async function checkoutCart() {
            document.getElementById('checkoutModal').classList.remove('hidden');
            document.getElementById('checkoutListText').innerText = "Generating master list...";
            
            const res = await fetch(`${API_URL}/${currentCartID}/checkout`);
            if(res.ok) {
                const data = await res.json();
                
                checkoutMasterText = `TRUSTED GROUPS - CART #${currentCartID.substring(0,4).toUpperCase()}\n`;
                checkoutMasterText += `Total Items: ${data.totalItems} | Grand Total: ₹${data.grandTotal}\n`;
                checkoutMasterText += `------------------------------------\n`;
                
                data.consolidatedItems.forEach(item => {
                    checkoutMasterText += `${item.quantity}x ${item.name} (₹${item.total})\n`;
                
                checkoutMasterText += `------------------------------------\n`;
                checkoutMasterText += `Powered by trusted-groups`;
                
                document.getElementById('checkoutListText').innerText = checkoutMasterText;
                document.getElementById('checkoutListText').innerText = "Failed to load checkout list.";

        function copyCheckoutList() {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(checkoutMasterText);
                showToast("Master list copied!");
                const textArea = document.createElement("textarea");
                textArea.value = checkoutMasterText;
                textArea.style.position = "fixed";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    showToast("Master list copied!");
                    showToast("Failed to copy");
                document.body.removeChild(textArea);
        async function pushToBlinkit() {
            const authKey = document.getElementById('authKeyInput').value;
            if (!authKey) {
                showToast("Please enter an auth_key first.");
                return;
            
            const btn = document.getElementById('pushBtn');
            btn.innerText = "[ INJECTING... ]";
            
            const res = await fetch(`${API_URL}/${currentCartID}/push`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ authKey: authKey })
            
            if (res.ok) {
                const data = await res.json();
                showToast(`Pushed ${data.successful_items} items to Blinkit! (${data.failed_items} failed)`);
                btn.innerText = "[ SUCCESS ]";
                setTimeout(() => btn.innerText = "[ INJECT CART ]", 3000);
                showToast("Failed to push to Blinkit API.");
                btn.innerText = "[ INJECT CART ]";
