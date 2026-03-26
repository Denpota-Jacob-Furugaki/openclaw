"""
Platform Message Handler
Handles authentication, navigation, reading, and replying to messages on job platforms
Supports: CrowdWorks, Lancers, LinkedIn, and other platforms
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
        logging.FileHandler('platform_messages.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Platform credentials (load from .env)
CREDENTIALS = {
    'crowdworks': {
        'email': os.getenv('CROWDWORKS_EMAIL'),
        'password': os.getenv('CROWDWORKS_PASSWORD'),
        'login_url': 'https://crowdworks.jp/login'
    },
    'lancers': {
        'email': os.getenv('LANCERS_EMAIL'),
        'password': os.getenv('LANCERS_PASSWORD'),
        'login_url': 'https://www.lancers.jp/login'
    },
    'forkwell': {
        'email': os.getenv('FORKWELL_EMAIL'),
        'password': os.getenv('FORKWELL_PASSWORD'),
        'login_url': 'https://forkwell.com/login'
    }
}

# Session storage
SESSION_DIR = Path('platform_sessions')
SESSION_DIR.mkdir(exist_ok=True)

# Denpota's profile for reply generation
PROFILE_SUMMARY = """Denpota Furugaki (古垣 伝法太) — Freelance Software Developer / Marketing Strategist / AI Specialist
- Bilingual (Japanese/English), Korean business level
- Tech: JavaScript/TypeScript, React/Next.js, Node.js, Python, AI/ML (OpenAI, TensorFlow)
- Marketing: Google/META/LinkedIn Ads, SEO, Email (Klaviyo), data analytics
- Key achievements: Onitsuka Tiger 17 countries ROAS 120%, Meta Q1 Top Performer #1/34, InsightHub -40% task delays
- Portfolio: https://denpota-portfolio.vercel.app/
- Email: denpotafurugaki@gmail.com | Phone: 080-2466-0377
"""


class PlatformHandler:
    """Base class for platform-specific handlers."""
    
    def __init__(self, platform_name):
        self.platform = platform_name
        self.creds = CREDENTIALS.get(platform_name, {})
        self.session_file = SESSION_DIR / f"{platform_name}_session.json"
        self.browser = None
        self.context = None
        self.page = None
    
    def start_browser(self, headless=True):
        """Start browser with session persistence."""
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=headless)
        
        # Load saved session if exists
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                storage_state = json.load(f)
            self.context = self.browser.new_context(storage_state=storage_state)
        else:
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        
        self.page = self.context.new_page()
        return self.page
    
    def save_session(self):
        """Save session cookies for reuse."""
        storage_state = self.context.storage_state()
        with open(self.session_file, 'w') as f:
            json.dump(storage_state, f)
        log.info(f"Session saved to {self.session_file}")
    
    def close(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
    
    def login(self):
        """Login to platform (must be implemented by subclass)."""
        raise NotImplementedError
    
    def read_message(self, url):
        """Read message from URL (must be implemented by subclass)."""
        raise NotImplementedError
    
    def send_reply(self, message_text):
        """Send reply (must be implemented by subclass)."""
        raise NotImplementedError


class CrowdWorksHandler(PlatformHandler):
    """Handler for CrowdWorks platform."""
    
    def __init__(self):
        super().__init__('crowdworks')
    
    def login(self):
        """Login to CrowdWorks."""
        if not self.creds.get('email') or not self.creds.get('password'):
            log.error("CrowdWorks credentials not found in .env")
            return False
        
        log.info("Logging into CrowdWorks...")
        self.page.goto(self.creds['login_url'])
        self.page.wait_for_timeout(2000)
        
        # Fill login form
        self.page.fill('input[type="email"], input[name="email"]', self.creds['email'])
        self.page.fill('input[type="password"], input[name="password"]', self.creds['password'])
        
        # Click login button
        self.page.click('button:has-text("ログイン")')
        self.page.wait_for_timeout(3000)
        
        # Check if logged in
        if 'login' not in self.page.url:
            log.info("✓ Logged into CrowdWorks")
            self.save_session()
            return True
        else:
            log.error("✗ CrowdWorks login failed")
            return False
    
    def read_message(self, url):
        """Read proposal/message from CrowdWorks."""
        log.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(3000)
        
        # Check if login required
        if 'login' in self.page.url:
            log.info("Session expired, logging in...")
            if not self.login():
                return None
            self.page.goto(url, wait_until="domcontentloaded")
            self.page.wait_for_timeout(3000)
        
        # Take screenshot
        screenshot_path = f"crowdworks_message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.page.screenshot(path=screenshot_path, full_page=True)
        log.info(f"Screenshot saved: {screenshot_path}")
        
        # Extract message content
        data = {}
        
        # Job title
        title_el = self.page.query_selector('.o-workDetail_title, h1, [class*="title"]')
        data['title'] = title_el.text_content().strip() if title_el else ''
        
        # Job description
        desc_el = self.page.query_selector('.o-workDetail_description, [class*="description"]')
        data['description'] = desc_el.text_content().strip() if desc_el else ''
        
        # Client name
        client_el = self.page.query_selector('.c-client_name, [class*="client"]')
        data['client'] = client_el.text_content().strip() if client_el else ''
        
        # Budget
        budget_el = self.page.query_selector('[class*="budget"], [class*="price"]')
        data['budget'] = budget_el.text_content().strip() if budget_el else ''
        
        # Messages/conversation
        messages = []
        message_elements = self.page.query_selector_all('.c-message, [class*="message"]')
        for msg_el in message_elements:
            sender_el = msg_el.query_selector('[class*="sender"], [class*="name"]')
            text_el = msg_el.query_selector('[class*="text"], [class*="body"]')
            
            if text_el:
                messages.append({
                    'sender': sender_el.text_content().strip() if sender_el else 'Unknown',
                    'text': text_el.text_content().strip()
                })
        
        data['messages'] = messages
        data['screenshot'] = screenshot_path
        data['url'] = url
        
        # Get full page text for context
        data['full_text'] = self.page.text_content('body')[:3000]
        
        log.info(f"Extracted: {data['title'][:50]}... ({len(messages)} messages)")
        return data
    
    def send_reply(self, message_text):
        """Send reply on CrowdWorks."""
        log.info("Sending reply on CrowdWorks...")
        
        # Find message textarea
        textarea = self.page.query_selector('textarea[name="message"], textarea[class*="message"]')
        if not textarea:
            # Try different selectors
            textarea = self.page.query_selector('textarea, [contenteditable="true"]')
        
        if not textarea:
            log.error("Could not find message textarea")
            return False
        
        # Fill message
        textarea.fill(message_text)
        self.page.wait_for_timeout(1000)
        
        # Find and click send button
        send_btn = self.page.query_selector('button:has-text("送信"), button:has-text("Send"), input[value*="送信"]')
        if send_btn:
            send_btn.click()
            self.page.wait_for_timeout(2000)
            log.info("✓ Reply sent")
            
            # Take confirmation screenshot
            self.page.screenshot(path=f"crowdworks_sent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            return True
        else:
            log.error("Could not find send button")
            return False


class LancersHandler(PlatformHandler):
    """Handler for Lancers platform."""
    
    def __init__(self):
        super().__init__('lancers')
    
    def login(self):
        """Login to Lancers."""
        if not self.creds.get('email') or not self.creds.get('password'):
            log.error("Lancers credentials not found in .env")
            return False
        
        log.info("Logging into Lancers...")
        self.page.goto(self.creds['login_url'])
        self.page.wait_for_timeout(2000)
        
        self.page.fill('input[name="login_name"]', self.creds['email'])
        self.page.fill('input[name="password"]', self.creds['password'])
        self.page.click('button[type="submit"], input[type="submit"]')
        self.page.wait_for_timeout(3000)
        
        if 'login' not in self.page.url:
            log.info("✓ Logged into Lancers")
            self.save_session()
            return True
        else:
            log.error("✗ Lancers login failed")
            return False
    
    def read_message(self, url):
        """Read message from Lancers."""
        log.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(3000)
        
        if 'login' in self.page.url:
            if not self.login():
                return None
            self.page.goto(url)
            self.page.wait_for_timeout(3000)
        
        screenshot_path = f"lancers_message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.page.screenshot(path=screenshot_path, full_page=True)
        
        data = {
            'title': '',
            'description': '',
            'screenshot': screenshot_path,
            'url': url,
            'full_text': self.page.text_content('body')[:3000]
        }
        
        # Extract content (Lancers-specific selectors)
        title_el = self.page.query_selector('h1, .c-heading__title')
        data['title'] = title_el.text_content().strip() if title_el else ''
        
        desc_el = self.page.query_selector('.c-projectDetail__description, article')
        data['description'] = desc_el.text_content().strip() if desc_el else ''
        
        return data
    
    def send_reply(self, message_text):
        """Send reply on Lancers."""
        textarea = self.page.query_selector('textarea')
        if textarea:
            textarea.fill(message_text)
            self.page.wait_for_timeout(1000)
            
            send_btn = self.page.query_selector('button:has-text("送信"), input[type="submit"]')
            if send_btn:
                send_btn.click()
                self.page.wait_for_timeout(2000)
                log.info("✓ Reply sent on Lancers")
                return True
        
        log.error("Could not send reply on Lancers")
        return False


def generate_reply(platform_data, interested=True):
    """Generate AI reply based on platform message data."""
    prompt = f"""You are Denpota Furugaki replying to a job message on {platform_data.get('platform', 'job platform')}.

