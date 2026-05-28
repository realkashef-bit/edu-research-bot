import os
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ----------------------------
# Telegram sender
# ----------------------------
def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


# ----------------------------
# FILTER (balanced + safe)
# ----------------------------
def is_education_paper(text):
    text = (text or "").lower()

    include = [
        "education", "learning", "teaching", "student",
        "school", "classroom", "curriculum", "instruction",
        "pedagogy", "assessment"
    ]

    exclude = [
        "surgery", "clinical", "hospital", "medicine",
        "finance", "crypto", "stock", "bank"
    ]

    if any(x in text for x in exclude):
        return False

    return any(x in text for x in include)


# ----------------------------
# Semantic Scholar (MAIN)
# ----------------------------
def fetch_semantic_scholar():
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            "query": "education learning teaching classroom",
            "limit": 10,
            "fields": "title,abstract,url,year"
        }

        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return []

        data = r.json().get("data", [])
        results = []

        for p in data:
            title = p.get("title", "")
            abstract = p.get("abstract", "")
            url = p.get("url", "")

            if is_education_paper(title + " " + (abstract or "")):
                results.append(f"📄 {title}\n🔗 {url}")

        return results

    except Exception as e:
        print("Semantic Scholar error:", e)
        return []


# ----------------------------
# arXiv (backup)
# ----------------------------
def fetch_arxiv():
    try:
        url = "http://export.arxiv.org/api/query?search_query=all:education&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"

        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return []

        root = ET.fromstring(r.text)
        ns = "{http://www.w3.org/2005/Atom}"

        results = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title")
            link = entry.find(f"{ns}id")

            if title is not None and title.text:
                text = title.text.strip()

                if is_education_paper(text):
                    results.append(f"📄 {text}\n🔗 {link.text}")

        return results

    except Exception as e:
        print("arXiv error:", e)
        return []


# ----------------------------
# MAIN
# ----------------------------
def main():
    send("🤖 Research Bot started")

    papers = []

    # sources
    papers += fetch_semantic_scholar()
    papers += fetch_arxiv()

    # deduplicate
    seen = set()
    unique
