import os
import time
import threading
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8942443467:AAGa91LxkLLBqIY-5-zMr2_GmRHtj1rxs6Y"
CHAT_ID = "-1003915138060"

active_trades = {}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def get_gold_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"
        r = requests.get(url, timeout=5)
        data = r.json()
        return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
    except:
        return None

def monitor_trade(trade_id, signal, entry, tp1, tp2, tp3, sl):
    tp1_hit = False
    tp2_hit = False

    while trade_id in active_trades:
        price = get_gold_price()
        if price is None:
            time.sleep(30)
            continue

        if signal == "buy":
            if not tp1_hit and price >= tp1:
                tp1_hit = True
                send_message("GOLD SMASHED TP1 ✅✅✅\n\n☑️ Close your positions now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free")
            elif tp1_hit and not tp2_hit and price >= tp2:
                tp2_hit = True
                send_message("GOLD SMASHED TP2 ✅✅✅\n\n☑️ Close your positions now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free")
            elif tp2_hit and price >= tp3:
                send_message("GOLD SMASHED TP3 ✅✅✅\n\n🥇 ALL TARGETS HIT\n\n💰 Full profits secured\n\n👏 Well done team!")
                del active_trades[trade_id]
                break
            elif price <= sl:
                send_message("❌ GOLD SL HIT")
                del active_trades[trade_id]
                break

        elif signal == "sell":
            if not tp1_hit and price <= tp1:
                tp1_hit = True
                send_message("GOLD SMASHED TP1 ✅✅✅\n\n☑️ Close your positions now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free")
            elif tp1_hit and not tp2_hit and price <= tp2:
                tp2_hit = True
                send_message("GOLD SMASHED TP2 ✅✅✅\n\n☑️ Close your positions now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free")
            elif tp2_hit and price <= tp3:
                send_message("GOLD SMASHED TP3 ✅✅✅\n\n🥇 ALL TARGETS HIT\n\n💰 Full profits secured\n\n👏 Well done team!")
                del active_trades[trade_id]
                break
            elif price >= sl:
                send_message("❌ GOLD SL HIT")
                del active_trades[trade_id]
                break

        time.sleep(30)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    signal = data.get("signal", "").lower()
    price = float(data.get("price"))

    if signal == "buy":
        tp1 = round(price + 2, 2)
        tp2 = round(price + 3, 2)
        tp3 = round(price + 15, 2)
        sl  = round(price - 15, 2)
        entry_high = round(price, 2)
        entry_low  = round(price - 10, 2)
        msg = f"BUY 🟢\nXAU/USD | GOLD\n\nENTRY : {entry_high} - {entry_low}\n\n✅ TP1 : {tp1}\n✅ TP2 : {tp2}\n✅ TP3 : {tp3}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"

    elif signal == "sell":
        tp1 = round(price - 2, 2)
        tp2 = round(price - 3, 2)
        tp3 = round(price - 15, 2)
        sl  = round(price + 15, 2)
        entry_low  = round(price, 2)
        entry_high = round(price + 10, 2)
        msg = f"SELL 🔴\nXAU/USD | GOLD\n\nENTRY : {entry_low} - {entry_high}\n\n✅ TP1 : {tp1}\n✅ TP2 : {tp2}\n✅ TP3 : {tp3}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"

    else:
        return "invalid", 400

    send_message(msg)

    trade_id = str(time.time())
    active_trades[trade_id] = True
    t = threading.Thread(target=monitor_trade, args=(trade_id, signal, price, tp1, tp2, tp3, sl))
    t.daemon = True
    t.start()

    return "ok", 200

@app.route("/")
def home():
    return "Gold Signals Bot is running! ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
