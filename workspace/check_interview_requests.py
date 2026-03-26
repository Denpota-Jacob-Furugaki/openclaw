"""
Check Gmail for Interview/Meeting Requests
Alerts when recruiters want to schedule interviews or meetings
"""
import os
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN_PATH = 'google_token.json'

# Interview/meeting keywords
INTERVIEW_KEYWORDS = [
    'interview', '面接', '面談', 'カジュアル面談',
    'meet', 'meeting', 'schedule', 'zoom', 'google meet',
    'teams', 'skype', 'call', 'オンライン面談',
    'ご都合', 'available', 'availability', '日程',
    '面接日程', '面談希望'
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
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    return body


def check_interviews():
    """Check for interview/meeting requests in recent unread emails."""
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
                results.append({
                    'id': msg['id'],
                    'from': sender,
                    'subject': subject,
                    'date': date,
                    'matched_keywords': matched_keywords,
                    'snippet': body[:300] + '...' if len(body) > 300 else body
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
    """Format alert message."""
    if data["status"] != "ok":
        return f"⚠️ Error checking Gmail: {data.get('error', 'Unknown error')}"
    
    if data["count"] == 0:
        return None  # No alert needed
    
    alert = f"🎯 **{data['count']} Interview/Meeting Request(s) Found!**\n\n"
    
    for i, interview in enumerate(data["interviews"], 1):
        alert += f"**{i}. {interview['subject']}**\n"
        alert += f"   From: {interview['from']}\n"
        alert += f"   Date: {interview['date']}\n"
        alert += f"   Keywords: {', '.join(interview['matched_keywords'][:3])}\n"
        alert += f"   Preview: {interview['snippet'][:150]}...\n\n"
    
    alert += f"\n📧 Check Gmail: https://mail.google.com/mail/u/0/#inbox"
    
    return alert


if __name__ == "__main__":
    result = check_interviews()
    
    if result:
        alert = format_alert(result)
        if alert:
            # Write to file instead of printing (Windows console encoding issues)
            with open('interview_alert.txt', 'w', encoding='utf-8') as f:
                f.write(alert)
            print("ALERT_FILE_WRITTEN")
        else:
            print("NO_INTERVIEWS")
        
        # Save result for tracking
        with open('last_interview_check.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print("CHECK_FAILED")