Your profile: {PROFILE_SUMMARY}

Message details:
Title: {platform_data.get('title', 'N/A')}
Client: {platform_data.get('client', 'N/A')}
Budget: {platform_data.get('budget', 'N/A')}
Description: {platform_data.get('description', 'N/A')[:500]}

Previous messages:
{json.dumps(platform_data.get('messages', [])[:3], ensure_ascii=False, indent=2)}

Generate a {"professional, interested" if interested else "polite decline"} reply in Japanese.

If interested:
- Thank the client
- Express interest in the project
- Highlight 1-2 relevant skills from your profile
- Ask about remote work if not mentioned
- Ask about next steps (interview/discussion)
- Keep under 200 characters

If declining:
- Brief thank you
- Polite decline
- 2-3 sentences only

Write ONLY the reply message text (no subject, no greeting format)."""

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
        return "ご連絡いただきありがとうございます。詳細を拝見し、ご連絡させていただきます。"


def handle_message_url(url, auto_reply=False, interested=True, headless=True):
    """
    Main function to handle a message URL.
    
    Args:
        url: Platform message/proposal URL
        auto_reply: If True, send reply automatically
        interested: If True, generate interested reply, else decline
        headless: Run browser in headless mode
    
    Returns:
        dict with message data and reply status
    """
    # Detect platform
    platform = None
    if 'crowdworks.jp' in url:
        platform = 'crowdworks'
        handler = CrowdWorksHandler()
    elif 'lancers.jp' in url:
        platform = 'lancers'
        handler = LancersHandler()
    else:
        log.error(f"Unsupported platform: {url}")
        return {'error': 'Unsupported platform'}
    
    try:
        # Start browser
        handler.start_browser(headless=headless)
        
        # Read message
        message_data = handler.read_message(url)
        if not message_data:
            return {'error': 'Failed to read message'}
        
        message_data['platform'] = platform
        
        # Generate reply
        reply_text = generate_reply(message_data, interested=interested)
        message_data['generated_reply'] = reply_text
        
        log.info(f"\n=== Generated Reply ===\n{reply_text}\n")
        
        # Send reply if auto_reply enabled
        if auto_reply:
            success = handler.send_reply(reply_text)
            message_data['reply_sent'] = success
        else:
            message_data['reply_sent'] = False
            log.info("Auto-reply disabled. Review the reply above and send manually.")
        
        # Save result
        result_file = f"message_handled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(message_data, f, indent=2, ensure_ascii=False)
        
        log.info(f"Result saved to {result_file}")
        
        return message_data
        
    finally:
        handler.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python platform_message_handler.py <url> [--auto-reply] [--decline] [--visible]")
        print("\nExample:")
        print("  python platform_message_handler.py https://crowdworks.jp/proposals/288200154")
        print("  python platform_message_handler.py <url> --auto-reply  # Send reply automatically")
        print("  python platform_message_handler.py <url> --decline     # Generate decline message")
        print("  python platform_message_handler.py <url> --visible     # Show browser (not headless)")
        sys.exit(1)
    
    url = sys.argv[1]
    auto_reply = '--auto-reply' in sys.argv
    interested = '--decline' not in sys.argv
    headless = '--visible' not in sys.argv
    
    result = handle_message_url(url, auto_reply=auto_reply, interested=interested, headless=headless)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n✓ Message processed")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Client: {result.get('client', 'N/A')}")
        print(f"\nGenerated reply:\n{result.get('generated_reply', 'N/A')}")
        print(f"\nReply sent: {result.get('reply_sent', False)}")
        print(f"Screenshot: {result.get('screenshot', 'N/A')}")
