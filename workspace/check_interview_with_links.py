"""
Enhanced Interview Request Checker - Follows Links
Checks Gmail for interview requests and follows links to extract full details
from platforms like CrowdWorks, Lancers, etc.
"""
import os
import json
import base64
import re
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from playwright.sync_api import sync_playwright

TOKEN_PATH = 'google_token.json'

# Interview/meeting keywords
INTERVIEW_KEYWORDS = [
    'interview', '面接', '面談', 'カジュアル面談',
    'meet', 'meeting', 'schedule', 'zoom', 'google meet',
    'teams', 'skype', 'call', 'オンライン面談',
    'ご都合', 'available', 'availability', '日程',
    '面接日程', '面談希望', '応募', '提案', 'proposal',
    'message', 'メッセージ', '返信', 'reply', 'respond'
]

# Job platforms to follow links
JOB_PLATFORMS = [
    'crowdworks.jp',
    'lancers.jp',
    'coconala.com',
    'workship.jp',
    'forkwell.com',
    'findy-code.io',
    'linkedin.com',
    'wantedly.com',
    'green-japan.com',
    'bizreach.jp'
]


def get_gmail_service():
    """Get authenticated Gmail service."""
    if not os.path.exists(TOKEN_PATH):
        print(f"Error: {TOKEN_PATH} not found. Run gmail_job_reply_bot.py first to authenticate.")
        return None
    
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    return build('gmail', 'v1', credentials=creds)


def decode_body(payload):
    """Decode email body."""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    return body


def extract_links(text):
    """Extract URLs from email text."""
    # Match http/https URLs
    url_pattern = r'https?://[^\s<>"\'\)]+(?:[^\s<>"\'\.\,\)]|\.[^\s<>"\'\)])*'
    urls = re.findall(url_pattern, text)
    
    # Filter for job platform URLs
    platform_urls = []
    for url in urls:
        if any(platform in url for platform in JOB_PLATFORMS):
            # Clean up URL (remove trailing punctuation, HTML entities)
            url = re.sub(r'[\.,:;]+$', '', url)
            url = url.replace('&amp;', '&')
            platform_urls.append(url)
    
    return list(set(platform_urls))  # Remove duplicates


