import os
import time
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8942443467:AAGa91LxkLLBqIY-5-zMr2_GmRHtj1rxs6Y"
CHAT_ID = "-1003915138060"

# Cooldown tracker - prevents duplicate messages within 30 seconds
last_signal_time = {}

def is_duplicate(signal_key):
    now = time.time()
    if signal_key in last_signal_time:
        if now - last_signal_time[signal_key] < 30:
            return True
    last_signal_time[signal_key] = now
    return False

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        if not data:
            return "no data", 400

        signal = data.get("signal", "").lower()
        price = float(data.get("price", 0))

        # Block duplicates
        if is_duplicate(signal):
            return "duplicate blocked", 200

        if signal == "buy":
            tp1 = round(price + 2, 2)
            tp2 = round(price + 3, 2)
            tp3 = round(price + 15, 2)
            sl  = round(price - 15, 2)
            entry_high = round(price, 2)
            entry_low  = round(price - 10, 2)
            msg = f"BUY 🟢\nXAU/USD | GOLD\n\nENTRY : {entry_high} - {entry_low}\n\n✅ TP1 : {tp1}\n✅ TP2 : {tp2}\n✅ TP3 : {tp3}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
            send_message(msg)

        elif signal == "sell":
            tp1 = round(price - 2, 2)
            tp2 = round(price - 3, 2)
            tp3 = round(price - 15, 2)
            sl  = round(price + 15, 2)
            entry_low  = round(price, 2)
            entry_high = round(price + 10, 2)
            msg = f"SELL 🔴\nXAU/USD | GOLD\n\nENTRY : {entry_low} - {entry_high}\n\n✅ TP1 : {tp1}\n✅ TP2 : {tp2}\n✅ TP3 : {tp3}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
            send_message(msg)

        elif signal == "tp1_hit":
            send_message("GOLD SMASHED TP1 ✅✅✅\n\n☑️ Close your positions now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free")

        elif signal == "tp2_hit":
            send_message("GOLD SMASHED TP2 ✅✅✅\n\n☑️ Close your positions now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free")

        elif signal == "tp3_hit":
            send_message("GOLD SMASHED TP3 ✅✅✅\n\n🥇 ALL TARGETS HIT\n\n💰 Full profits secured\n\n👏 Well done team!")

        elif signal == "sl_hit":
            send_message("❌ GOLD SL HIT\n\nClose your positions and wait for the next signal.")

        elif signal == "breakeven":
            send_message("⚠️ MOVE SL TO BREAK EVEN NOW\n\nPrice has returned to entry level. Protect your trade!")

        else:
            return "invalid signal", 400

        return "ok", 200

    except Exception as e:
        print(f"Error: {e}")
        return "error", 500

@app.route("/")
def home():
    return "Gold Signals Bot is running! ✅"

@app.route("/test-buy")
def test_buy():
    price = 4125.00
    tp1 = round(price + 2, 2)
    tp2 = round(price + 3, 2)
    tp3 = round(price + 15, 2)
    sl  = round(price - 15, 2)
    entry_high = round(price, 2)
    entry_low  = round(price - 10, 2)
    msg = f"BUY 🟢\nXAU/USD | GOLD\n\nENTRY : {entry_high} - {entry_low}\n\n✅ TP1 : {tp1}\n✅ TP2 : {tp2}\n✅ TP3 : {tp3}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
    send_message(msg)
    return "BUY test sent! ✅"

@app.route("/test-sell")
def test_sell():
    price = 4125.00
    tp1 = round(price - 2, 2)
    tp2 = round(price - 3, 2)
    tp3 = round(price - 15, 2)
    sl  = round(price + 15, 2)
    entry_low  = round(price, 2)
    entry_high = round(price + 10, 2)
    msg = f"SELL 🔴\nXAU/USD | GOLD\n\nENTRY : {entry_low} - {entry_high}\n\n✅ TP1 : {tp1}\n✅ TP2 : {tp2}\n✅ TP3 : {tp3}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
    send_message(msg)
    return "SELL test sent! ✅"

@app.route("/test-tp1")
def test_tp1():
    send_message("GOLD SMASHED TP1 ✅✅✅\n\n☑️ Close your positions now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free")
    return "TP1 test sent! ✅"

@app.route("/test-sl")
def test_sl():
    send_message("❌ GOLD SL HIT\n\nClose your positions and wait for the next signal.")
    return "SL test sent! ✅"

@app.route("/test-breakeven")
def test_breakeven():
    send_message("⚠️ MOVE SL TO BREAK EVEN NOW\n\nPrice has returned to entry level. Protect your trade!")
    return "Breakeven test sent! ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
