from flask import Flask
from threading import Thread
import requests
import time

# Flask app - Render için server açıyoruz
app = Flask(__name__)

@app.route('/')
def home():
    return "Tesla Stok Botu Çalışıyor!"

# Tesla API URL
TESLA_API_URL = ("https://www.tesla.com/inventory/api/v1/inventory-results?query="
                 "{\"query\":{\"model\":\"my\",\"condition\":\"new\","
                 "\"market\":\"TR\",\"language\":\"tr\",\"super_region\":\"europe\"},"
                 "\"offset\":0,\"count\":50}")

# Telegram bot bilgileri
BOT_TOKEN = "7658744054:AAGElNA0jOysddJBZIZAPGtkADb_dSAXh6E"
CHAT_ID = "1148447451"

# Header
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Başlangıç durumu
prev_has_stock = False

# Kontrol fonksiyonu
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
            print(f"Hata oluştu: {e}. Tekrar denenecek...")
        else:
            if total_stock > 0:
                if not prev_has_stock:
                    print(">>> Stok bulundu! Telegram bildirimi gönderiliyor...")
                    try:
                        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        params = {"chat_id": CHAT_ID, "text": "🚗 Stok geldi! Model Y stoğa eklendi."}
                        requests.get(telegram_url, params=params, timeout=5)
                    except Exception as te:
                        print(f"Telegram bildirimi gönderilemedi: {te}")
                    prev_has_stock = True
                else:
                    print(f"Stok mevcut (Toplam {total_stock} araç).")
            else:
                if prev_has_stock:
                    print("Stok tükendi, bekleniyor...")
                    prev_has_stock = False
                else:
                    print("Henüz stok yok. Yeni araç bekleniyor...")
        time.sleep(300)  # 5 dakikada bir kontrol

# Thread ile stok kontrolü arka planda çalışacak
def run_check_inventory():
    t = Thread(target=check_inventory)
    t.start()

if __name__ == "__main__":
    run_check_inventory()
    app.run(host='0.0.0.0', port=10000)
