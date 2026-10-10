import random
import time
import os
import smtplib
from email.mime.text import MIMEText

otpBank = {}

# Loaded from secrets.sh
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD")

def verifyEmailAddress(email: str) -> bool:
    # Restrict app to BITS Pilani Hyderabad students only
    return email.strip().endswith("@hyderabad.bits-pilani.ac.in")

def generateAndSendOtp(email: str) -> bool:
    otp = str(random.randint(100000, 999999))
    expiresAt = time.time() + (5 * 60)
    
    otpBank[email] = {
        "otp": otp,
        "expiresAt": expiresAt
    }
    
    try:
        msg = MIMEText(f"Your Trusted Groups OTP is: {otp}\nIt expires in 5 minutes.")
        msg['Subject'] = 'Trusted Groups Login OTP'
        msg['From'] = SMTP_EMAIL
        msg['To'] = email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            server.send_message(msg)
            
        print(f"[GMAIL] -> Sent OTP to {email}")
        return True
    except Exception as e:
        print(f"[GMAIL ERROR] -> {e}")
        # Fallback to terminal for local dev
        print(f"\n[MOCK EMAIL] -> Sent OTP {otp} to {email}\n")
        return True

def verifyOtp(email: str, userProvidedOtp: str) -> bool:
    if email not in otpBank:
        return False
        
    record = otpBank[email]
    
    if time.time() > record["expiresAt"]:
        del otpBank[email]
        return False
        
    if record["otp"] == userProvidedOtp:
        del otpBank[email]
        return True
        
    return False
