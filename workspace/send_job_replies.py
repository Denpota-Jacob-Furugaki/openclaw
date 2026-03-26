"""Send job reply emails via Gmail API."""
import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'google_token.json'

def send_email(service, to, subject, body):
    """Send an email via Gmail API."""
    message = MIMEText(body, 'plain', 'utf-8')
    message['To'] = to
    message['From'] = 'me'
    message['Subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        print(f"[OK] Sent email to {to}")
        print(f"  Message ID: {sent_message['id']}")
        return sent_message
    except Exception as e:
        print(f"[ERROR] Failed to send to {to}: {e}")
        return None

def main():
    # Authenticate
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('gmail', 'v1', credentials=creds)
    
    # Workship reply
    workship_to = "izumi_haruka@giginc.co.jp"
    workship_subject = "Re: 【Workship】【 TypeScript / Node.js / 週5日 / フルリモート可 / 時給3,800円 〜 5000円】"
    workship_body = """泉様

お世話になっております。古垣 伝法太（ふるがき でんぽうた）と申します。

ゴルフ場レストランオーダーシステムのバックエンド開発案件について、大変興味がございます。

TypeScript/Node.jsを使用したバックエンド開発の経験があり、特に以下の点で貢献できると考えております：

- フルスタック開発経験（React/Next.js + Node.js）
- API設計・実装の実績
- クラウド環境での開発経験

フルリモート勤務とのことで、リモート環境での開発体制も整っております。

ぜひ詳細についてお話しさせていただきたく、カジュアル面談の機会をいただけますと幸いです。

ポートフォリオ：https://denpota-portfolio.vercel.app/

何卒よろしくお願いいたします。

---
古垣 伝法太（ふるがき でんぽうた）
Email: denpotafurugaki@gmail.com
Phone: 080-2466-0377"""
    
    print("Sending Workship reply...")
    send_email(service, workship_to, workship_subject, workship_body)
    
    print("\n" + "="*50)
    print("CrowdWorks messages need to be sent ON the platform.")
    print("Opening browser to send those...")
    print("="*50)

if __name__ == "__main__":
    main()
