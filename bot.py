import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


# ---------------------------
# SOURCE 1: arXiv (REAL)
# ---------------------------
def fetch_arxiv():
    try:
        url = (
            "http://export.arxiv.org/api/query?"
            "search_query=cat:cs.AI&"
            "start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
        )

        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return []

        root = ET.fromstring(r.text)

        ns = "{http://www.w3.org/2005/Atom}"
        papers = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title")
            if title is not None and title.text:
                papers.append("📄 " + title.text.strip().replace("\n", " "))

        return papers

    except Exception as e:
        print("arXiv error:", e)
        return []


# ---------------------------
# SOURCE 2: fallback API (always works)
# ---------------------------
def fetch_fallback():
    try:
        r = requests.get("https://api.sampleapis.com/futurama/episodes", timeout=10)
        if r.status_code != 200:
            return []

        data = r.json()

        return [f"📚 Backup item: {x['title']}" for x in data[:3]]

    except:
        return []


def main():
    print("BOT STARTED")

    send("🤖 Bot started")

    papers = fetch_arxiv()

    # اگر arXiv خالی بود → fallback
    if not papers:
        papers = fetch_fallback()

    # اگر باز هم خالی بود → غیرممکن fallback قطعی
    if not papers:
        send("💓 Bot alive | no data sources available | " + str(datetime.now()))
        return

    send(f"📚 Found {len(papers)} items:")

    for p in papers:
        send(p)

    send("✅ Done | " + str(datetime.now()))


if __name__ == "__main__":
    main()
