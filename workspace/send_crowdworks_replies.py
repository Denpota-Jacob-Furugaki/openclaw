"""Send CrowdWorks reply notifications via Gmail."""
import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = 'google_token.json'

def reply_to_thread(service, thread_id, subject, body):
    """Reply to an existing email thread."""
    message = MIMEText(body, 'plain', 'utf-8')
    message['To'] = 'no-reply@crowdworks.jp'
    message['From'] = 'me'
    message['Subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    try:
        # Note: Gmail won't actually send to no-reply, but we'll mark as handled
        # Real replies need to go through CrowdWorks platform
        print(f"[INFO] CrowdWorks reply drafted for thread {thread_id}")
        print(f"  Subject: {subject}")
        print(f"  Reply needs to be sent on CrowdWorks platform")
        return True
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        return False

def send_crowdworks_platform_message(url, message_text):
    """
    Send message on CrowdWorks platform using browser automation.
    Simplified version that will work with current login page.
    """
    from playwright.sync_api import sync_playwright
    import time
    
    print(f"\n[INFO] Opening CrowdWorks message: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible for now
        page = browser.new_page()
        
        # Go directly to the message URL
        page.goto(url)
        time.sleep(3)
        
        # If not logged in, it will redirect to login
        if 'login' in page.url:
            print("[INFO] Need to login - please login manually in the browser")
            print("[INFO] After login, I'll send the message")
            
            # Wait for manual login (up to 60 seconds)
            try:
                page.wait_for_url(url, timeout=60000)
                print("[OK] Logged in!")
            except:
                print("[ERROR] Login timeout. Please try again.")
                browser.close()
                return False
        
        # Now on the message page, find textarea and send
        time.sleep(2)
        
        try:
            # Try to find message textarea
            textarea = page.query_selector('textarea')
            if textarea:
                textarea.fill(message_text)
                time.sleep(1)
                
                # Find send button
                send_btn = page.query_selector('button:has-text("送信"), input[type="submit"]')
                if send_btn:
                    print(f"[INFO] Sending message...")
                    send_btn.click()
                    time.sleep(2)
                    print(f"[OK] Message sent!")
                    
                    # Take screenshot
                    page.screenshot(path=f'crowdworks_sent_{int(time.time())}.png')
                    browser.close()
                    return True
                else:
                    print("[ERROR] Could not find send button")
            else:
                print("[ERROR] Could not find message textarea")
                print("[INFO] Please send manually:")
                print(f"       URL: {url}")
                print(f"       Message: {message_text}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        input("\nPress Enter to close browser...")
        browser.close()
        return False

def main():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    service = build('gmail', 'v1', credentials=creds)
    
    # CrowdWorks messages
    messages = [
        {
            'url': 'https://crowdworks.jp/messages/400850966',
            'name': 'ALL BLUE (Most Recent)',
            'message': """ご連絡いただきありがとうございます。

オンライン面談の件、承知いたしました。
以下の日程でしたらご対応可能です：

- 3月25日（水）10:00-18:00の間
- 3月26日（木）10:00-18:00の間  
- 3月27日（金）14:00-18:00の間

ご都合の良いお時間をお知らせいただけますと幸いです。
どうぞよろしくお願いいたします。

古垣 伝法太"""
        },
        {
            'url': 'https://crowdworks.jp/messages/400778086',
            'name': 'ALL BLUE (Earlier)',
            'message': """ご連絡ありがとうございます。

プロジェクトの詳細について興味がございます。
フルスタック開発を専門としており、React/Next.js、Node.jsの実装経験が豊富です。

リモート勤務での対応は可能でしょうか？
可能であれば、ぜひ詳細についてお話しさせていただきたいです。

ポートフォリオ：https://denpota-portfolio.vercel.app/

よろしくお願いいたします。

古垣 伝法太"""
        },
        {
            'url': 'https://crowdworks.jp/messages/400762340',
            'name': 'Job35423',
            'message': """ご連絡いただきありがとうございます。

プロジェクトに興味がございます。
詳細について確認させていただきたく、お時間をいただけますと幸いです。

以下の日程でしたら対応可能です：
- 3月25日（水）以降
- 平日 10:00-18:00

ご都合の良い日時をお知らせください。

よろしくお願いいたします。

古垣 伝法太
denpotafurugaki@gmail.com"""
        }
    ]
    
    print("="*60)
    print("Sending CrowdWorks messages...")
    print("="*60)
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- Message {i}/3: {msg['name']} ---")
        success = send_crowdworks_platform_message(msg['url'], msg['message'])
        if not success:
            print(f"\n[INFO] Manual send required:")
            print(f"  URL: {msg['url']}")
            print(f"  Message ready to paste")
        
        if i < len(messages):
            print("\nMoving to next message...")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
