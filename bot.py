import os
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ----------------------------
# TELEGRAM
# ----------------------------
def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass


# ----------------------------
# AGENT: generates search queries dynamically
# ----------------------------
def generate_queries():
    base_topics = [
        "education research",
        "learning science",
        "classroom teaching methods",
        "AI in education",
        "student performance study"
    ]

    return base_topics


# ----------------------------
# Semantic Scholar (smart search)
# ----------------------------
def fetch_semantic(query):
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": query,
                "limit": 5,
                "fields": "title,url,year"
            },
            timeout=15
        )

        data = r.json().get("data", [])
        results = []

        for p in data:
            title = p.get("title")
            url = p.get("url")

            if title and url:
                score = score_paper(title)
                results.append((score, f"📘 {title}\n🔗 {url}"))

        return results

    except:
        return []


# ----------------------------
# arXiv fallback
# ----------------------------
def fetch_arxiv():
    try:
        url = "http://export.arxiv.org/api/query?search_query=all&start=0&max_results=5&sortBy=submittedDate"

        r = requests.get(url, timeout=15)
        root = ET.fromstring(r.text)

        ns = "{http://www.w3.org/2005/Atom}"

        results = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title")
            link = entry.find(f"{ns}id")

            if title is not None:
                score = score_paper(title.text)
                results.append((score, f"📄 {title.text}\n🔗 {link.text}"))

        return results

    except:
        return []


# ----------------------------
# SIMPLE RELEVANCE SCORER (AGENT BRAIN)
# ----------------------------
def score_paper(text):
    text = text.lower()

    score = 0

    keywords = {
        "education": 5,
        "learning": 4,
        "teaching": 4,
        "student": 3,
        "classroom": 3,
        "ai": 2,
        "machine learning": 2
    }

    for k, v in keywords.items():
        if k in text:
            score += v

    return score


# ----------------------------
# AGENT CORE LOOP
# ----------------------------
def run_agent():
    send("🤖 Research Agent started")

    queries = generate_queries()

    all_results = []

    for q in queries:
        all_results += fetch_semantic(q)

    all_results += fetch_arxiv()

    # sort by relevance score
    all_results.sort(key=lambda x: x[0], reverse=True)

    # remove duplicates
    seen = set()
    final = []

    for score, item in all_results:
        if item not in seen:
            final.append(item)
            seen.add(item)

    # OUTPUT POLICY (NO EMPTY OUTPUT EVER)
    if final:
        send(f"📚 Agent found {len(final)} ranked papers:\n")

        for f in final[:10]:
            send(f)

        send("✅ Agent cycle complete | " + str(datetime.now()))
    else:
        send("💓 Agent active | no strong matches this cycle | " + str(datetime.now()))


if __name__ == "__main__":
    run_agent()
