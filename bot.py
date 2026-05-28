import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ----------------------------
# Telegram sender
# ----------------------------
def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass


# ----------------------------
# Score system (IMPORTANT FIX)
# ----------------------------
def score(title):
    t = title.lower()

    score = 0

    strong = ["education", "school", "student", "classroom", "teaching", "learning", "secondary"]
    medium = ["ai", "assessment", "curriculum", "pedagogy"]
    weak = ["review", "study", "analysis"]

    for w in strong:
        if w in t:
            score += 5

    for w in medium:
        if w in t:
            score += 3

    for w in weak:
        if w in t:
            score += 1

    return score


# ----------------------------
# Semantic Scholar (primary source)
# ----------------------------
def semantic_search():
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": "secondary education OR classroom learning OR teaching OR student learning",
                "limit": 10,
                "fields": "title,url,year"
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
# arXiv fallback (WIDER SEARCH, not empty)
# ----------------------------
def arxiv_search():
    try:
        url = "http://export.arxiv.org/api/query?search_query=all&start=0&max_results=10"
        r = requests.get(url, timeout=15)

        root = ET.fromstring(r.text)
        ns = "{http://www.w3.org/2005/Atom}"

        results = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title")
            link = entry.find(f"{ns}id")

            if title is not None:
                results.append((score(title.text), title.text, link.text))

        return results

    except:
        return []


# ----------------------------
# MAIN AGENT LOGIC (FIXED)
# ----------------------------
def run():

    send("🤖 Research Agent started")

    results = semantic_search()

    # fallback if weak results
    if len(results) < 3:
        results += arxiv_search()

    # ALWAYS GUARANTEE OUTPUT (CRITICAL FIX)
    if not results:
        send("📡 No strong matches found — showing general education research signal")

        send("📚 Suggested area: Secondary education research + classroom learning studies")
        send("🔗 https://scholar.google.com")
        send("🔗 https://arxiv.org")
        send("⏱ " + str(datetime.now()))
        return

    # sort by score
    results.sort(key=lambda x: x[0], reverse=True)

    # remove duplicates
    seen = set()
    final = []

    for s, title, url in results:
        if title not in seen:
            final.append((title, url))
            seen.add(title)

    # OUTPUT (like your example)
    send("📚 جدیدترین مقالات آموزش متوسطه:\n")

    for i, (title, url) in enumerate(final[:5], 1):
        send(f"{i}) {title}\n📄 {url}")

    send("⏱ " + str(datetime.now()))


if __name__ == "__main__":
    run()
