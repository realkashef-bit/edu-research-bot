import os
import requests
import hashlib
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEEN_FILE = "seen_papers.txt"

# ----------------------------
# Keywords (balanced)
# ----------------------------
KEYWORDS = [
    "education",
    "secondary school",
    "teaching learning",
    "teacher education",
    "curriculum",
    "assessment",
    "pedagogy",
    "classroom management",
    "educational technology"
]

# ----------------------------
# Seen system (anti-duplicate)
# ----------------------------
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for s in seen:
            f.write(s + "\n")

def make_id(title, url):
    return hashlib.sha256((title + url).encode()).hexdigest()

# ----------------------------
# Score system (soft)
# ----------------------------
def score(title, abstract, year):
    s = 0

    if year and year >= datetime.now().year - 1:
        s += 2
    if abstract:
        s += 1
    if title and len(title) > 20:
        s += 1

    keywords = ["education", "learning", "teaching", "school", "curriculum"]
    if any(k in (title or "").lower() for k in keywords):
        s += 2

    return s

# ----------------------------
# Smart summary (safe fallback)
# ----------------------------
def summarize(abstract):
    if not abstract:
        return "خلاصه در دسترس نیست."

    sentences = [s.strip() for s in abstract.split(".") if len(s.strip()) > 30]
    if sentences:
        return sentences[0][:300]
    return abstract[:200]

# ----------------------------
# Fetch papers (Semantic Scholar)
# ----------------------------
def fetch():
    results = []

    for q in KEYWORDS:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            "query": q,
            "limit": 5,
            "fields": "title,abstract,year,url,openAccessPdf"
        }

        try:
            r = requests.get(url, params=params, timeout=10).json()

            for p in r.get("data", []):
                results.append({
                    "title": p.get("title"),
                    "abstract": p.get("abstract"),
                    "url": p.get("url"),
                    "pdf": (p.get("openAccessPdf") or {}).get("url"),
                    "year": p.get("year")
                })
        except:
            continue

    return results

# ----------------------------
# Telegram send
# ----------------------------
def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# ----------------------------
# MAIN
# ----------------------------
def main():
    seen = load_seen()
    papers = fetch()

    new_papers = []

    for p in papers:
        uid = make_id(p["title"], p["url"])

        if uid in seen:
            continue

        seen.add(uid)

        p["score"] = score(p["title"], p["abstract"], p["year"])

        # نرم شده: خیلی سخت‌گیر نیست
        if p["score"] >= 2:
            new_papers.append(p)

    save_seen(seen)

    # ----------------------------
    # NO EMPTY OUTPUT MODE (IMPORTANT)
    # ----------------------------
    if not new_papers:
        msg = "📊 گزارش پژوهشی آموزش متوسطه\n\n"
        msg += "📚 امروز مقاله مستقیم کافی پیدا نشد.\n\n"
        msg += "🔎 موضوعات پیشنهادی برای تحقیق:\n\n"

        fallback_topics = [
            "Teacher training in modern education systems",
            "Digital learning in secondary schools",
            "Curriculum design and
