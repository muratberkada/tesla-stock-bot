from flask import Flask
from threading import Thread
import requests
import time

# Flask server
app = Flask(__name__)

@app.route('/')
def home():
    return "Tesla Stok Botu Aktif!"

# Tesla API URL
TESLA_API_URL = ("https://www.tesla.com/inventory/api/v1/inventory-results?query="
                 "{\"query\":{\"model\":\"my\",\"condition\":\"new\","
                 "\"market\":\"TR\",\"language\":\"tr\",\"super_region\":\"europe\"},"
                 "\"offset\":0,\"count\":50}")

# Telegram bilgileri
BOT_TOKEN = "7658744054:AAGElNA0jOysddJBZIZAPGtkADb_dSAXh6E"
CHAT_ID = "1148447451"

# Header
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

prev_has_stock = False

def check_inventory():
    global prev_has_stock
    while True:
        try:
            response = requests.get(TESLA_API_URL, headers=HEADERS, timeout=30)
            data = response.json()
            total_stock = data.get("total_matches_found", 0)
            if isinstance(total_stock, str):
                total_stock = int(total_stock)
        except Exception as e:
            print(f"[{time.ctime()}] Hata oluştu: {e}")
        else:
            if total_stock > 0:
                if not prev_has_stock:
                    print(f"[{time.ctime()}] 🚗 Stok geldi! Bildirim gönderiliyor...")
                    try:
                        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        params = {"chat_id": CHAT_ID, "text": "🚗 Tesla Model Y stok geldi!"}
                        requests.get(telegram_url, params=params, timeout=5)
                    except Exception as te:
                        print(f"[{time.ctime()}] Telegram bildirimi hatası: {te}")
                    prev_has_stock = True
                else:
                    print(f"[{time.ctime()}] Stok devam ediyor ({total_stock} araç).")
            else:
                if prev_has_stock:
                    print(f"[{time.ctime()}] Stok tükendi.")
                    prev_has_stock = False
                else:
                    print(f"[{time.ctime()}] Henüz stok yok...")
        time.sleep(300)  # 5 dakikada bir kontrol

def start_background_tasks():
    thread = Thread(target=check_inventory)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    start_background_tasks()
    app.run(host="0.0.0.0", port=10000)