def scrape_page_content(url, timeout=10000):
    """Scrape content from a job platform page."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            # Visit the page
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            page.wait_for_timeout(2000)
            
            # Take screenshot for reference
            screenshot_name = f"interview_link_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=screenshot_name)
            
            # Extract main content based on platform
            content = {}
            
            if 'crowdworks.jp' in url:
                # CrowdWorks specific selectors
                title_el = page.query_selector('.o-workDetail_title, [class*="title"]')
                body_el = page.query_selector('.o-workDetail_description, [class*="description"]')
                client_el = page.query_selector('.c-client_name, [class*="client"]')
                
                content['title'] = title_el.text_content().strip() if title_el else ''
                content['body'] = body_el.text_content().strip() if body_el else ''
                content['client'] = client_el.text_content().strip() if client_el else ''
                
            elif 'lancers.jp' in url:
                # Lancers specific selectors
                title_el = page.query_selector('.c-heading__title, h1')
                body_el = page.query_selector('.c-projectDetail__description')
                
                content['title'] = title_el.text_content().strip() if title_el else ''
                content['body'] = body_el.text_content().strip() if body_el else ''
                
            else:
                # Generic extraction
                title_el = page.query_selector('h1, [class*="title"]')
                body_el = page.query_selector('main, article, [class*="content"], [class*="description"]')
                
                content['title'] = title_el.text_content().strip() if title_el else ''
                content['body'] = body_el.text_content().strip()[:1000] if body_el else ''
            
            content['screenshot'] = screenshot_name
            content['full_text'] = page.text_content('body')[:2000]
            
            browser.close()
            return content
            
    except Exception as e:
        return {
            'error': str(e),
            'title': '',
            'body': f'Failed to scrape: {str(e)}'
        }


def check_interviews_with_links():
    """Check for interview/meeting requests and follow links."""
    service = get_gmail_service()
    if not service:
        return None
    
    results = []
    
    try:
        # Search unread emails from last 7 days
        after_date = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
        query = f'is:unread after:{after_date}'
        
        messages = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute().get('messages', [])
        
        if not messages:
            return {"status": "ok", "count": 0, "interviews": []}
        
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            body = decode_body(msg_data['payload'])
            
            # Check for interview keywords
            text = f"{subject} {body}".lower()
            matched_keywords = [kw for kw in INTERVIEW_KEYWORDS if kw.lower() in text]
            
            if matched_keywords:
                # Extract links from email
                links = extract_links(body)
                
                # Scrape content from links
                scraped_content = []
                for link in links[:3]:  # Limit to first 3 links
                    print(f"Scraping {link}...")
                    content = scrape_page_content(link)
                    scraped_content.append({
                        'url': link,
                        'content': content
                    })
                
                results.append({
                    'id': msg['id'],
                    'from': sender,
                    'subject': subject,
                    'date': date,
                    'matched_keywords': matched_keywords,
                    'snippet': body[:300] + '...' if len(body) > 300 else body,
                    'links': links,
                    'scraped': scraped_content
                })
        
        return {
            "status": "ok",
            "count": len(results),
            "interviews": results,
            "checked_at": datetime.now().isoformat()
        }
        
    except HttpError as e:
        return {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }


def format_alert(data):
    """Format alert message with link content."""
    if data["status"] != "ok":
        return f"⚠️ Error checking Gmail: {data.get('error', 'Unknown error')}"
    
    if data["count"] == 0:
        return None  # No alert needed
    
    alert = f"🎯 **{data['count']} Interview/Meeting Request(s) Found!**\n\n"
    
    for i, interview in enumerate(data["interviews"], 1):
        alert += f"**{i}. {interview['subject']}**\n"
        alert += f"   From: {interview['from']}\n"
        alert += f"   Date: {interview['date']}\n"
        alert += f"   Keywords: {', '.join(interview['matched_keywords'][:3])}\n\n"
        
        # Show email preview
        alert += f"   📧 Email: {interview['snippet'][:150]}...\n\n"
        
        # Show links found
        if interview['links']:
            alert += f"   🔗 Links found: {len(interview['links'])}\n"
            for link in interview['links'][:2]:
                alert += f"      • {link}\n"
            alert += "\n"
        
        # Show scraped content
        if interview['scraped']:
            for scraped in interview['scraped']:
                content = scraped['content']
                if content.get('title'):
                    alert += f"   📄 **{content['title']}**\n"
                if content.get('client'):
                    alert += f"      Client: {content['client']}\n"
                if content.get('body'):
                    alert += f"      {content['body'][:200]}...\n"
                if content.get('screenshot'):
                    alert += f"      Screenshot: {content['screenshot']}\n"
                if content.get('error'):
                    alert += f"      ⚠️ {content['error']}\n"
                alert += "\n"
        
        alert += "---\n\n"
    
    alert += f"\n📧 Check Gmail: https://mail.google.com/mail/u/0/#inbox"
    
    return alert


if __name__ == "__main__":
    print("🔍 Checking for interview requests and following links...\n")
    
    result = check_interviews_with_links()
    
    if result:
        alert = format_alert(result)
        if alert:
            print(alert)
            
            # If interview requests found, offer to handle them
            if result.get('count', 0) > 0:
                print("\n💡 To read and reply to these messages on the platform:")
                for interview in result.get('interviews', []):
                    for link in interview.get('links', [])[:1]:  # First link only
                        print(f"\n   python platform_message_handler.py {link}")
                        print(f"   python platform_message_handler.py {link} --auto-reply  # Send automatically")
        else:
            print("✅ No interview requests found.")
        
        # Save result for tracking
        with open('last_interview_check.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print("❌ Failed to check Gmail. Make sure google_token.json exists.")
