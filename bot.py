import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def search_articles():
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": "secondary education OR high school education OR pedagogy OR curriculum OR teacher training",
        "limit": 5,
        "fields": "title,openAccessPdf,url,year"
    }

    r = requests.get(url, params=params).json()

    results = []
    for paper in r.get("data", []):
        pdf = None
        if paper.get("openAccessPdf"):
            pdf = paper["openAccessPdf"].get("url")

        if pdf:
            results.append({
                "title": paper.get("title"),
                "pdf": pdf
            })
    return results

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def main():
    articles = search_articles()

    if not articles:
        send_message("امروز مقاله رایگان جدیدی پیدا نشد.")
        return

    msg = "📚 جدیدترین مقالات آموزش متوسطه:\n\n"

    for i, a in enumerate(articles, 1):
        msg += f"{i}) {a['title']}\n📄 PDF: {a['pdf']}\n\n"

    send_message(msg)

if __name__ == "__main__":
    main()
