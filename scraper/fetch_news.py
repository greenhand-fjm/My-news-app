import json
import feedparser
import requests
from datetime import datetime
import os
import time

RSS_SOURCES = {
    "zh_cn": {
        "财报": [
            "https://rss.eastmoney.com/channel/414",
        ],
        "科技": [
            "https://36kr.com/feed-newsflash",
            "https://www.huxiu.com/rss/0.xml",
        ]
    },
    "en": {
        "财报": [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=yhoo&region=US&lang=en-US",
        ],
        "科技": [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
        ]
    }
}

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

def fetch_hn():
    top_ids = requests.get(HN_TOP_STORIES_URL).json()[:10]
    articles = []
    for id in top_ids:
        item = requests.get(HN_ITEM_URL.format(id)).json()
        articles.append({
            "title": item.get("title"),
            "url": item.get("url", f"https://news.ycombinator.com/item?id={id}"),
            "summary": "",
            "published": datetime.fromtimestamp(item.get("time")).strftime("%Y-%m-%d %H:%M"),
            "source": "Hacker News",
            "lang": "en",
            "category": "科技"
        })
        time.sleep(0.1)
    return articles

def parse_rss(url, source_name, lang, category):
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M") if hasattr(entry, 'published_parsed') else ""
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "summary": entry.get("summary", ""),
                "published": published,
                "source": source_name,
                "lang": lang,
                "category": category
            })
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return articles

def main():
    all_articles = []
    for lang, categories in RSS_SOURCES.items():
        for category, urls in categories.items():
            for url in urls:
                source_name = url.split("//")[-1].split("/")[0]
                articles = parse_rss(url, source_name, lang, category)
                all_articles.extend(articles)
                time.sleep(0.5)

    if "en" in RSS_SOURCES:
        all_articles.extend(fetch_hn())

    seen_titles = set()
    unique_articles = []
    for art in all_articles:
        lower_title = art['title'].lower().strip()
        if lower_title not in seen_titles:
            seen_titles.add(lower_title)
            unique_articles.append(art)

    unique_articles.sort(key=lambda x: x['published'], reverse=True)

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(unique_articles),
        "articles": unique_articles
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(unique_articles)} articles to docs/news.json")

if __name__ == "__main__":
    main()
