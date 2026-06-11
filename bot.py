import os
import time
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8942443467:AAGa91LxkLLBqIY-5-zMr2_GmRHtj1rxs6Y"
CHAT_ID = "-1003915138060"

last_buy_msg_id = None
last_sell_msg_id = None
last_signal_time = {}

def is_duplicate(signal_key):
    now = time.time()
    if signal_key in last_signal_time:
        if now - last_signal_time[signal_key] < 30:
            return True
    last_signal_time[signal_key] = now
    return False

def send_message(text, reply_to=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    response = requests.post(url, json=payload)
    data = response.json()
    if data.get("ok"):
        return data["result"]["message_id"]
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    global last_buy_msg_id, last_sell_msg_id
    try:
        data = request.json
        if not data:
            return "no data", 400

        signal = data.get("signal", "").lower()
        price = float(data.get("price", 0))

        if is_duplicate(signal):
            return "duplicate blocked", 200

        if signal == "buy":
            tp = round(price + 30, 2)
            sl = round(price - 15, 2)
            entry_high = round(price, 2)
            entry_low  = round(price - 10, 2)
            msg = f"BUY 🟢\nXAU/USD | GOLD\n\nENTRY : {entry_high} - {entry_low}\n\n✅ TP : {tp}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
            last_buy_msg_id = send_message(msg)

        elif signal == "sell":
            tp = round(price - 30, 2)
            sl = round(price + 15, 2)
            entry_low  = round(price, 2)
            entry_high = round(price + 10, 2)
            msg = f"SELL 🔴\nXAU/USD | GOLD\n\nENTRY : {entry_low} - {entry_high}\n\n✅ TP : {tp}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
            last_sell_msg_id = send_message(msg)

        elif signal == "be_alert":
            reply_id = last_buy_msg_id if last_buy_msg_id else last_sell_msg_id
            send_message("⚠️ GOLD UPDATE\n\nWe caught 20 pips from the market! 🎯\n\n☑️ Close the trade now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free", reply_to=reply_id)

        elif signal == "tp_hit":
            reply_id = last_buy_msg_id if last_buy_msg_id else last_sell_msg_id
            send_message("GOLD SMASHED TP ✅✅✅\n\n🥇 ALL TARGETS HIT\n\n💰 Full profits secured\n\n👏 Well done team!", reply_to=reply_id)

        elif signal == "sl_hit":
            reply_id = last_buy_msg_id if last_buy_msg_id else last_sell_msg_id
            send_message("❌ GOLD SL HIT\n\nClose your positions and wait for the next signal.", reply_to=reply_id)

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
    global last_buy_msg_id
    price = 4060.00
    tp = round(price + 30, 2)
    sl = round(price - 15, 2)
    entry_high = round(price, 2)
    entry_low  = round(price - 10, 2)
    msg = f"BUY 🟢\nXAU/USD | GOLD\n\nENTRY : {entry_high} - {entry_low}\n\n✅ TP : {tp}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
    last_buy_msg_id = send_message(msg)
    return "BUY test sent! ✅"

@app.route("/test-sell")
def test_sell():
    global last_sell_msg_id
    price = 4060.00
    tp = round(price - 30, 2)
    sl = round(price + 15, 2)
    entry_low  = round(price, 2)
    entry_high = round(price + 10, 2)
    msg = f"SELL 🔴\nXAU/USD | GOLD\n\nENTRY : {entry_low} - {entry_high}\n\n✅ TP : {tp}\n🛑 SL : {sl}\n\n(Use Appropriate Lot Sizes)"
    last_sell_msg_id = send_message(msg)
    return "SELL test sent! ✅"

@app.route("/test-be")
def test_be():
    reply_id = last_buy_msg_id if last_buy_msg_id else last_sell_msg_id
    send_message("⚠️ GOLD UPDATE\n\nWe caught 20 pips from the market! 🎯\n\n☑️ Close the trade now and secure your profits\n\nOr\n\n☑️ Move your SL to Break Even and let the trade run risk free", reply_to=reply_id)
    return "BE test sent! ✅"

@app.route("/test-tp")
def test_tp():
    reply_id = last_buy_msg_id if last_buy_msg_id else last_sell_msg_id
    send_message("GOLD SMASHED TP ✅✅✅\n\n🥇 ALL TARGETS HIT\n\n💰 Full profits secured\n\n👏 Well done team!", reply_to=reply_id)
    return "TP test sent! ✅"

@app.route("/test-sl")
def test_sl():
    reply_id = last_buy_msg_id if last_buy_msg_id else last_sell_msg_id
    send_message("❌ GOLD SL HIT\n\nClose your positions and wait for the next signal.", reply_to=reply_id)
    return "SL test sent! ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
