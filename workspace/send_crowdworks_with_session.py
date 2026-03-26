"""
Send CrowdWorks messages using existing browser session
"""
import os
import time
from playwright.sync_api import sync_playwright
from pathlib import Path

SESSION_DIR = Path("C:/Users/denpo/CascadeProjects/my-first-ai-agent/crowdworks_session")

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

def send_message(context, url, message_text, name):
    """Send a message on CrowdWorks using existing session."""
    print(f"\n[INFO] Sending: {name}")
    print(f"[INFO] URL: {url}")
    
    page = context.new_page()
    
    try:
        # Navigate to message URL
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)
        
        # Check if logged in (if redirects to login, session expired)
        if 'login' in page.url:
            print("[ERROR] Session expired, need to re-login")
            page.screenshot(path=f'crowdworks_session_expired_{int(time.time())}.png')
            return False
        
        print("[OK] Logged in with existing session")
        
        # Find and fill textarea
        print("[INFO] Looking for message textarea...")
        
        textarea_selectors = [
            'textarea',
            'textarea[name="message"]',
            'textarea[placeholder*="メッセージ"]',
            '[contenteditable="true"]'
        ]
        
        textarea_found = False
        for selector in textarea_selectors:
            textareas = page.query_selector_all(selector)
            for textarea in textareas:
                if textarea.is_visible():
                    try:
                        textarea.fill(message_text)
                        textarea_found = True
                        print(f"[OK] Filled message with selector: {selector}")
                        break
                    except:
                        continue
            if textarea_found:
                break
        
        if not textarea_found:
            print("[ERROR] Could not find message textarea")
            page.screenshot(path=f'crowdworks_no_textarea_{name.replace(" ", "_")}.png')
            return False
        
        time.sleep(2)
        
        # Find and click send button
        print("[INFO] Looking for send button...")
        
        send_selectors = [
            'button:has-text("送信")',
            'input[value*="送信"]',
            'button[type="submit"]',
            'input[type="submit"]'
        ]
        
        send_clicked = False
        for selector in send_selectors:
            buttons = page.query_selector_all(selector)
            for button in buttons:
                if button.is_visible():
                    try:
                        button.click()
                        send_clicked = True
                        print(f"[OK] Clicked send with selector: {selector}")
                        break
                    except:
                        continue
            if send_clicked:
                break
        
        if not send_clicked:
            print("[ERROR] Could not find send button")
            page.screenshot(path=f'crowdworks_no_send_{name.replace(" ", "_")}.png')
            return False
        
        time.sleep(3)
        
        # Take confirmation screenshot
        page.screenshot(path=f'crowdworks_sent_{name.replace(" ", "_")}_{int(time.time())}.png')
        print(f"[OK] Message sent successfully!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        try:
            page.screenshot(path=f'crowdworks_error_{name.replace(" ", "_")}.png')
        except:
            pass
        return False
    finally:
        page.close()

def main():
    print("="*60)
    print("CrowdWorks Message Sender (Using Existing Session)")
    print("="*60)
    
    with sync_playwright() as p:
        # Use existing session
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        success_count = 0
        fail_count = 0
        
        for msg in messages:
            result = send_message(browser, msg['url'], msg['message'], msg['name'])
            if result:
                success_count += 1
            else:
                fail_count += 1
            
            # Small delay between messages
            time.sleep(3)
        
        browser.close()
        
        print("\n" + "="*60)
        print(f"Summary: {success_count} sent, {fail_count} failed")
        print("="*60)
        
        return success_count == len(messages)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
