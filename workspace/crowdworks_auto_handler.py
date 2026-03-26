"""
CrowdWorks Automatic Message Handler
- Checks CrowdWorks for new proposals/messages
- Reads message content
- Evaluates if interested (remote + software/AI/DX)
- Generates AI reply
- Sends reply automatically (or drafts for review)
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from openai import OpenAI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('crowdworks_auto_handler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Config
CROWDWORKS_EMAIL = os.getenv('CROWDWORKS_EMAIL')
CROWDWORKS_PASSWORD = os.getenv('CROWDWORKS_PASSWORD')
AUTO_SEND = os.getenv('CROWDWORKS_AUTO_SEND', 'false').lower() == 'true'
PROCESSED_FILE = 'crowdworks_processed.json'
SESSION_FILE = 'platform_sessions/crowdworks_session.json'

# Denpota's profile
PROFILE_SUMMARY = """Denpota Furugaki (古垣 伝法太) — Freelance Software Developer / Marketing Strategist / AI Specialist
- Bilingual (Japanese/English), Korean business level
- Tech: JavaScript/TypeScript, React/Next.js, Node.js, Python, AI/ML (OpenAI, TensorFlow)
- Marketing: Google/META/LinkedIn Ads, SEO, Email (Klaviyo), data analytics
- Key achievements: Onitsuka Tiger 17 countries ROAS 120%, Meta Q1 Top Performer #1/34, InsightHub -40% task delays
- Portfolio: https://denpota-portfolio.vercel.app/
- Email: denpotafurugaki@gmail.com | Phone: 080-2466-0377
"""

INTEREST_KEYWORDS = [
    "software", "engineer", "developer", "プログラマ", "エンジニア", "開発",
    "ai", "artificial intelligence", "machine learning", "ml", "人工知能",
    "python", "javascript", "typescript", "react", "node", "next.js",
    "full-stack", "fullstack", "フルスタック", "バックエンド", "フロントエンド",
    "backend", "frontend", "web developer", "web開発",
    "dx", "デジタルトランスフォーメーション", "digital transformation",
    "remote", "リモート", "フルリモート", "在宅", "テレワーク",
]

REJECT_KEYWORDS = [
    "営業", "sales", "コールセンター", "call center",
    "事務", "一般事務", "経理", "accounting",
    "接客", "ホール", "キッチン", "調理",
]


def load_processed():
    """Load processed proposal IDs."""
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    return set()


def save_processed(processed):
    """Save processed proposal IDs."""
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(processed), f)


def ai_evaluate_proposal(title, description, client, budget):
    """Evaluate if proposal matches interests."""
    prompt = f"""You are evaluating a CrowdWorks project proposal for Denpota Furugaki.

Denpota's interests:
- Software Engineering, AI Development, Full-stack Development, DX/Digital Transformation
- Marketing Engineering (combining dev + marketing)
- MUST be remote or mostly remote (fully remote preferred)
- NOT interested in: pure sales, admin, accounting, manual labor, customer service, non-tech roles

Evaluate this proposal:
Title: {title}
Client: {client}
Budget: {budget}
Description:
{description[:2000]}

Respond with EXACTLY this JSON format:
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
        return json.loads(text)
    except Exception as e:
        log.error(f"AI evaluation failed: {e}")
        return {"interested": False, "reason": "AI evaluation error", "is_remote": False, "confidence": 0}


def generate_reply(title, description, client, budget, interested):
    """Generate AI reply."""
    if interested:
        prompt = f"""Write a professional reply in Japanese to this CrowdWorks proposal.
Denpota is INTERESTED. The reply should:
- Thank the client
- Express strong interest in the project
- Briefly highlight 1-2 relevant skills from Denpota's profile
- Ask about remote work if not clearly mentioned
- Ask about next steps (interview/discussion)
- Be concise (under 200 characters)

Denpota's profile: {PROFILE_SUMMARY}

Proposal:
Title: {title}
Client: {client}
Budget: {budget}
Description: {description[:1000]}

Write ONLY the reply body text. Start with acknowledging the client/project."""
    else:
        prompt = f"""Write a polite decline reply in Japanese to this CrowdWorks proposal.
Denpota is NOT interested. The reply should:
- Thank them for considering
- Politely decline (currently not looking for this type of project)
- Keep it short (2-3 sentences)

Proposal title: {title}

Write ONLY the reply body text."""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"AI reply generation failed: {e}")
        if interested:
            return f"ご連絡いただきありがとうございます。\n{title}のプロジェクトに大変興味がございます。\nぜひ詳細についてお話しさせていただけますと幸いです。\n\nポートフォリオ：https://denpota-portfolio.vercel.app/\n\n古垣 伝法太"
        else:
            return "ご連絡いただきありがとうございます。\n大変恐縮ですが、現在このタイプのプロジェクトは検討しておりません。\nまた機会がございましたらよろしくお願いいたします。"


