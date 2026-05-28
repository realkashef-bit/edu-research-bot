import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ----------------------------
# Telegram Sender
# ----------------------------
def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


# ----------------------------
# Semantic Scholar (MAIN SOURCE)
# ----------------------------
def fetch_semantic_scholar():
    try:
        url = (
            "https://api.semanticscholar.org/graph/v1/paper/search"
        )

        params = {
            "query": "education OR classroom OR learning OR teaching",
            "limit": 10,
            "fields": "title,abstract,year,url"
        }

        r = requests.get(url, params=params, timeout=15)

        if r.status_code != 200:
            return []

        data = r.json().get("data", [])

        papers = []
        for p in data:
            title = p.get("title", "")
            abstract = p.get("abstract", "")

            if is_valid_education_paper(title, abstract):
                link = p.get("url", "")
                papers.append(f"📄 {title}\n🔗 {link}")

        return papers

    except Exception as e:
        print("Semantic Scholar error:", e)
        return []


# ----------------------------
# arXiv (SECOND SOURCE)
# ----------------------------
def fetch_arxiv():
    try:
        url = "http://export.arxiv.org/api/query?search_query=all:education&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"

        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return []

        import xml.etree.ElementTree as ET

        root = ET.fromstring(r.text)
        ns = "{http://www.w3.org/2005/Atom}"

        papers = []

        for entry in root.findall(f"{ns}entry"):
            title = entry.find(f"{ns}title")
            link = entry.find(f"{ns}id")

            if title is not None and title.text:
                if is_valid_education_paper(title.text, ""):
                    papers.append(f"📄 {title.text.strip()}\n🔗 {link.text}")

        return papers

    except Exception as e:
        print("arXiv error:", e)
        return []


# ----------------------------
# SMART FILTER (IMPORTANT PART)
# ----------------------------
def is_valid_education_paper(title, abstract):
    text = (title + " " + abstract).lower()

    # MUST HAVE (education domain)
    positive = [
        "education", "classroom", "learning", "teaching",
        "student", "school", "pedagogy", "curriculum",
        "instruction", "assessment", "education policy"
    ]

    # MUST NOT HAVE (noise domains)
    negative = [
        "medicine", "clinical", "hospital", "physician",
        "finance", "bank", "crypto", "economic model",
        "psychology experiment", "neuroscience (clinical)"
    ]

    if any(n in text for n in negative):
        return False

    return any(p in text for p in positive)


# ----------------------------
# MAIN
# ----------------------------
def main():
    send("🤖 Research Bot started")

    papers = []

    # source 1
    papers += fetch_semantic_scholar()

    # source 2
    papers += fetch_arxiv()

    # remove duplicates
    seen = set()
    unique = []

    for p in papers:
        if p not in seen:
            unique.append(p)
            seen.add(p)

    # FINAL OUTPUT LOGIC
    if not unique:
        send("💓 No new education papers found | system healthy | " + str(datetime.now()))
        return

    send(f"📚 Found {len(unique)} research papers:\n")

    for p in unique[:8]:
        send(p)

    send("✅ Done | " + str(datetime.now()))


if __name__ == "__main__":
    main()
