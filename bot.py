import os
import requests
import hashlib
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SEEN_FILE = "seen_papers.txt"

KEYWORDS = [
    "education",
    "teaching learning",
    "secondary school",
    "teacher training",
    "curriculum",
    "assessment",
    "pedagogy"
]

# ----------------------------
# LOG helper (IMPORTANT)
# ----------------------------
def log(msg):
    print(f"[LOG] {msg}")

# ----------------------------
# Safe Telegram send
# ----------------------------
def send(msg):
    try:
        log("Sending message to Telegram...")
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
        log(f"Telegram response: {r.text}")
    except Exception as e:
        log(f"Telegram ERROR: {e}")

# ----------------------------
# Seen system
# ----------------------------
def load_seen():
    try:
        if not os.path.exists(SEEN_FILE):
            return set()
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f)
    except Exception as e:
        log(f"Seen load error: {e}")
        return set()

def save_seen(seen):
    try:
        with open(SEEN_FILE, "w") as f:
            for s in seen:
                f.write(s + "\n")
    except Exception as e:
        log(f"Seen save error: {e}")

def uid(title, url):
    return hashlib.md5((str(title) + str(url)).encode()).hexdigest()

# ----------------------------
# Fetch papers
# ----------------------------
def fetch():
    results = []

    for q in KEYWORDS:
        try:
            log(f"Fetching: {q}")

            r = requests.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={
                    "query": q,
                    "limit": 5,
                    "fields": "title,abstract,year,url,openAccessPdf"
                },
                timeout=10
            ).json()

            for p in r.get("data", []):
                results.append({
                    "title": p.get("title"),
                    "abstract": p.get("abstract"),
                    "url": p.get("url"),
                    "pdf": (p.get("openAccessPdf") or {}).get("url")
                })

        except Exception as e:
            log(f"Fetch error: {e}")
            continue

    return results

# ----------------------------
# fallback topics
# ----------------------------
def fallback_topics():
    return [
        "AI in education systems",
        "Curriculum modernization trends",
        "Teacher training improvements",
        "Student assessment methods",
        "Digital learning in schools"
    ]

# ----------------------------
# summary
# ----------------------------
def summary(text):
    try:
        if not text:
            return "خلاصه در دسترس نیست."
        parts = [p.strip() for p in text.split(".") if len(p.strip()) > 30]
        return parts[0][:250] if parts else text[:200]
    except:
        return "خلاصه خطا دارد."

# ----------------------------
# MAIN
# ----------------------------
def main():
    log("BOT STARTED")

    try:
        seen = load_seen()
        papers = fetch()

        log(f"Total fetched papers: {len(papers)}")

        new_papers = []

        for p in papers:
            id_ = uid(p.get("title"), p.get("url"))

            if id_ in seen:
                continue

            seen.add(id_)
            new_papers.append(p)

        save_seen(seen)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # ----------------------------
        # CASE 1: papers exist
        # ----------------------------
        if new_papers:
            msg = "📊 گزارش پژوهشی آموزش متوسطه\n"
            msg += f"📅 {now}\n\n"

            for i, p in enumerate(new_papers[:8], 1):
                msg += f"📚 {i}) {p.get('title')}\n"
                msg += f"🧠 {summary(p.get('abstract'))}\n"
                msg += f"📄 {p.get('pdf')}\n"
                msg += f"🔗 {p.get('url')}\n"
                msg += "────────────────────\n\n"

            send(msg)
            log("Report sent successfully")
            return

        # ----------------------------
        # CASE 2: HEARTBEAT (GUARANTEED)
        # ----------------------------
        msg = "💓 HEARTBEAT REPORT\n"
        msg += f"📅 {now}\n\n"
        msg += "📚 مقاله مستقیم پیدا نشد.\n\n"
        msg += "🔎 موضوعات پیشنهادی:\n\n"

        for i, t in enumerate(fallback_topics(), 1):
            msg += f"{i}) {t}\n"

        msg += "\n✅ سیستم فعال است و در حال پایش می‌باشد."

        send(msg)
        log("Heartbeat sent successfully")

    except Exception as e:
        log(f"CRITICAL ERROR: {e}")

        try:
            send(
                "🚨 CRITICAL HEARTBEAT\n\n"
                "سیستم اجرا شد اما خطای جدی رخ داد.\n"
                "🔄 تلاش بعدی انجام خواهد شد."
            )
        except:
            log("Even emergency send failed")

if __name__ == "__main__":
    main()
