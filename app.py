from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def get_cointelegraph():
    url = "https://cointelegraph.com/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    news = []
    for item in soup.select(".posts-listing__item"):  # Ana sayfa haberleri
        title = item.select_one(".post-card-inline__title")
        link = item.select_one("a")
        summary = item.select_one(".post-card-inline__text")
        date = item.select_one("time")
        news.append({
            "title": title.text.strip() if title else "",
            "url": link['href'] if link else "",
            "description": summary.text.strip() if summary else "",
            "published_at": date['datetime'] if date and date.has_attr('datetime') else ""
        })
    return news

def get_investing():
    url = "https://tr.investing.com/news/cryptocurrency-news"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "lxml")
    news = []
    for item in soup.select(".textDiv"):
        title = item.select_one("a.title")
        link = title
        summary = item.select_one("p.articleDetails")
        date = item.select_one("span.date")
        news.append({
            "title": title.text.strip() if title else "",
            "url": link['href'] if link else "",
            "description": summary.text.strip() if summary else "",
            "published_at": date.text.strip() if date else ""
        })
    return news

def get_cryptonews():
    url = "https://cryptonews.com/tr/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    news = []
    for item in soup.select(".cn-tile-row .cn-tile"):
        title = item.select_one(".cn-tile-title")
        link = item.select_one("a")
        summary = item.select_one(".cn-tile-description")
        date = item.select_one(".cn-tile-date")
        news.append({
            "title": title.text.strip() if title else "",
            "url": link['href'] if link else "",
            "description": summary.text.strip() if summary else "",
            "published_at": date.text.strip() if date else ""
        })
    return news

@app.route('/')
def index():
    news = []
    error = None
    try:
        news += get_cointelegraph()
    except Exception as e:
        error = f"Cointelegraph: {str(e)}"
    try:
        news += get_investing()
    except Exception as e:
        error = (error or "") + f" Investing: {str(e)}"
    try:
        news += get_cryptonews()
    except Exception as e:
        error = (error or "") + f" Cryptonews: {str(e)}"
    # En güncelden eskiye sırala
    def get_pub(post):
        try:
            return datetime.strptime(post['published_at'], '%Y-%m-%dT%H:%M:%SZ')
        except Exception:
            return datetime.min
    news = sorted(news, key=get_pub, reverse=True)
    return render_template('index.html', news=news, error=error)

if __name__ == '__main__':
    app.run(debug=True)
