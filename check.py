import requests
from bs4 import BeautifulSoup
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
import sys
from dotenv import load_dotenv

URL = "https://www.transitbus.co.jp/rosen/"
STATE_FILE = "last_hash.txt"

# メール設定
# Actions実行時は環境変数が渡されるので.envは不要
if os.getenv("GITHUB_ACTIONS") != "true":
    print("Loading .env.development...")
    load_dotenv(".env.development")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

def validate_config():
    missing = []
    if not EMAIL_ADDRESS:
        missing.append("EMAIL_ADDRESS")
    if not EMAIL_PASSWORD:
        missing.append("EMAIL_PASSWORD")
    if not TO_EMAIL:
        missing.append("TO_EMAIL")
    
    if missing:
        print(f"❌ Missing required configurations: {', '.join(missing)}")
        sys.exit(1)

def get_page_hash():
    res = requests.get(URL)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # お知らせ部分だけを取得（必要に応じて調整）
    news_section = soup.find('div', class_='main_content')  # ← クラス名等、実際にHTMLを確認して修正
    content = news_section.get_text(strip=True) if news_section else ''
    
    return hashlib.sha256(content.encode()).hexdigest()

def load_last_hash():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, 'r') as f:
        return f.read().strip()

def save_hash(hash_value):
    with open(STATE_FILE, 'w') as f:
        f.write(hash_value)

def send_email():
    msg = MIMEText(f"{URL} のお知らせが更新されました！")
    msg['Subject'] = '【通知】バス情報更新'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL

    with smtplib.SMTP_SSL('smtp.163.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print(f"✅ メール送信完了: {TO_EMAIL}")

def main():
    validate_config()

    current_hash = get_page_hash()
    last_hash = load_last_hash()
    
    if current_hash != last_hash:
        print("更新を検知しました！")
        send_email()
        save_hash(current_hash)
    else:
        print("変更はありませんでした。")

if __name__ == "__main__":
    main()