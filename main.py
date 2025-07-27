import requests
import time
import telegram
from datetime import datetime, timezone
from keep_alive import keep_alive

BOT_TOKEN = '8465620127:AAGK4b1Pqyc9YPpfG1k5TgQ8O87HE2sDwjg'
CHAT_ID = '65074199'
CHECK_INTERVAL = 60  # ثانیه

bot = telegram.Bot(token=BOT_TOKEN)
sent_ids = set()

def fetch_trending_tokens():
    try:
        r = requests.get("https://pump.fun/api/tokens/trending", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("⛔️ خطا در ارتباط:", e)
    return []

def is_recent(token_time, minutes=5):
    now = datetime.now(timezone.utc)
    created = datetime.fromisoformat(token_time.replace("Z", "+00:00"))
    return (now - created).total_seconds() <= minutes * 60

def check_extra_conditions(t):
    if t['liquidity_injected'] < 5:
        return False
    if t['supply'] > 1_000_000:
        return False
    if "test" in t['name'].lower():
        return False
    if t.get('dev_wallet') in [None, "", "0x0000000000000000000000000000000000000000"]:
        return False
    if t.get('holders', 0) < 2:
        return False
    return True

def send_alert(t):
    url = f"https://pump.fun/{t['id']}"
    msg = (
        f"🚨 <b>توکن جدید و قابل خرید در Pump.fun</b>\n\n"
        f"🧪 Name: <code>{t['name']}</code> (${t['symbol']})\n"
        f"💵 Supply: {t['supply']:,}\n"
        f"💧 Liquidity: ${t['liquidity_injected']:,}\n"
        f"👥 Holders: {t.get('holders', 'N/A')}\n"
        f"🧑‍💻 Dev Wallet: <code>{t.get('dev_wallet', 'N/A')}</code>\n"
        f"🔗 <a href='{url}'>مشاهده / خرید</a>\n\n"
        f"⚠️ فقط ورود سریع! امکان پامپ بالا وجود دارد."
    )
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

def main():
    keep_alive()
    print("🟢 ربات فعال شد.")
    while True:
        tokens = fetch_trending_tokens()
        for t in tokens:
            if (
                t['id'] not in sent_ids
                and is_recent(t['created_at'])
                and check_extra_conditions(t)
            ):
                send_alert(t)
                sent_ids.add(t['id'])
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
