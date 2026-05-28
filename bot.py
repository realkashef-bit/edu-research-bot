import os
import requests
import hashlib
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SEEN_FILE = "seen_papers.txt"

KEYWORDS = [
    "secondary education",
    "teacher training",
    "curriculum design",
    "educational technology",
    "student assessment",
    "pedagogy",
    "learning science"
]

# ----------------------------
# Seen system
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
# AI Summary (optional GPT)
# ----------------------------
def summarize(title, abstract):
    text = (title or "") + "\n" + (abstract or "")

    if OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Summarize academic papers in simple Persian in 3-5 lines."
                    },
                    {
                        "role": "user",
                        "content": text[:2000]
                    }
                ]
            }

            r = requests.post(url, json=payload, headers=headers).json()
            return r["choices"][0]["message"]["content"]

        except:
            pass

    # fallback
    if abstract:
        sentences = [s.strip() for s in abstract.split(".") if len(s.strip()) > 40]
        return sentences[0][:300] if sentences else abstract[:200]

    return "خلاصه در دسترس نیست."

# ----------------------------
# Category detection
# ----------------------------
def category(title):
    t = (title or "").lower()

    if "teacher" in t:
        return "👩‍🏫 Teacher Training"
    if "curriculum" in t:
        return "📘 Curriculum Design"
    if "assessment" in t:
        return "📊 Assessment"
    if "technology" in t:
        return "💻 Educational Technology"
    if "learning" in t:
        return "🧠 Learning Science"

    return "🎓 General Education"

# ----------------------------
# Quality score
# ----------------------------
def score(title, abstract, year):
    s = 0

    if year and year >= datetime.now().year - 1:
        s += 3
    if abstract:
        s += 2
    if title and len(title) > 25:
        s += 1

    keywords = ["education", "teaching", "learning", "school"]
    if any(k in (title or "").lower() for k in keywords):
        s += 2

    return s

# ----------------------------
# Fetch from Semantic Scholar
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

        r = requests.get(url, params=params).json()

        for p in r.get("data", []):
            results.append({
                "title": p.get("title"),
                "abstract": p.get("abstract"),
                "url": p.get("url"),
                "pdf": (p.get("openAccessPdf") or {}).get("url"),
                "year": p.get("year")
            })

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

        if p["score"] >= 5:
            new_papers.append(p)

    save_seen(seen)

    if not new_papers:
        send("📚 امروز مقاله جدید و باکیفیت پیدا نشد.")
        return

    new_papers.sort(key=lambda x: x["score"], reverse=True)

    msg = "📊 گزارش نهایی پژوهش آموزش متوسطه\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"

    for i, p in enumerate(new_papers[:10], 1):

        msg += f"📚 {i}) {p['title']}\n"
        msg += f"{category(p['title'])}\n"
        msg += f"⭐ امتیاز: {p['score']}/6\n"
        msg += f"🧠 {summarize(p['title'], p['abstract'])}\n"
        msg += f"📄 PDF: {p.get('pdf')}\n"
        msg += f"🔗 {p.get('url')}\n"
        msg += "────────────────────\n\n"

    send(msg)

if __name__ == "__main__":
    main()
