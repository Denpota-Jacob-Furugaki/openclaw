"""
Send CrowdWorks messages automatically - Fixed version
Uses session cookies if available, handles current login page structure
"""
import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

CROWDWORKS_EMAIL = os.getenv('CROWDWORKS_EMAIL')
CROWDWORKS_PASSWORD = os.getenv('CROWDWORKS_PASSWORD')

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

def send_message(browser, url, message_text, name):
    """Send a message on CrowdWorks."""
    print(f"\n[INFO] Sending: {name}")
    print(f"[INFO] URL: {url}")
    
    page = browser.new_page()
    
    try:
        # Navigate to message URL
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        
        # Check if we need to login
        if 'login' in page.url:
            print("[INFO] Not logged in, attempting login...")
            
            # Try multiple selectors for email input
            email_filled = False
            for selector in [
                'input[type="email"]',
                'input[name="email"]',
                'input[id="email"]',
                '#user_name',
                'input[placeholder*="メール"]',
                'input[placeholder*="mail"]'
            ]:
                try:
                    page.fill(selector, CROWDWORKS_EMAIL, timeout=2000)
                    email_filled = True
                    print(f"[OK] Filled email with selector: {selector}")
                    break
                except:
                    continue
            
            if not email_filled:
                print("[ERROR] Could not find email input field")
                page.screenshot(path=f'crowdworks_login_fail_{int(time.time())}.png')
                return False
            
            # Try multiple selectors for password
            password_filled = False
            for selector in [
                'input[type="password"]',
                'input[name="password"]',
                'input[id="password"]',
                '#password'
            ]:
                try:
                    page.fill(selector, CROWDWORKS_PASSWORD, timeout=2000)
                    password_filled = True
                    print(f"[OK] Filled password with selector: {selector}")
                    break
                except:
                    continue
            
            if not password_filled:
                print("[ERROR] Could not find password input field")
                return False
            
            time.sleep(1)
            
            # Click login button
            login_clicked = False
            for selector in [
                'button:has-text("ログイン")',
                'input[type="submit"]',
                'button[type="submit"]',
                'input[value*="ログイン"]',
                'button:has-text("login")'
            ]:
                try:
                    page.click(selector, timeout=2000)
                    login_clicked = True
                    print(f"[OK] Clicked login with selector: {selector}")
                    break
                except:
                    continue
            
            if not login_clicked:
                print("[ERROR] Could not find login button")
                return False
            
            # Wait for redirect
            time.sleep(5)
            
            # Check if login successful
            if 'login' in page.url:
                print("[ERROR] Login failed - still on login page")
                page.screenshot(path=f'crowdworks_login_failed_{int(time.time())}.png')
                return False
            else:
                print("[OK] Login successful!")
                # Navigate back to message URL
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
        
        # Now on message page, find textarea and send
        print("[INFO] Looking for message textarea...")
        
        textarea_found = False
        for selector in [
            'textarea',
            'textarea[name="message"]',
            'textarea[id="message"]',
            '[contenteditable="true"]',
            'textarea[placeholder*="メッセージ"]'
        ]:
            try:
                page.fill(selector, message_text, timeout=2000)
                textarea_found = True
                print(f"[OK] Filled message with selector: {selector}")
                break
            except:
                continue
        
        if not textarea_found:
            print("[ERROR] Could not find message textarea")
            page.screenshot(path=f'crowdworks_no_textarea_{int(time.time())}.png')
            return False
        
        time.sleep(1)
        
        # Find and click send button
        print("[INFO] Looking for send button...")
        
        send_clicked = False
        for selector in [
            'button:has-text("送信")',
            'input[type="submit"]',
            'button[type="submit"]',
            'input[value*="送信"]',
            'button:has-text("Send")'
        ]:
            try:
                page.click(selector, timeout=2000)
                send_clicked = True
                print(f"[OK] Clicked send with selector: {selector}")
                break
            except:
                continue
        
        if not send_clicked:
            print("[ERROR] Could not find send button")
            page.screenshot(path=f'crowdworks_no_send_btn_{int(time.time())}.png')
            return False
        
        time.sleep(2)
        
        # Take confirmation screenshot
        page.screenshot(path=f'crowdworks_sent_{name.replace(" ", "_")}_{int(time.time())}.png')
        print(f"[OK] Message sent successfully!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        page.screenshot(path=f'crowdworks_error_{int(time.time())}.png')
        return False
    finally:
        page.close()

def main():
    print("="*60)
    print("CrowdWorks Automatic Message Sender")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        success_count = 0
        fail_count = 0
        
        for msg in messages:
            result = send_message(browser, msg['url'], msg['message'], msg['name'])
            if result:
                success_count += 1
            else:
                fail_count += 1
            
            # Small delay between messages
            time.sleep(2)
        
        browser.close()
        
        print("\n" + "="*60)
        print(f"Summary: {success_count} sent, {fail_count} failed")
        print("="*60)
        
        return success_count == len(messages)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
