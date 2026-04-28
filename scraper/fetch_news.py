import json
import feedparser
import requests
from datetime import datetime
import os
import time

# 扩展的国内稳定源（中文为主，也可保留少量英文）
RSS_SOURCES = {
    "zh_cn": {
        "财报": [
            "https://rss.eastmoney.com/channel/414",       # 东方财富-财报
            "https://wallstreetcn.com/rss/news/global",    # 华尔街见闻-快讯（含财报）
        ],
        "科技": [
            "https://36kr.com/feed-newsflash",             # 36氪-快讯
            "https://www.huxiu.com/rss/0.xml",             # 虎嗅
            "https://sspai.com/feed",                      # 少数派
            "https://rss.itjuzi.com/rss",                  # IT桔子
        ]
    },
    "en": {
        "科技": [
            "https://techcrunch.com/feed/",                # TechCrunch
            "https://www.theverge.com/rss/index.xml",      # The Verge
        ]
    }
}

# Hacker News 特例
HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

def safe_request(url, timeout=10):
    try:
        return requests.get(url, timeout=timeout)
    except Exception as e:
        print(f"请求失败 {url}: {e}")
        return None

def fetch_hn():
    resp = safe_request(HN_TOP_URL)
    if not resp: return []
    try:
        top_ids = resp.json()[:8]
    except:
        return []
    articles = []
    for id in top_ids:
        item_resp = safe_request(HN_ITEM_URL.format(id), 8)
        if not item_resp: continue
        item = item_resp.json()
        if not item: continue
        articles.append({
            "title": item.get("title", "无标题"),
            "url": item.get("url", f"https://news.ycombinator.com/item?id={id}"),
            "summary": "",
            "published": datetime.fromtimestamp(item.get("time", 0)).strftime("%Y-%m-%d %H:%M") if item.get("time") else "",
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
        for entry in feed.entries[:12]:
            pub = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            summary = entry.get("summary", "").strip()
            if not title or not link:
                continue
            articles.append({
                "title": title,
                "url": link,
                "summary": summary,
                "published": pub,
                "source": source_name,
                "lang": lang,
                "category": category
            })
    except Exception as e:
        print(f"解析RSS失败 {url}: {e}")
    return articles

def main():
    all_articles = []
    for lang, categories in RSS_SOURCES.items():
        for category, urls in categories.items():
            for url in urls:
                domain = url.split("//")[-1].split("/")[0]
                print(f"正在抓取: {url}")
                arts = parse_rss(url, domain, lang, category)
                all_articles.extend(arts)
                time.sleep(0.6)

    # 添加 Hacker News（英文科技）
    if "en" in RSS_SOURCES:
        all_articles.extend(fetch_hn())

    # 去重
    seen = set()
    unique = []
    for a in all_articles:
        key = a["title"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(a)

    # 排序
    unique.sort(key=lambda x: x["published"] if x["published"] else "0", reverse=True)

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(unique),
        "articles": unique
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"成功保存 {len(unique)} 篇文章")

if __name__ == "__main__":
    main()
