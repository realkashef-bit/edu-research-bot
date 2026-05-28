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
# Safe Telegram sender (CRITICAL)
# ----------------------------
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        # اگر تلگرام هم fail شد → هیچ کاری نمی‌تونیم بکنیم
        pass

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
# Fetch safe
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
# fallback content (CRITICAL)
# ----------------------------
def fallback():
    return [
        "Digital transformation in education",
        "Modern teacher training methods",
        "Curriculum innovation trends",
        "AI in classroom learning",
        "Student evaluation systems",
        "Behavior management in schools"
    ]

# ----------------------------
# summary safe
# ----------------------------
def summary(text):
    try:
        if not text:
            return "خلاصه در دسترس نیست."
        parts = [p.strip() for p in text.split(".") if len(p.strip()) > 30]
        return parts[0][:250] if parts else text[:200]
    except:
        return "خلاصه قابل نمایش نیست."

# ----------------------------
# MAIN SAFE FLOW
# ----------------------------
def main():
    try:
        seen = load_seen()
        papers = fetch()

        new_items = []

        # filter duplicates
        for p in papers:
            id_ = uid(p.get("title"), p.get("url"))

            if id_ in seen:
                continue

            seen.add(id_)
            new_items.append(p)

        save_seen(seen)

        # =========================
        # CASE 1: real papers exist
        # =========================
        if len(new_items) > 0:
            msg = "📊 گزارش پژوهشی آموزش متوسطه\n"
            msg += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"

            for i, p in enumerate(new_items[:8], 1):
                msg += f"📚 {i}) {p.get('title')}\n"
                msg += f"🧠 {summary(p.get('abstract'))}\n"
                msg += f"📄 {p.get('pdf')}\n"
                msg += f"🔗 {p.get('url')}\n"
                msg += "────────────────────\n\n"

            send(msg)
            return

        # =========================
        # CASE 2: fallback mode
        # =========================
        msg = "📊 گزارش پژوهشی (حالت جایگزین)\n"
        msg += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        msg += "📚 مقاله مستقیم پیدا نشد، اما موضوعات مهم پژوهشی:\n\n"

        for i, t in enumerate(fallback(), 1):
            msg += f"{i}) {t}\n"

        msg += "\n🔎 سیستم در حال پایش منابع جدید است."
        send(msg)
        return

    except Exception as e:
        # =========================
        # CASE 3: EMERGENCY MODE
        # =========================
        try:
            send(
                "🚨 گزارش اضطراری سیستم\n\n"
                "ربات با خطا مواجه شد اما همچنان فعال است.\n"
                "🔄 در اجرای بعدی دوباره تلاش می‌شود.\n"
            )
        except:
            pass

if __name__ == "__main__":
    main()
