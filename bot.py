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
    except:
        pass


# ----------------------------
# Semantic Scholar (NO FILTER)
# ----------------------------
def fetch_semantic():
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": "education OR learning OR teaching OR science OR medicine OR finance",
                "limit": 10,
                "fields": "title,url"
            },
            timeout=15
        )

        data = r.json().get("data", [])
        results = []

        for p in data:
            title = p.get("title", "")
            url = p.get("url", "")

            if title:
                results.append(f"📘 {title}\n🔗 {url}")

        return results

    except:
        return []


# ----------------------------
# arXiv (NO FILTER)
# ----------------------------
def fetch_arxiv():
    try:
        url = "http://export.arxiv.org/api/query?search_query=all&start=0&max_results=5"

        r = requests.get(url, timeout=15)
        root = ET.fromstring(r.text)

        ns = "{http://www.w3.org/2005/Atom}"
        results = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title")
            link = entry.find(f"{ns}id")

            if title is not None:
                results.append(f"📄 {title.text}\n🔗 {link.text}")

        return results

    except:
        return []


# ----------------------------
# MAIN (NO FILTER LOGIC)
# ----------------------------
def main():
    send("🤖 Loose Research Bot started")

    results = []
    results += fetch_semantic()
    results += fetch_arxiv()

    if not results:
        send("💓 Bot alive | no data returned | " + str(datetime.now()))
        return

    send(f"📚 Found {len(results)} mixed papers:\n")

    for r in results[:15]:
        send(r)

    send("✅ Done | " + str(datetime.now()))


if __name__ == "__main__":
    main()
