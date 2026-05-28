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
# Telegram safe send (always safe)
# ----------------------------
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        pass  # حتی اگر تلگرام مشکل داشت، کرش نکن

# ----------------------------
# Seen system
# ----------------------------
def load_seen():
    try:
        if not os.path.exists(SEEN_FILE):
            return set()
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f)
    except:
        return set()

def save_seen(seen):
    try:
        with open(SEEN_FILE, "w") as f:
            for s in seen:
                f.write(s + "\n")
    except:
        pass

def uid(title, url):
    return hashlib.md5((str(title) + str(url)).encode()).hexdigest()

# ----------------------------
# Fetch papers
# ----------------------------
def fetch():
    results = []
    for q in KEYWORDS:
        try:
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

        except:
            continue

    return results

# ----------------------------
# fallback topics
# ----------------------------
def fallback_topics():
    return [
        "AI in education",
        "Curriculum innovation",
        "Teacher training methods",
        "Student assessment systems",
        "Digital learning in schools"
    ]

# ----------------------------
# summary
# ----------------------------
def summary(text):
    if not text:
        return "خلاصه در دسترس نیست."
    parts = [p.strip() for p in text.split(".") if len(p.strip()) > 30]
    return parts[0][:250] if parts else text[:200]

# ----------------------------
# MAIN
# ----------------------------
def main():
    try:
        seen = load_seen()
        papers = fetch()

        new_papers = []

        for p in papers:
            id_ = uid(p.get("title"), p.get("url"))

            if id_ in seen:
                continue

            seen.add(id_)
            new_papers.append(p)

        save_seen(seen)

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # =========================
        # CASE 1: has papers
        # =========================
        if len(new_papers) > 0:
            msg = "📊 گزارش پژوهشی آموزش متوسطه\n"
            msg += f"📅 {now}\n\n"

            for i, p in enumerate(new_papers[:8], 1):
                msg += f"📚 {i}) {p.get('title')}\n"
                msg += f"🧠 {summary(p.get('abstract'))}\n"
                msg += f"📄 {p.get('pdf')}\n"
                msg += f"🔗 {p.get('url')}\n"
                msg += "────────────────────\n\n"

            send(msg)
            return

        # =========================
        # CASE 2: HEARTBEAT (IMPORTANT FIX)
        # =========================
        msg = "💓 HEARTBEAT REPORT\n"
        msg += f"📅 {now}\n\n"
        msg += "📚 امروز مقاله جدیدی پیدا نشد.\n\n"
        msg += "🔎 موضوعات پیشنهادی برای تحقیق:\n\n"

        for i, t in enumerate(fallback_topics(), 1):
            msg += f"{i}) {t}\n"

        msg += "\n✅ سیستم فعال و در حال پایش منابع است."

        send(msg)

    except Exception as e:
        # =========================
        # EMERGENCY HEARTBEAT
        # =========================
        send(
            "🚨 EMERGENCY HEARTBEAT\n\n"
            "سیستم اجرا شد اما با خطای داخلی مواجه شد.\n"
            "🔄 در اجرای بعدی دوباره تلاش خواهد شد.\n"
        )

if __name__ == "__main__":
    main()
