import os
from groq import Groq

MERGED_FILE = "../data/future.md"
REPORT_FILE = "../data/future_report.md"

# ✅ API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ 環境變數 GROQ_API_KEY 未設定！")

client = Groq(api_key=GROQ_API_KEY)

# ✅ 讀取合併後內容
if not os.path.exists(MERGED_FILE):
    raise FileNotFoundError(f"❌ 找不到合併檔案：{MERGED_FILE}")

with open(MERGED_FILE, "r", encoding="utf-8") as f:
    merged_content = f.read()

# ✅ Prompt 設定
prompt = f"""
你是一位專業資安趨勢分析師，以下是一週內來自不同消息來源彙整的「未來資安趨勢」相關觀察內容。

這些內容涵蓋了企業建議、技術走向、威脅演進與政策發展等面向，可能存在描述重複、措辭混亂、分類不清的問題。請協助我進行完整的整理與優化，產出可作為資安週報的「未來趨勢」段落。

請遵循以下要求：

1. 使用繁體中文。
2. 每一項趨勢請使用 `* `（星號+空格）開頭，禁止使用數字、破折號。
3. 請統整重複資訊，避免出現相同觀點以不同說法重複出現。
4. 將趨勢分類為下列面向之一（無需標題，只需依此思考統整邏輯）：
   - 技術發展（如：AI、ML、IoT、無密碼、雲端）
   - 威脅演進（如：勒索、供應鏈攻擊、惡意軟體變種）
   - 政策與產業趨勢（如：政府計畫、資安產值）
   - 組織因應建議（如：教育訓練、修補作業、CI強化）
5. 如出現具體國家、公司或技術名稱，請保留。
6. 文字要精煉具體，避免模糊詞彙如「值得注意」、「可能」、「有風險」。
7. 最終輸出須保留 `### 4. 未來趨勢` 標題，內容結構需可直接用於正式資安週報。

---

以下是原始「未來趨勢」內容：
### 4. 未來趨勢
{merged_content}
"""

# ✅ 呼叫 Groq API
try:
    print("🧠 正在產生完整資安週報...")
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "你是專業的資安新聞分析師，請協助撰寫週報。"},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
    )

    weekly_report = chat_completion.choices[0].message.content.strip()

    # ✅ 儲存輸出
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(weekly_report)

    print(f"✅ 資安週報已儲存至：{REPORT_FILE}")

except Exception as e:
    print(f"❌ 週報產生失敗：{e}")
