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
# RAW ARXIV FEED (NO FILTER AT ALL)
# ----------------------------
def fetch_arxiv():
    url = "http://export.arxiv.org/api/query?search_query=all&start=0&max_results=10"

    r = requests.get(url, timeout=20)
    root = ET.fromstring(r.text)

    ns = "{http://www.w3.org/2005/Atom}"

    results = []

    for entry in root.findall(f"{ns}entry"):
        title = entry.find(f"{ns}title").text.strip()
        link = entry.find(f"{ns}id").text.strip()

        results.append((title, link))

    return results


def run():
    send("🤖 Raw Research Feed Started")

    results = fetch_arxiv()

    if results:
        send("📚 Latest papers (NO FILTER):\n")

        for i, (title, link) in enumerate(results, 1):
            send(f"{i}) {title}\n{link}")

    else:
        # still never empty
        send("📡 No data returned from source")
        send("🔗 https://arxiv.org")

    send("⏱ " + str(datetime.now()))


if __name__ == "__main__":
    run()
