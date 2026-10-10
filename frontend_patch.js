// --- OTP LOGIC ---
async function requestOtp(emailInputId, nextDivId, btnId) {
    const email = document.getElementById(emailInputId).value;
    if(!email.endsWith("@hyderabad.bits-pilani.ac.in")) { 
        showToast("Only BITS Pilani Hyderabad emails are allowed!"); 
        return; 
    }
    
    document.getElementById(btnId).innerText = "[ SENDING... ]";
    const res = await fetch(`${API_URL}/request-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    });
    if(res.ok) {
        showToast("OTP sent to your email!");
        document.getElementById(nextDivId).classList.remove('hidden');
        document.getElementById(btnId).innerText = "[ RESEND OTP ]";
        document.getElementById(btnId).style.background = "transparent";
        document.getElementById(btnId).style.color = "var(--text-muted)";
        document.getElementById(btnId).style.border = "1px solid var(--border)";
    } else { 
        showToast("Error sending OTP"); 
        document.getElementById(btnId).innerText = "[ TRY AGAIN ]";
    }
}

async function verifyOtpAPI(email, otp) {
    const res = await fetch(`${API_URL}/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, otp: otp })
    });
    return res.ok;
}

// --- CREATE / JOIN LOGIC ---
async function verifyAndCreate() {
    currentUserEmail = document.getElementById('hostEmail').value;
    currentUserName = document.getElementById('hostName').value || "Host";
    const otp = document.getElementById('hostOtp').value;

    if(!await verifyOtpAPI(currentUserEmail, otp)) { showToast("Invalid OTP"); return; }

    const res = await fetch(`${API_URL}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: currentUserEmail, name: currentUserName, timer: 3600 })
    });

    if (res.ok) {
        const data = await res.json();
        currentCartID = data.cartID;
        showDashboard();
        
        const newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?cartID=' + currentCartID;
        document.getElementById('modalLinkDisplay').innerText = newurl;
        document.getElementById('inviteModal').classList.remove('hidden');
        
    } else { showToast("Creation failed"); }
}

async function verifyAndJoin() {
    currentUserEmail = document.getElementById('joinEmail').value;
    currentUserName = document.getElementById('joinName').value || "Guest";
    const otp = document.getElementById('joinOtp').value;

    if(!await verifyOtpAPI(currentUserEmail, otp)) { showToast("Invalid OTP"); return; }

    const res = await fetch(`${API_URL}/${currentCartID}/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: currentUserEmail, name: currentUserName })
    });

    if (res.ok) { 
        showToast(`Joined as ${currentUserName}`);
        showDashboard(); 
    } else { showToast("Error joining cart"); }
}
