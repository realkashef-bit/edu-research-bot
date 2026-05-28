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
    except:
        pass


# ----------------------------
# Simple scorer (optional)
# ----------------------------
def score(text):
    t = text.lower()
    keywords = ["education", "learning", "student", "school", "teaching", "classroom"]
    return sum(3 for k in keywords if k in t)


# ----------------------------
# Semantic Scholar
# ----------------------------
def semantic():
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": "education learning teaching",
                "limit": 5,
                "fields": "title,url"
            },
            timeout=15
        )

        data = r.json().get("data", [])
        results = []

        for p in data:
            title = p.get("title")
            url = p.get("url")

            if title:
                results.append((score(title), title, url))

        return results

    except:
        return []


# ----------------------------
# arXiv fallback
# ----------------------------
def arxiv():
    try:
        r = requests.get(
            "http://export.arxiv.org/api/query?search_query=all&start=0&max_results=5",
            timeout=15
        )

        root = ET.fromstring(r.text)
        ns = "{http://www.w3.org/2005/Atom}"

        results = []

        for e in root.findall(f"{ns}entry"):
            title = e.find(f"{ns}title")
            link = e.find(f"{ns}id")

            if title is not None:
                results.append((score(title.text), title.text, link.text))

        return results

    except:
        return []


# ----------------------------
# GUARANTEED OUTPUT BLOCK
# ----------------------------
def fallback_output():
    send("📡 No new strong matches found today")
    send("📚 But here are active research sources you can still explore:")
    send("1) https://scholar.google.com")
    send("2) https://arxiv.org")
    send("3) https://www.semanticscholar.org")
    send("🧠 Tip: Try broader query like 'education AI learning study'")
    send("⏱ " + str(datetime.now()))


# ----------------------------
# MAIN
# ----------------------------
def run():

    send("🤖 Research Bot started")

    results = semantic()

    if len(results) < 2:
        results += arxiv()

    # اگر هنوز هم چیزی نبود → باز هم خروجی می‌دهیم
    if not results:
        fallback_output()
        return

    # sort
    results.sort(key=lambda x: x[0], reverse=True)

    # remove duplicates
    seen = set()
    final = []

    for _, title, url in results:
        if title not in seen:
            final.append((title, url))
            seen.add(title)

    # OUTPUT
    send("📚 Latest Education Papers:\n")

    for i, (title, url) in enumerate(final[:5], 1):
        send(f"{i}) {title}\n📄 {url}")

    send("⏱ " + str(datetime.now()))


if __name__ == "__main__":
    run()
