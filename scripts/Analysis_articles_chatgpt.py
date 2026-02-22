import os
from openai import OpenAI

MERGED_FILE = "../data/structured_report.json"
REPORT_FILE = "../data/structured_report_everyday.md"

# ✅ 讀取 API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ 環境變數 OPENAI_API_KEY 未設定！")

client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ 讀取資料來源
if not os.path.exists(MERGED_FILE):
    raise FileNotFoundError(f"❌ 找不到檔案：{MERGED_FILE}")

with open(MERGED_FILE, "r", encoding="utf-8") as f:
    merged_content = f.read()

# ✅ Prompt
prompt = f"""
請根據最新資安資訊，生成一份結構化報告，包含以下內容： 
1.  威脅概述：概述資安趨勢，聚焦兩岸、國內、國際威脅（如駭客攻擊、資料外洩）。必要時在括號補充技術用語（如「駭客攻擊（魚叉式攻擊）」）。若無重大事件，簡述一項具體趨勢（如某CVE漏洞）並標註「影響程度」。
2.  重大事件：摘要高影響事件（標準：影響關鍵產業如科技/醫療、涉及大量資料外洩或地緣政治風險），按「兩岸」「國內」「國際」分類（允許跨類別標註，如「國際+國內」）。為每起事件標示優先級（[緊急]：影響關鍵基礎設施如電力/通訊、超過10萬筆資料外洩或地緣政治風險，特別是中國駭客；[高]：影響關鍵產業或大量資料；[中]：局部影響；[低]：潛in風險低），並按優先級排序（緊急 > 高 > 中 > 低）每起事件包括： 
 •  事件簡述（必要時可括號補充技術用語）
 •  影響（強調與臺灣關聯的部分）
 •  風險
 •  建議（1至3條可行措施，直接回應風險，必要時括號補充技術細節）
3.  行動總結：彙總所有建議，單獨強調緊急事件的立即行動，語言簡潔，呼應事件風險。
4.  呈現方式： 
 •  總長度350-500字，使用簡單語言（優先用「駭客攻擊」「資料外洩」等詞），括號補充技術用語（如「漏洞（CVE-2025-1234）」）。
 •  結構清晰：每段以「問題-影響-風險-解決方案」邏輯呈現，緊急事件置頂，建議直接回應風險，行動總結銜接所有事件。
 •  結尾註明參考來源。
請以繁體中文生成報告，確保內容簡單明瞭，適合高階主管快速閱讀，並於結尾註明參考來源。


以下是資料來源：
{merged_content}
"""

# ✅ 呼叫 ChatGPT API
try:
    print("🧠 正在產生完整資安週報...")

    response = client.chat.completions.create(
        model="gpt-5.2",  # 或 gpt-4o-mini
        messages=[
            {"role": "system", "content": "你是一位資安專家，負責提供每日一份簡潔明瞭的資安新聞報告（我會提供資料來源），聚焦兩岸（臺灣與中國大陸）、國內（臺灣）及國際事件。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    weekly_report = response.choices[0].message.content.strip()

    # ✅ 儲存報告
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(weekly_report)

    print(f"✅ 每日資安已儲存至：{REPORT_FILE}")

except Exception as e:
    print(f"❌ 報告產生失敗：{e}")
