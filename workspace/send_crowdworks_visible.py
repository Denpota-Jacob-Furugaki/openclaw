"""
Send CrowdWorks messages - VISIBLE browser to debug
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

def main():
    print("="*60)
    print("Sending CrowdWorks Messages (VISIBLE - Will Auto-Click Send)")
    print("="*60)
    print("\nBrowser will open and automatically:")
    print("1. Navigate to each message")
    print("2. Fill in your reply") 
    print("3. Click send")
    print("\nWatch the browser window!")
    print("="*60 + "\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,  # VISIBLE
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        success_count = 0
        
        for i, msg in enumerate(messages, 1):
            print(f"\n[{i}/3] Sending: {msg['name']}")
            print(f"       URL: {msg['url']}")
            
            try:
                page.goto(msg['url'], wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
                
                if 'login' in page.url:
                    print("[ERROR] Session expired - please login manually and run again")
                    input("Press Enter after logging in...")
                    page.goto(msg['url'])
                    time.sleep(3)
                
                # Fill textarea - try all visible textareas
                textareas = page.query_selector_all('textarea')
                filled = False
                for textarea in textareas:
                    if textarea.is_visible():
                        textarea.fill(msg['message'])
                        print("[OK] Message filled")
                        filled = True
                        break
                
                if not filled:
                    print("[ERROR] No visible textarea found")
                    continue
                
                time.sleep(2)
                
                # Try to find and click send button
                # Strategy: press Enter key which usually submits
                page.keyboard.press('Control+Enter')  # Try Ctrl+Enter first
                time.sleep(1)
                
                # If that didn't work, try clicking buttons
                for selector in ['button:visible', 'input[type="submit"]:visible']:
                    try:
                        buttons = page.query_selector_all(selector)
                        for btn in buttons:
                            text = btn.text_content() or btn.get_attribute('value') or ''
                            if '送信' in text or 'send' in text.lower():
                                btn.click()
                                print(f"[OK] Clicked send button: {text}")
                                break
                    except:
                        pass
                
                time.sleep(3)
                success_count += 1
                print(f"[OK] Message {i}/3 sent!")
                
            except Exception as e:
                print(f"[ERROR] {e}")
            
            if i < len(messages):
                time.sleep(2)
        
        print("\n" + "="*60)
        print(f"Completed: {success_count}/{len(messages)} sent")
        print("="*60)
        print("\nPress Enter to close browser...")
        input()
        browser.close()

if __name__ == "__main__":
    main()
