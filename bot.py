import yfinance as yf
import pandas as pd
import ta
import requests
import time

# ===== TELEGRAM SETTINGS =====
BOT_TOKEN = "8687171363:AAHQ-EhkujtrNmPXP9HFpX82Iw3iTsMtAWw"
CHAT_ID = "6339346924"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        print("Telegram Error")

# ===== FOREX PAIRS =====
pairs = ["EURUSD=X", "GBPUSD=X"]

def get_signal(pair):
    data = yf.download(pair, interval="5m", period="1d")

    if data.empty:
        return None

    # Indicators
    data['rsi'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    data['ema50'] = ta.trend.EMAIndicator(data['Close'], window=50).ema_indicator()
    data['ema200'] = ta.trend.EMAIndicator(data['Close'], window=200).ema_indicator()

    macd = ta.trend.MACD(data['Close'])
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()

    bb = ta.volatility.BollingerBands(data['Close'])
    data['bb_high'] = bb.bollinger_hband()
    data['bb_low'] = bb.bollinger_lband()

    latest = data.iloc[-1]

    # ===== BUY CONDITION =====
    if (latest['rsi'] < 35 and
        latest['ema50'] > latest['ema200'] and
        latest['macd'] > latest['macd_signal'] and
        latest['Close'] <= latest['bb_low']):
        
        return "BUY 🟢"

    # ===== SELL CONDITION =====
    elif (latest['rsi'] > 65 and
          latest['ema50'] < latest['ema200'] and
          latest['macd'] < latest['macd_signal'] and
          latest['Close'] >= latest['bb_high']):
        
        return "SELL 🔴"

    else:
        return None


# ===== START MESSAGE =====
send_telegram("🤖 Binart Bot Started! (5 Min Signals)")

# ===== MAIN LOOP =====
while True:
    print("Checking signals...")

    for pair in pairs:
        signal = get_signal(pair)

        if signal:
            message = f"📊 {pair}\nSignal: {signal}\nTimeframe: 5 Min ⏱️"
            print(message)
            send_telegram(message)

    print("Waiting 5 minutes...\n")
    time.sleep(300)
