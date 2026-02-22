import os
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# ========= 寄信位置 =========
raw_receivers = os.getenv("RECEIVER_EMAILS")

# ========= 處理附件（可選） =========
raw_attachments = os.getenv("ATTACHMENT_FILES", "")

MARKDOWN_FILE = "../../data/structured_report_everyday.md"


def send_email():
    # ========= 基本檢查 =========
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ 未設定 SENDER_EMAIL 或 SENDER_PASSWORD")
        return
    
    if not raw_receivers:
        print("❌ 未設定 RECEIVER_EMAILS")
        return

    RECEIVER_EMAILS = [
        email.strip()
        for email in raw_receivers.split(",")
        if email.strip()
    ]

    if not RECEIVER_EMAILS:
        print("❌ 收件人清單為空")
        return

    if not os.path.exists(MARKDOWN_FILE):
        print(f"❌ 檔案不存在: {MARKDOWN_FILE}")
        return

    # ========= 讀取 Markdown =========
    with open(MARKDOWN_FILE, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    html_content = markdown.markdown(markdown_content)

    # ========= 建立 Email =========
    msg = MIMEMultipart("mixed")
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)
    msg["Subject"] = "📢 資安每日快訊"

    # 純文字 + HTML
    alternative_part = MIMEMultipart("alternative")

    text_part = MIMEText(markdown_content, "plain", "utf-8")
    alternative_part.attach(text_part)

    styled_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            a {{ color: #2980b9; }}
            code {{ background-color: #f4f4f4; padding: 2px 4px; }}
        </style>
    </head>
    <body>
        <h2>📢 資安每日快訊</h2>
        {html_content}
    </body>
    </html>
    """

    html_part = MIMEText(styled_html, "html", "utf-8")
    alternative_part.attach(html_part)

    msg.attach(alternative_part)

    # ========= 附件 =========    
    if raw_attachments:
        attachment_list = [
            file.strip()
            for file in raw_attachments.split(",")
            if file.strip()
        ]

        for file_path in attachment_list:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{os.path.basename(file_path)}"',
                    )
                    msg.attach(part)
            else:
                print(f"⚠️ 附件不存在: {file_path}")

    # ========= 發送 =========
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        server.sendmail(
            SENDER_EMAIL,
            RECEIVER_EMAILS,
            msg.as_string()
        )

        server.quit()
        print("✅ 每日快訊 Email 發送成功！")

    except Exception as e:
        print("❌ Email 發送失敗:", str(e))


if __name__ == "__main__":
    send_email()
