import requests

API_KEY = "8346Z6K-3G84EJV-K5FN0B7-0RHC4AB"
url = "https://api.nowpayments.io/v1/payment"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "price_amount": 50,  # ← مبلغ را ببر 50 یا 100
    "price_currency": "usd",
    "pay_currency": "usdttrc20",
    "order_id": "test_005",
    "is_fee_paid_by_user": True
}

response = requests.post(url, json=payload, headers=headers)
print("Status:", response.status_code)

if response.status_code == 201:
    data = response.json()
    print("✅ Success!")
    print(f"Address: {data['pay_address']}")
    print(f"Amount: {data['pay_amount']} USDT")
    print(f"Payment ID: {data['payment_id']}")
else:
    print("❌ Error:", response.json())