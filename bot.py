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


def fetch_papers():
    try:
        # arXiv API واقعی (آخرین مقالات AI / ML / CS)
        url = (
            "http://export.arxiv.org/api/query?"
            "search_query=all:machine+learning&"
            "start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
        )

        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return []

        root = ET.fromstring(r.text)
        ns = {"a": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("a:entry", ns):
            title = entry.find("a:title", ns)
            if title is not None:
                papers.append("📄 " + title.text.strip().replace("\n", " "))

        return papers

    except Exception as e:
        print("fetch error:", e)
        return []


def main():
    print("BOT STARTED")

    send("🤖 Bot started")

    papers = fetch_papers()

    if not papers:
        send("💓 Bot alive | no new papers detected | " + str(datetime.now()))
        return

    send(f"📚 Found {len(papers)} new papers:\n")

    for p in papers:
        send(p)

    send("✅ Done | " + str(datetime.now()))


if __name__ == "__main__":
    main()