def run_crowdworks_handler(headless=True):
    """Main handler: check proposals, evaluate, reply."""
    if not CROWDWORKS_EMAIL or not CROWDWORKS_PASSWORD:
        log.error("CrowdWorks credentials not found in .env")
        return
    
    processed = load_processed()
    log.info(f"Starting CrowdWorks auto-handler. {len(processed)} proposals already processed.")
    log.info(f"Auto-send mode: {AUTO_SEND}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        
        # Load session if exists
        Path('platform_sessions').mkdir(exist_ok=True)
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                storage_state = json.load(f)
            context = browser.new_context(storage_state=storage_state)
        else:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        
        page = context.new_page()
        
        # Login
        log.info("Checking CrowdWorks login status...")
        page.goto('https://crowdworks.jp/dashboard', wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        
        if 'login' in page.url:
            log.info("Logging in...")
            page.goto('https://crowdworks.jp/login')
            page.wait_for_timeout(2000)
            
            page.fill('input[type="email"], input[name="email"]', CROWDWORKS_EMAIL)
            page.fill('input[type="password"], input[name="password"]', CROWDWORKS_PASSWORD)
            page.click('button:has-text("ログイン")')
            page.wait_for_timeout(3000)
            
            if 'login' not in page.url:
                log.info("✓ Logged in")
                # Save session
                storage_state = context.storage_state()
                with open(SESSION_FILE, 'w') as f:
                    json.dump(storage_state, f)
            else:
                log.error("✗ Login failed")
                browser.close()
                return
        else:
            log.info("✓ Already logged in")
        
        # Check for new messages/proposals
        log.info("Checking for new proposals and messages...")
        
        # Go to proposals/messages page
        page.goto('https://crowdworks.jp/dashboard/proposals', wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        
        # Take screenshot
        page.screenshot(path=f"crowdworks_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        stats = {"processed": 0, "interested": 0, "declined": 0, "skipped": 0, "errors": 0}
        
        # Find all proposals/messages needing response
        # Look for unread messages or proposals awaiting response
        proposal_items = page.query_selector_all('[class*="proposal"], [class*="message"], .c-card')
        
        log.info(f"Found {len(proposal_items)} proposal/message items")
        
        for i, item in enumerate(proposal_items[:10]):  # Limit to first 10
            try:
                # Extract proposal ID or link
                link_el = item.query_selector('a[href*="/proposals/"], a[href*="/messages/"]')
                if not link_el:
                    continue
                
                proposal_url = link_el.get_attribute('href')
                if not proposal_url.startswith('http'):
                    proposal_url = f"https://crowdworks.jp{proposal_url}"
                
                proposal_id = proposal_url.split('/')[-1].split('#')[0].split('?')[0]
                
                if proposal_id in processed:
                    log.info(f"[{i}] Proposal {proposal_id} already processed")
                    stats["skipped"] += 1
                    continue
                
                # Check if needs response (look for indicators)
                status_el = item.query_selector('[class*="status"], [class*="badge"]')
                status = status_el.text_content().strip() if status_el else ''
                
                # Skip if already responded
                if '返信済' in status or '応募済' in status or 'responded' in status.lower():
                    log.info(f"[{i}] Proposal {proposal_id} already responded")
                    processed.add(proposal_id)
                    stats["skipped"] += 1
                    continue
                
                log.info(f"\n[{i}] Processing proposal {proposal_id}")
                log.info(f"URL: {proposal_url}")
                
                # Navigate to proposal
                page.goto(proposal_url, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                
                # Take screenshot
                screenshot_path = f"crowdworks_proposal_{proposal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                
                # Extract proposal details
                title_el = page.query_selector('.o-workDetail_title, h1, [class*="title"]')
                title = title_el.text_content().strip() if title_el else 'No title'
                
                desc_el = page.query_selector('.o-workDetail_description, [class*="description"]')
                description = desc_el.text_content().strip() if desc_el else ''
                
                client_el = page.query_selector('.c-client_name, [class*="client"]')
                client = client_el.text_content().strip() if client_el else 'Unknown'
                
                budget_el = page.query_selector('[class*="budget"], [class*="price"]')
                budget = budget_el.text_content().strip() if budget_el else 'Not specified'
                
                log.info(f"Title: {title}")
                log.info(f"Client: {client}")
                log.info(f"Budget: {budget}")
                
                # AI evaluation
                evaluation = ai_evaluate_proposal(title, description, client, budget)
                interested = evaluation.get("interested", False)
                is_remote = evaluation.get("is_remote", False)
                reason = evaluation.get("reason", "")
                confidence = evaluation.get("confidence", 0)
                
                # If interested but not remote, decline
                if interested and is_remote == False:
                    interested = False
                    reason = "Interested in project but not remote"
                
                log.info(f"AI: interested={interested}, remote={is_remote}, confidence={confidence}%, reason={reason}")
                
                # Generate reply
                reply_text = generate_reply(title, description, client, budget, interested)
                log.info(f"\n=== Generated Reply ===\n{reply_text}\n====================\n")
                
                # Send reply
                if AUTO_SEND:
                    # Find textarea
                    textarea = page.query_selector('textarea[name="message"], textarea[class*="message"], textarea')
                    if textarea:
                        textarea.fill(reply_text)
                        page.wait_for_timeout(1000)
                        
                        # Find send button
                        send_btn = page.query_selector('button:has-text("送信"), button:has-text("Send"), input[value*="送信"]')
                        if send_btn:
                            send_btn.click()
                            page.wait_for_timeout(2000)
                            log.info("✓ Reply sent automatically")
                            
                            # Take confirmation screenshot
                            page.screenshot(path=f"crowdworks_sent_{proposal_id}.png")
                            
                            if interested:
                                stats["interested"] += 1
                            else:
                                stats["declined"] += 1
                        else:
                            log.warning("Could not find send button")
                            stats["errors"] += 1
                    else:
                        log.warning("Could not find message textarea")
                        stats["errors"] += 1
                else:
                    log.info("Auto-send disabled. Reply generated but not sent.")
                    # Save reply for manual review
                    with open(f"crowdworks_reply_{proposal_id}.txt", 'w', encoding='utf-8') as f:
                        f.write(f"Proposal: {title}\n")
                        f.write(f"Client: {client}\n")
                        f.write(f"URL: {proposal_url}\n")
                        f.write(f"Interested: {interested}\n")
                        f.write(f"\n{reply_text}\n")
                    
                    if interested:
                        stats["interested"] += 1
                    else:
                        stats["declined"] += 1
                
                # Mark as processed
                processed.add(proposal_id)
                stats["processed"] += 1
                save_processed(processed)
                
                # Go back to proposals list
                page.goto('https://crowdworks.jp/dashboard/proposals', wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                
            except Exception as e:
                log.error(f"Error processing proposal {i}: {e}")
                stats["errors"] += 1
        
        browser.close()
    
    log.info(f"\n=== Summary ===")
    log.info(f"Processed: {stats['processed']}")
    log.info(f"Interested: {stats['interested']}")
    log.info(f"Declined: {stats['declined']}")
    log.info(f"Skipped (already done): {stats['skipped']}")
    log.info(f"Errors: {stats['errors']}")
    log.info(f"Mode: {'AUTO-SEND' if AUTO_SEND else 'DRAFT'}")
    
    return stats


if __name__ == "__main__":
    import sys
    
    headless = '--visible' not in sys.argv
    
    run_crowdworks_handler(headless=headless)
