from flask import Flask
from threading import Thread
import requests
import time

print("Tesla stok kontrol botu başlatıldı...")

app = Flask('')

@app.route('/')
def home():
    return "Tesla bot canlı!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

bot_token = '7658744054:AAGElNA0jOysddJBZIZAPGtkADb_dSAXh6E'
chat_id = '1148447451'

urls = [
    "https://www.tesla.com/tr_TR/inventory/new/my?arrangeby=plh&zip=06490&range=0",
    "https://www.tesla.com/tr_TR/inventory/new/my?arrangeby=plh&zip=34810&range=0"
]

last_inventory_counts = [0 for _ in urls]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

def check_inventory():
    for idx, url in enumerate(urls):
        response = requests.get(url)
        if response.status_code == 200:
            count = response.text.count('Model Y')
            if count > last_inventory_counts[idx]:
                message = f"🚗 Yeni Model Y stoğu geldi! Bölge: {url.split('zip=')[1].split('&')[0]}"
                send_telegram_message(message)
                last_inventory_counts[idx] = count
            else:
                print(f"[{time.ctime()}] Kontrol edildi: {url} - Değişiklik yok.")
        else:
            print(f"Hata: {url} - Status code: {response.status_code}")

keep_alive()

while True:
    check_inventory()
    time.sleep(300)
