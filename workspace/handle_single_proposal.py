"""
Handle a single CrowdWorks proposal - read, evaluate, respond
"""
import os
import time
import re
from playwright.sync_api import sync_playwright
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SESSION_DIR = Path("C:/Users/denpo/CascadeProjects/my-first-ai-agent/crowdworks_session")

PROFILE = """Denpota Furugaki (古垣 伝法太) — Freelance Software Developer / Marketing Strategist / AI Specialist
- Bilingual (Japanese/English), Korean business level
- Tech: JavaScript/TypeScript, React/Next.js, Node.js, Python, AI/ML (OpenAI, TensorFlow)
- Marketing: Google/META/LinkedIn Ads, SEO, Email (Klaviyo), data analytics
- Key achievements: Onitsuka Tiger 17 countries ROAS 120%, Meta Q1 Top Performer #1/34
- Portfolio: https://denpota-portfolio.vercel.app/
- Email: denpotafurugaki@gmail.com | Phone: 080-2466-0377
"""

def evaluate_proposal(title, description, budget, client):
    """Evaluate if proposal matches criteria."""
    prompt = f"""Evaluate this CrowdWorks proposal for Denpota Furugaki.

Criteria:
- Software Engineering, AI Development, Full-stack Development, DX
- Marketing Engineering (dev + marketing)
- MUST be remote or mostly remote
- NOT interested in: pure sales, admin, manual labor, customer service, non-tech

Proposal:
Title: {title}
Client: {client}
Budget: {budget}
Description:
{description[:2000]}

Respond with JSON:
{{"interested": true/false, "reason": "brief reason", "is_remote": true/false/unknown, "confidence": 0-100}}
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )
        text = resp.choices[0].message.content.strip()
        if '{' in text:
            text = text[text.index('{'):text.rindex('}') + 1]
        import json
        return json.loads(text)
    except Exception as e:
        print(f"[ERROR] AI evaluation failed: {e}")
        return {"interested": False, "reason": "evaluation error", "is_remote": False, "confidence": 0}

def generate_reply(title, description, budget, client, interested):
    """Generate appropriate reply."""
    if interested:
        prompt = f"""Write a professional reply in Japanese to this CrowdWorks proposal.
Denpota is INTERESTED. Reply should:
- Thank the client
- Express strong interest
- Briefly highlight 1-2 relevant skills
- Ask about remote work if not clear
- Ask about next steps
- Be concise (under 200 chars)

Profile: {PROFILE}

Proposal:
Title: {title}
Client: {client}
Budget: {budget}
Description: {description[:1000]}

Write ONLY the reply text."""
    else:
        prompt = f"""Write a polite decline in Japanese to this CrowdWorks proposal.
Denpota is NOT interested. Reply should:
- Thank them
- Politely decline (not looking for this type)
- Keep short (2-3 sentences)

Title: {title}

Write ONLY the reply text."""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Reply generation failed: {e}")
        if interested:
            return f"ご連絡いただきありがとうございます。\n{title}のプロジェクトに大変興味がございます。\nぜひ詳細についてお話しさせていただけますと幸いです。\n\nポートフォリオ：https://denpota-portfolio.vercel.app/\n\n古垣 伝法太"
        else:
            return "ご連絡いただきありがとうございます。\n大変恐縮ですが、現在このタイプのプロジェクトは検討しておりません。\nまた機会がございましたらよろしくお願いいたします。"

def handle_proposal(url):
    """Read proposal, evaluate, generate reply, send."""
    print("="*60)
    print("CrowdWorks Proposal Handler")
    print("="*60)
    print(f"URL: {url}\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        try:
            # Navigate to proposal
            print("[INFO] Loading proposal page...")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(4)
            
            if 'login' in page.url:
                print("[ERROR] Session expired - please login manually")
                input("Press Enter after logging in...")
                page.goto(url)
                time.sleep(3)
            
            # Extract proposal details
            print("[INFO] Extracting proposal details...")
            
            title = ""
            title_selectors = ['.o-workDetail_title', 'h1', '[class*="title"]']
            for selector in title_selectors:
                el = page.query_selector(selector)
                if el:
                    title = el.text_content().strip()
                    break
            
            description = ""
            desc_selectors = ['.o-workDetail_description', '[class*="description"]', 'article']
            for selector in desc_selectors:
                el = page.query_selector(selector)
                if el:
                    description = el.text_content().strip()
                    break
            
            client_name = ""
            client_selectors = ['.c-client_name', '[class*="client"]']
            for selector in client_selectors:
                el = page.query_selector(selector)
                if el:
                    client_name = el.text_content().strip()
                    break
            
            budget = ""
            budget_selectors = ['[class*="budget"]', '[class*="price"]']
            for selector in budget_selectors:
                el = page.query_selector(selector)
                if el:
                    budget = el.text_content().strip()
                    break
            
            print(f"\n{'='*60}")
            print(f"Title: {title}")
            print(f"Client: {client_name}")
            print(f"Budget: {budget}")
            print(f"Description: {description[:200]}...")
            print(f"{'='*60}\n")
            
            # Evaluate
            print("[INFO] Evaluating proposal...")
            evaluation = evaluate_proposal(title, description, budget, client_name)
            
            interested = evaluation.get("interested", False)
            is_remote = evaluation.get("is_remote", False)
            reason = evaluation.get("reason", "")
            confidence = evaluation.get("confidence", 0)
            
            # If interested but not remote, decline
            if interested and is_remote == False:
                interested = False
                reason = "Interested but not remote"
            
            print(f"\n[EVALUATION]")
            print(f"  Interested: {interested}")
            print(f"  Remote: {is_remote}")
            print(f"  Confidence: {confidence}%")
            print(f"  Reason: {reason}\n")
            
            # Generate reply
            print("[INFO] Generating reply...")
            reply_text = generate_reply(title, description, budget, client_name, interested)
            
            print(f"\n{'='*60}")
            print("GENERATED REPLY:")
            print(f"{'='*60}")
            print(reply_text)
            print(f"{'='*60}\n")
            
            # Ask for confirmation
            confirm = input("Send this reply? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("[INFO] Reply not sent (user cancelled)")
                browser.close()
                return False
            
            # Find and fill textarea
            print("\n[INFO] Sending reply...")
            textareas = page.query_selector_all('textarea')
            filled = False
            for textarea in textareas:
                if textarea.is_visible():
                    textarea.fill(reply_text)
                    print("[OK] Message filled")
                    filled = True
                    break
            
            if not filled:
                print("[ERROR] Could not find textarea")
                browser.close()
                return False
            
            time.sleep(2)
            
            # Try to send
            page.keyboard.press('Control+Enter')
            time.sleep(1)
            
            # Try clicking send button
            for selector in ['button:visible']:
                buttons = page.query_selector_all(selector)
                for btn in buttons:
                    text = btn.text_content() or ''
                    if '送信' in text or '提案' in text:
                        btn.click()
                        print(f"[OK] Clicked send button: {text}")
                        break
            
            time.sleep(3)
            
            # Take screenshot
            page.screenshot(path=f'crowdworks_sent_{int(time.time())}.png')
            print("[OK] Reply sent successfully!")
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] {e}")
            try:
                page.screenshot(path=f'crowdworks_error_{int(time.time())}.png')
            except:
                pass
            browser.close()
            return False

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else input("Enter proposal URL: ")
    handle_proposal(url)
