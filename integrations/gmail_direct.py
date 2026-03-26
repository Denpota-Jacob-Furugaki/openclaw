"""
Direct Gmail Integration for OpenClaw
Sends emails directly via Gmail API (no browser automation needed)
"""

import os
import base64
from email.mime.text import MIMEText
from google_auth import get_google_creds
from googleapiclient.discovery import build

class GmailDirect:
    def __init__(self):
        self.creds = get_google_creds()
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def send_email(self, to, subject, body, thread_id=None):
        """Send email directly via Gmail API"""
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        email_msg = {'raw': raw}
        if thread_id:
            email_msg['threadId'] = thread_id
        
        try:
            sent = self.service.users().messages().send(
                userId='me',
                body=email_msg
            ).execute()
            print(f"✓ Email sent! Message ID: {sent['id']}")
            return sent
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return None
    
    def reply_to_thread(self, thread_id, body):
        """Reply to an existing email thread"""
        # Get the thread to extract recipient and subject
        thread = self.service.users().threads().get(
            userId='me',
            id=thread_id
        ).execute()
        
        messages = thread['messages']
        if not messages:
            print("No messages in thread")
            return None
        
        # Get last message
        last_msg = messages[-1]
        headers = {h['name']: h['value'] for h in last_msg['payload']['headers']}
        
        # Extract reply-to or from
        to = headers.get('Reply-To', headers.get('From'))
        subject = headers.get('Subject', '')
        
        # Add Re: if not already there
        if not subject.startswith('Re:'):
            subject = f"Re: {subject}"
        
        return self.send_email(to, subject, body, thread_id=thread_id)

if __name__ == "__main__":
    # Test
    gmail = GmailDirect()
    
    # Example: Send test email
    # gmail.send_email(
    #     to="recipient@example.com",
    #     subject="Test from OpenClaw",
    #     body="This email was sent directly via Gmail API!"
    # )
    
    print("Gmail Direct integration ready!")
    print("Use gmail.send_email() to send emails")
    print("Use gmail.reply_to_thread() to reply to threads")
