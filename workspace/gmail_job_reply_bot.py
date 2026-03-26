"""
Gmail Job Search Auto-Reply Bot
- Reads unread emails from job platforms (LinkedIn, Indeed, Wantedly, etc.)
- Uses AI to evaluate fit (remote + software/AI/DX roles)
- Auto-drafts replies in Denpota's style
- Saves drafts for review or sends automatically (configurable)
"""
import os
import json
import logging
import base64
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('gmail_job_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Config
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_PATH = 'google_token.json'
CREDENTIALS_PATH = 'google_credentials.json'
PROCESSED_FILE = 'gmail_processed.json'
AUTO_SEND = False  # Set to True to auto-send replies, False to save as drafts

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Denpota's profile
PROFILE_SUMMARY = """Denpota Furugaki (古垣 伝法太) — Freelance Software Developer / Marketing Strategist / AI Specialist
- Bilingual (Japanese/English), Korean business level
- Tech: JavaScript/TypeScript, React/Next.js, Node.js, Python, AI/ML (OpenAI, TensorFlow)
- Marketing: Google/META/LinkedIn Ads, SEO, Email (Klaviyo), data analytics
- Key achievements: Onitsuka Tiger 17 countries ROAS 120%, Meta Q1 Top Performer #1/34, InsightHub -40% task delays
- Portfolio: https://denpota-portfolio.vercel.app/
- Email: denpotafurugaki@gmail.com | Phone: 080-2466-0377
"""

# Job platform domains to monitor
JOB_PLATFORMS = [
    'linkedin.com',
    'indeed.com',
    'wantedly.com',
    'green-japan.com',
    'bizreach.jp',
    'en-japan.com',
    'doda.jp',
    'rikunabi.com',
    'mynavi.jp',
    'findy-code.io',
    'forkwell.com',
    'levtech.jp',
    'geekly.co.jp',
    'paiza.jp',
    'crowdworks.jp',
    'lancers.jp',
]

INTEREST_KEYWORDS = [
    "software", "engineer", "developer", "プログラマ", "エンジニア", "開発",
    "ai", "artificial intelligence", "machine learning", "ml", "人工知能",
    "python", "javascript", "typescript", "react", "node", "next.js",
    "full-stack", "fullstack", "フルスタック", "バックエンド", "フロントエンド",
    "backend", "frontend", "web developer", "web開発",
    "dx", "デジタルトランスフォーメーション", "digital transformation",
    "data", "データ", "analytics", "分析",
    "saas", "cloud", "クラウド", "devops",
    "remote", "リモート", "フルリモート", "在宅", "テレワーク",
    "marketing engineer", "マーケティングエンジニア", "growth",
]

REJECT_KEYWORDS = [
    "営業", "sales representative", "コールセンター", "call center",
    "事務", "一般事務", "経理", "accounting clerk",
    "接客", "ホール", "キッチン", "調理",
    "介護", "看護", "保育",
    "建設作業", "ドライバー", "配送",
]


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None
    
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                log.error(f"Missing {CREDENTIALS_PATH}. Download from Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def load_processed():
    """Load set of already-processed message IDs."""
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    return set()


def save_processed(processed):
    """Save processed message IDs."""
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(processed), f)


def decode_email_body(payload):
    """Decode email body from Gmail API payload."""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return body


def get_email_details(service, msg_id):
    """Get email subject, sender, body."""
    try:
        msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        
        body = decode_email_body(msg['payload'])
        
        return {
            'id': msg_id,
            'subject': subject,
            'sender': sender,
            'body': body,
            'threadId': msg['threadId']
        }
    except HttpError as e:
        log.error(f"Error getting email {msg_id}: {e}")
        return None


def ai_evaluate_job(sender, subject, body):
    """Use AI to evaluate if the job matches Denpota's interests."""
    prompt = f"""You are evaluating a job email for Denpota Furugaki.

Denpota's interests:
- Software Engineering, AI Development, Full-stack Development, DX/Digital Transformation
- Marketing Engineering (combining dev + marketing)
- MUST be remote or mostly remote (fully remote preferred)
- NOT interested in: pure sales, admin, accounting, manual labor, customer service, non-tech roles

Evaluate this email:
From: {sender}
Subject: {subject}
Body:
{body[:2000]}

Respond with EXACTLY this JSON format:
{{"interested": true/false, "reason": "brief reason", "is_remote": true/false/unknown, "job_type": "brief job type description", "language": "ja/en"}}
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
        return {"interested": False, "reason": "AI evaluation error", "is_remote": False, "job_type": "unknown", "language": "ja"}


def ai_generate_reply(sender, subject, body, interested, language="ja"):
    """Generate a personalized reply using AI."""
    if interested:
        if language == "en":
            prompt = f"""Write a professional reply in English to this job email.
Denpota is INTERESTED. The reply should:
- Thank the recruiter
- Express strong interest
- Briefly highlight relevant experience from Denpota's profile
- Ask about remote work arrangement if not already mentioned
- Ask about next steps (casual interview / call)
- Be concise (under 200 words)

Denpota's profile: {PROFILE_SUMMARY}

From: {sender}
Subject: {subject}
Message: {body[:1500]}

Write ONLY the reply body text (no subject line)."""
        else:
            prompt = f"""Write a professional reply in Japanese to this job email.
Denpota is INTERESTED. The reply should:
- Thank the recruiter
- Express strong interest
- Briefly highlight relevant experience from Denpota's profile
- Ask about remote work arrangement if not already mentioned
- Ask about next steps (casual interview / call)
- Be concise (under 200 chars ideally)

Denpota's profile: {PROFILE_SUMMARY}

From: {sender}
Subject: {subject}
Message: {body[:1500]}

Write ONLY the reply body text (no subject line). Start with company/recruiter acknowledgment."""
    else:
        if language == "en":
            prompt = f"""Write a polite decline reply in English to this job email.
Denpota is NOT interested. The reply should:
- Thank them for reaching out
- Politely decline (e.g. currently not looking for this type of role)
- Keep it short and professional (2-3 sentences)

From: {sender}
Subject: {subject}

Write ONLY the reply body text."""
        else:
            prompt = f"""Write a polite decline reply in Japanese to this job email.
Denpota is NOT interested. The reply should:
- Thank them for reaching out
- Politely decline (e.g. currently not looking for this type of role)
- Keep it short and professional (2-3 sentences)

From: {sender}
Subject: {subject}

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
            if language == "en":
                return f"Thank you for reaching out. I'm very interested in this position and would love to learn more. Could we schedule a casual interview or call to discuss further?\n\nBest regards,\nDenpota Furugaki\ndenpotafurugaki@gmail.com"
            else:
                return f"ご連絡いただきありがとうございます。\n大変興味深いポジションですので、ぜひ詳細をお伺いしたいです。\nカジュアル面談等のお時間をいただけますと幸いです。\n\n古垣 伝法太\ndenpotafurugaki@gmail.com"
        else:
            if language == "en":
                return "Thank you for reaching out. I appreciate the opportunity, but I'm not currently looking for this type of role."
            else:
                return "ご連絡いただきありがとうございます。\n大変恐縮ですが、現在このタイプのポジションは検討しておりません。\nまた機会がございましたら、よろしくお願いいたします。"


def create_reply_draft(service, email, reply_text):
    """Create a draft reply in Gmail."""
    try:
        message = {
            'raw': base64.urlsafe_b64encode(
                f"To: {email['sender']}\nSubject: Re: {email['subject']}\n\n{reply_text}".encode('utf-8')
            ).decode('utf-8')
        }
        
        draft = service.users().drafts().create(
            userId='me',
            body={'message': message}
        ).execute()
        
        return draft['id']
    except HttpError as e:
        log.error(f"Error creating draft: {e}")
        return None


def send_reply(service, email, reply_text):
    """Send a reply email."""
    try:
        message = {
            'raw': base64.urlsafe_b64encode(
                f"To: {email['sender']}\nSubject: Re: {email['subject']}\nIn-Reply-To: {email['id']}\nReferences: {email['id']}\n\n{reply_text}".encode('utf-8')
            ).decode('utf-8'),
            'threadId': email['threadId']
        }
        
        sent = service.users().messages().send(userId='me', body=message).execute()
        return sent['id']
    except HttpError as e:
        log.error(f"Error sending reply: {e}")
        return None


def run_gmail_bot():
    """Main bot: read unread job emails, evaluate, reply."""
    service = get_gmail_service()
    if not service:
        log.error("Failed to authenticate Gmail API")
        return
    
    processed = load_processed()
    log.info(f"Starting Gmail job reply bot. {len(processed)} messages already processed.")
    
    # Build query for unread emails from job platforms
    from_queries = ' OR '.join([f'from:{domain}' for domain in JOB_PLATFORMS])
    query = f'is:unread ({from_queries})'
    
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
        messages = results.get('messages', [])
        
        if not messages:
            log.info("No unread job emails found.")
            return
        
        log.info(f"Found {len(messages)} unread job emails.")
        
        stats = {"processed": 0, "interested": 0, "declined": 0, "skipped": 0, "errors": 0}
        
        for msg in messages:
            msg_id = msg['id']
            
            if msg_id in processed:
                log.info(f"Message {msg_id} already processed, skipping")
                stats["skipped"] += 1
                continue
            
            email = get_email_details(service, msg_id)
            if not email:
                stats["errors"] += 1
                continue
            
            log.info(f"\n--- Email from {email['sender']} ---")
            log.info(f"Subject: {email['subject']}")
            
            # AI evaluation
            evaluation = ai_evaluate_job(email['sender'], email['subject'], email['body'])
            
            interested = evaluation.get("interested", False)
            is_remote = evaluation.get("is_remote", False)
            reason = evaluation.get("reason", "")
            language = evaluation.get("language", "ja")
            
            # If interested but not remote, decline
            if interested and is_remote == False:
                interested = False
                reason = "Interested in role but not remote"
            
            log.info(f"AI: interested={interested}, remote={is_remote}, reason={reason}")
            
            # Generate reply
            reply_text = ai_generate_reply(email['sender'], email['subject'], email['body'], interested, language)
            log.info(f"Reply ({len(reply_text)} chars): {reply_text[:100]}...")
            
            # Send or draft
            if AUTO_SEND:
                sent_id = send_reply(service, email, reply_text)
                if sent_id:
                    log.info(f"✓ Sent reply to {email['sender']}")
                    if interested:
                        stats["interested"] += 1
                    else:
                        stats["declined"] += 1
                else:
                    log.error(f"Failed to send reply")
                    stats["errors"] += 1
            else:
                draft_id = create_reply_draft(service, email, reply_text)
                if draft_id:
                    log.info(f"✓ Created draft reply (ID: {draft_id})")
                    if interested:
                        stats["interested"] += 1
                    else:
                        stats["declined"] += 1
                else:
                    log.error(f"Failed to create draft")
                    stats["errors"] += 1
            
            # Mark as processed and read
            processed.add(msg_id)
            stats["processed"] += 1
            save_processed(processed)
            
            # Mark email as read
            service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        
        log.info(f"\n=== Summary ===")
        log.info(f"Processed: {stats['processed']}")
        log.info(f"Interested: {stats['interested']}")
        log.info(f"Declined: {stats['declined']}")
        log.info(f"Skipped (already done): {stats['skipped']}")
        log.info(f"Errors: {stats['errors']}")
        log.info(f"Mode: {'AUTO-SEND' if AUTO_SEND else 'DRAFT'}")
        
    except HttpError as e:
        log.error(f"Gmail API error: {e}")


if __name__ == "__main__":
    run_gmail_bot()
