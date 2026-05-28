import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload, timeout=10)


def fetch_papers():
    """
    اینجا منطق مقاله‌هاست.
    فعلاً نمونه امن گذاشتم که همیشه چیزی برگرده یا fallback بده
    """

    try:
        # اینجا هر API خواستی می‌تونی بذاری
        # فعلاً نمونه تستی:

        response = requests.get("https://api.sampleapis.com/futurama/episodes", timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()

        # شبیه‌سازی مقاله
        papers = []
        for item in data[:3]:
            papers.append(f"📄 {item.get('title')}")

        return papers

    except Exception as e:
        print("ERROR:", e)
        return []


def main():
    print("BOT STARTED")

    send("🤖 Bot started successfully")

    papers = fetch_papers()

    if not papers:
        send("💓 امروز مقاله جدیدی پیدا نشد، اما سیستم سالم است (heartbeat OK).")
        return

    for p in papers:
        send(p)

    send(f"✅ ارسال کامل شد | {datetime.now()}")


if __name__ == "__main__":
    main()
