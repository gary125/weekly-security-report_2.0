import json
import re
import requests
from datetime import datetime
import os

ARTICLE_LIST_PATH = "../data/news_links.json"
TARGET_ID = 1
OUTPUT_PATH = "../data/structured_report.json"

# 讀取文章清單
with open(ARTICLE_LIST_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

# 找出目標文章連結
target_link = next((a["link"] for a in articles if a["id"] == TARGET_ID), None)
if not target_link:
    raise ValueError(f"找不到 id={TARGET_ID} 的文章連結")

# 強制使用 r.jina.ai
if not target_link.startswith("https://r.jina.ai/"):
    target_link = "https://r.jina.ai/" + target_link

print("抓取網址:", target_link)

# 下載內容
response = requests.get(target_link, timeout=15)
response.raise_for_status()
md_content = response.text

# 初始化報告
report = {
    "title": "",
    "source": target_link.replace("https://r.jina.ai/", "", 1),
    "published_time": "",
    "main_article": "",
    "sections": {
        "daily_news": [],
        "other_threats": []
    }
}

# 1️⃣ 標題
title_match = re.search(r"Title:\s*(.*)", md_content)
if title_match:
    report["title"] = title_match.group(1).strip()

# 2️⃣ 發布時間
time_match = re.search(r"Published Time:\s*(.*)", md_content)
if time_match:
    published_raw = time_match.group(1).strip()
    try:
        dt = datetime.strptime(published_raw, "%a, %d %b %Y %H:%M:%S %Z")
        report["published_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        report["published_time"] = published_raw

# 3️⃣ 主文 (去掉導覽、Markdown圖片、連結)
main_split = re.split(r"\[\*\*", md_content, maxsplit=1)
if main_split:
    main_text = main_split[0]
    main_text = re.sub(r"Markdown Content:\s*", "", main_text)
    # 去掉圖片 Markdown ![...](...)
    main_text = re.sub(r"!\[.*?\]\(.*?\)", "", main_text)
    # 去掉連結 Markdown [text](url)
    main_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", main_text)
    # 去掉多餘空行
    main_text = "\n".join([line.strip() for line in main_text.splitlines() if line.strip()])
    report["main_article"] = main_text

# 4️⃣ 小新聞
event_pattern = r"\[\*\*(.*?)\*\*\]\((.*?)\)\s*\n+(.*?)(?=\n\[\*\*|\n\*\*其他資安威脅|\Z)"
events = re.findall(event_pattern, md_content, re.DOTALL)
for title, url, desc in events:
    # 提取圖片 URL
    images = re.findall(r"!\[.*?\]\((.*?)\)", desc)
    # 移除 Markdown
    desc_clean = re.sub(r"!\[.*?\]\(.*?\)", "", desc)
    desc_clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc_clean)
    desc_clean = " ".join([line.strip() for line in desc_clean.splitlines() if line.strip()])
    
    report["sections"]["daily_news"].append({
        "title": title.strip(),
        "url": url.strip(),
        "description": desc_clean,
        "images": images
    })

# 5️⃣ 其他資安威脅
other_section = re.search(r"\*\*其他資安威脅\*\*(.*?)(?=\*\*近期資安日報\*\*|\Z)", md_content, re.DOTALL)
if other_section:
    other_content = other_section.group(1)
    other_events = re.findall(r"\*\*\[(.*?)\]\((.*?)\)\*\*", other_content)
    for title, url in other_events:
        report["sections"]["other_threats"].append({
            "title": title.strip(),
            "url": url.strip()
        })

# 確保資料夾存在
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
# 輸出 JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"✅ 整理完成 id={TARGET_ID}，輸出到 {OUTPUT_PATH}")
