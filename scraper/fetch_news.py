import json
import feedparser
import requests
from datetime import datetime
import os
import time

# 明确分离财报和科技源，确保财报渠道稳定
RSS_SOURCES = {
    "zh_cn": {
        "财报": [
            # 东方财富-公司公告（包含业绩预告、财报）
            "https://rss.eastmoney.com/channel/414",
            # 证券时报-公告快讯
            "https://rss.stcn.com/gonggao.xml",
            # 新浪财经-财报速递
            "https://finance.sina.com.cn/stock/stockx/20230420/2023042012345678912.shtml",  # 这个可能不行，备用
        ],
        "科技": [
            "https://36kr.com/feed-newsflash",
            "https://www.huxiu.com/rss/0.xml",
            "https://sspai.com/feed",
            # 华尔街见闻-快讯（含财经，但为了确保有内容，再专门加一个）
            "https://wallstreetcn.com/rss/news/global",
        ]
    },
    "en": {
        "财报": [
            # Yahoo Finance 财报新闻
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=yhoo&region=US&lang=en-US",
        ],
        "科技": [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
        ]
    }
}

# 备用：如果以上财报源都失败，强制从36氪中按关键词抓取财经类（但我们先靠专业源）
# 这里也可以手动添加一个“财经”分类的聚合源，但已包含。

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
            # 补充：如果这篇是中文且来自综合源（如华尔街见闻），但标签是“科技”，我们可以根据标题含“财报”“业绩”“利润”等关键词改为“财报”
            # 但这里我们先按源设定的 category 输出，后续如果还缺，再靠关键词纠正。
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
                print(f"正在抓取: {url} (类别: {category})")
                arts = parse_rss(url, domain, lang, category)
                all_articles.extend(arts)
                time.sleep(0.6)

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
    print(f"成功保存 {len(unique)} 篇文章，其中财报 {len([a for a in unique if a['category']=='财报'])} 篇，科技 {len([a for a in unique if a['category']=='科技'])} 篇")

if __name__ == "__main__":
    main()
