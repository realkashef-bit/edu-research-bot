import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import traceback

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)

        if not r.ok:
            print("Telegram error:", r.text)

    except Exception as e:
        print("Send failed:", e)


def safe_fetch():
    try:
        url = "http://export.arxiv.org/api/query?search_query=all&start=0&max_results=10"
        r = requests.get(url, timeout=20)

        print("HTTP status:", r.status_code)

        root = ET.fromstring(r.text)
        ns = "{http://www.w3.org/2005/Atom}"

        results = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title")
            link = entry.find(f"{ns}id")

            if title is not None and link is not None:
                results.append((title.text.strip(), link.text.strip()))

        return results

    except Exception as e:
        print("FETCH ERROR:")
        traceback.print_exc()
        return []


def run():
    try:
        send("🤖 Bot started")

        results = safe_fetch()

        print("RESULT COUNT:", len(results))

        if results:
            send("📚 Papers:\n")

            for i, (title, link) in enumerate(results, 1):
                send(f"{i}) {title}\n{link}")

        else:
            send("📡 No data returned (fallback mode)")
            send("🔗 https://arxiv.org")

        send("⏱ " + str(datetime.now()))

    except Exception:
        print("CRASH:")
        traceback.print_exc()
        send("💥 Bot crashed — check logs")


if __name__ == "__main__":
    run()
