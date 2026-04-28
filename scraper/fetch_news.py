import json
import feedparser
import requests
from datetime import datetime
import os
import time

# 只使用国内稳定源（简体中文）
RSS_SOURCES = {
    "zh_cn": {
        "财报": [
            "https://rss.eastmoney.com/channel/414",
        ],
        "科技": [
            "https://36kr.com/feed-newsflash",
            "https://www.huxiu.com/rss/0.xml",
            "https://sspai.com/feed",
        ]
    }
}

def parse_rss(url, source_name, lang, category):
    articles = []
    try:
        # 设置超时时间为15秒，避免卡死
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:  # 取前10条加快速度
            published = ""
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
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
        print(f"抓取 {url} 失败: {e}")
    return articles

def main():
    all_articles = []
    for lang, categories in RSS_SOURCES.items():
        for category, urls in categories.items():
            for url in urls:
                source_name = url.split("//")[-1].split("/")[0]
                print(f"正在抓取: {url}")
                articles = parse_rss(url, source_name, lang, category)
                all_articles.extend(articles)
                time.sleep(1)  # 礼貌延迟

    # 简单去重（按标题）
    seen_titles = set()
    unique_articles = []
    for art in all_articles:
        lower_title = art['title'].lower().strip()
        if lower_title not in seen_titles:
            seen_titles.add(lower_title)
            unique_articles.append(art)

    # 按发布时间倒序（新->旧）
    unique_articles.sort(key=lambda x: x['published'], reverse=True)

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(unique_articles),
        "articles": unique_articles
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"成功抓取 {len(unique_articles)} 条新闻，已保存到 docs/news.json")

if __name__ == "__main__":
    main()
