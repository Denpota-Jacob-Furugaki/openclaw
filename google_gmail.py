"""Gmail integration for OpenClaw.
Read, send, search, and manage emails via Gmail API.
"""
import os
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

from google_auth import get_google_credentials
from googleapiclient.discovery import build


def get_gmail_service():
    """Build and return a Gmail API service."""
    creds = get_google_credentials()
    return build('gmail', 'v1', credentials=creds)


def search_emails(query='', max_results=10):
    """Search for emails matching a query.
    
    Args:
        query: Gmail search query (e.g., 'from:example@gmail.com is:unread')
        max_results: Maximum number of results to return
    
    Returns:
        List of email summaries with id, threadId, subject, from, date
    """
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    email_list = []
    
    for msg in messages:
        email = get_email_summary(msg['id'])
        email_list.append(email)
    
    return email_list


def get_email_summary(message_id):
    """Get summary of an email (subject, from, date, snippet)."""
    service = get_gmail_service()
    msg = service.users().messages().get(userId='me', id=message_id, format='metadata').execute()
    
    headers = msg.get('payload', {}).get('headers', [])
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No subject')
    from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
    
    return {
        'id': msg['id'],
        'threadId': msg['threadId'],
        'subject': subject,
        'from': from_addr,
        'date': date,
        'snippet': msg.get('snippet', ''),
        'labels': msg.get('labelIds', [])
    }


def get_email_full(message_id):
    """Get full email content including body."""
    service = get_gmail_service()
    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    
    headers = msg.get('payload', {}).get('headers', [])
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No subject')
    from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
    to_addr = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
    
    body = _get_body(msg.get('payload', {}))
    
    return {
        'id': msg['id'],
        'threadId': msg['threadId'],
        'subject': subject,
        'from': from_addr,
        'to': to_addr,
        'date': date,
        'body': body,
        'labels': msg.get('labelIds', [])
    }


def _get_body(payload):
    """Extract text body from email payload."""
    if payload.get('body', {}).get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
    
    parts = payload.get('parts', [])
    
    # Try plain text first
    for part in parts:
        if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
    
    # Try HTML if no plain text
    for part in parts:
        if part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
    
    # Recurse into multipart
    for part in parts:
        if part.get('parts'):
            result = _get_body(part)
            if result:
                return result
    
    return ""


def send_email(to, subject, body, attachments=None, thread_id=None):
    """Send an email via Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        attachments: List of file paths to attach
        thread_id: If replying, the thread ID to reply to
    
    Returns:
        Sent message object
    """
    service = get_gmail_service()
    
    msg = MIMEMultipart()
    msg['to'] = to
    msg['subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Attach files
    if attachments:
        for file_path in attachments:
            if not os.path.exists(file_path):
                print(f"Warning: Attachment not found: {file_path}")
                continue
            
            content_type, encoding = mimetypes.guess_type(file_path)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            
            main_type, sub_type = content_type.split('/', 1)
            
            with open(file_path, 'rb') as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
                encoders.encode_base64(part)
                
                filename = os.path.basename(file_path)
                part.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', filename))
                msg.attach(part)
    
    raw = base64.urlsafe_b64decode(msg.as_bytes()).decode('utf-8')
    body = {'raw': raw}
    
    if thread_id:
        body['threadId'] = thread_id
    
    result = service.users().messages().send(userId='me', body=body).execute()
    return result


def get_unread_count():
    """Get count of unread emails."""
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=1
    ).execute()
    
    return results.get('resultSizeEstimate', 0)


def mark_as_read(message_id):
    """Mark an email as read."""
    service = get_gmail_service()
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()


def mark_as_unread(message_id):
    """Mark an email as unread."""
    service = get_gmail_service()
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'addLabelIds': ['UNREAD']}
    ).execute()


if __name__ == '__main__':
    # Test: Get recent emails
    print("Fetching recent emails...")
    emails = search_emails(query='', max_results=5)
    
    for i, email in enumerate(emails, 1):
        print(f"\n{i}. {email['subject']}")
        print(f"   From: {email['from']}")
        print(f"   Date: {email['date']}")
        print(f"   Snippet: {email['snippet'][:100]}...")
    
    print(f"\n✓ Unread emails: {get_unread_count()}")
