import requests
import base64
from datetime import datetime
import os

class MpesaAPI:
    def __init__(self):
        self.consumer_key = os.getenv("CONSUMER_KEY", "")
        self.consumer_secret = os.getenv("CONSUMER_SECRET", "")
        self.shortcode = os.getenv("SHORTCODE", "174379")
        self.passkey = os.getenv("PASSKEY", "")
        self.callback_url = os.getenv("CALLBACK_URL", "")
        self.base_url = "https://sandbox.safaricom.co.ke"

    def get_access_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return response.json().get("access_token")
        except:
            return None

    def stk_push(self, phone_number, amount):
        token = self.get_access_token()
        if not token:
            return {"error": "Failed to authenticate with M-Pesa"}

        # Format phone to 2547XXXXXXXX
        phone = str(phone_number).strip()
        if phone.startswith("0"): phone = "254" + phone[1:]
        elif phone.startswith("+"): phone = phone[1:]
        elif not phone.startswith("254"): phone = "254" + phone

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": "TechHub Purchase",
            "TransactionDesc": "Payment for gadgets"
        }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

mpesa_client = MpesaAPI()