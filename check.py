import requests
from bs4 import BeautifulSoup
import hashlib
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://www.transitbus.co.jp/rosen/"
STATE_FILE = "last_hash.txt"

# メール設定（Gmailを例に）
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

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

def main():
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