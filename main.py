from flask import Flask
from threading import Thread
import requests
import time

app = Flask(__name__)

# Tesla API URL
TESLA_API_URL = ("https://www.tesla.com/inventory/api/v1/inventory-results?query="
                 "{\"query\":{\"model\":\"my\",\"condition\":\"new\","
                 "\"market\":\"TR\",\"language\":\"tr\",\"super_region\":\"europe\"},"
                 "\"offset\":0,\"count\":50}")

# Telegram bot bilgileri
BOT_TOKEN = "7658744054:AAGElNA0jOysddJBZIZAPGtkADb_dSAXh6E"
CHAT_ID = "1148447451"

# HTTP header
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

prev_has_stock = False

def check_inventory():
    global prev_has_stock
    print("[BOT] Tesla stok kontrol botu başladı.", flush=True)
    while True:
        try:
            response = requests.get(TESLA_API_URL, headers=HEADERS, timeout=30)
            data = response.json()
            total_stock = data.get("total_matches_found", 0)
            if isinstance(total_stock, str):
                total_stock = int(total_stock)
        except Exception as e:
            print(f"[{time.ctime()}] Hata oluştu: {e}", flush=True)
        else:
            if total_stock > 0:
                if not prev_has_stock:
                    print(f"[{time.ctime()}] 🚗 Stok bulundu! Telegram bildirimi gönderiliyor...", flush=True)
                    try:
                        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        params = {"chat_id": CHAT_ID, "text": "🚗 Tesla Model Y stoğa eklendi!"}
                        requests.get(telegram_url, params=params, timeout=5)
                    except Exception as te:
                        print(f"[{time.ctime()}] Telegram bildirimi hatası: {te}", flush=True)
                    prev_has_stock = True
                else:
                    print(f"[{time.ctime()}] 🚗 Stok mevcut ({total_stock} araç).", flush=True)
            else:
                if prev_has_stock:
                    print(f"[{time.ctime()}] Stok tükendi.", flush=True)
                    prev_has_stock = False
                else:
                    print(f"[{time.ctime()}] Henüz stok yok. Bekleniyor...", flush=True)
        time.sleep(300)

@app.route('/')
def home():
    return "Tesla Stok Botu Aktif!"

def start_background_task():
    t = Thread(target=check_inventory)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    start_background_task()
    app.run(host='0.0.0.0', port=10000)
