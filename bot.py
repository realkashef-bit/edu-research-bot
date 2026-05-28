import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ----------------------------
# Telegram sender (safe)
# ----------------------------
def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Send error:", e)


# ----------------------------
# Simple relevance filter
# ----------------------------
KEYWORDS = [
    "education",
    "learning",
    "teaching",
    "student",
    "classroom",
    "school"
]


def is_relevant(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)


# ----------------------------
# Fetch arXiv (stable source)
# ----------------------------
def fetch_arxiv():
    url = "http://export.arxiv.org/api/query?search_query=all&start=0&max_results=15"

    try:
        r = requests.get(url, timeout=20)
        root = ET.fromstring(r.text)

        ns = "{http://www.w3.org/2005/Atom}"

        results = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title").text.strip()
            link = entry.find(f"{ns}id").text.strip()

            if is_relevant(title):
                results.append((title, link))

        return results

    except Exception as e:
        print("Fetch error:", e)
        return []


# ----------------------------
# MAIN LOGIC (NO EMPTY OUTPUT EVER)
# ----------------------------
def run():

    send("🤖 Daily Research Bot Started")

    results = fetch_arxiv()

    # remove duplicates
    seen = set()
    final = []

    for title, link in results:
        if title not in seen:
            final.append((title, link))
            seen.add(title)

    # ----------------------------
    # OUTPUT RULE (IMPORTANT)
    # ----------------------------
    if final:
        send("📚 جدیدترین مقالات آموزشی:\n")

        for i, (title, link) in enumerate(final[:7], 1):
            send(f"{i}) {title}\n📄 {link}")

        send("✅ پایان گزارش")
        send("⏱ " + str(datetime.now()))

    else:
        # GUARANTEED OUTPUT (NO FAILURE STATE)
        send("📡 امروز مقاله آموزشی جدید پیدا نشد")
        send("")
        send("🔎 اما منابع همیشه فعال:")
        send("https://arxiv.org")
        send("https://scholar.google.com")
        send("")
        send("💡 پیشنهاد جستجو: education learning teaching")
        send("⏱ " + str(datetime.now()))


if __name__ == "__main__":
    run()
