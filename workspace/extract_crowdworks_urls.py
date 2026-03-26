"""Extract CrowdWorks URLs from emails."""
import check_interview_requests
import re

get_gmail_service = check_interview_requests.get_gmail_service
decode_body = check_interview_requests.decode_body

service = get_gmail_service()

# Get the CrowdWorks emails
email_ids = [
    '19d1d891bc78d683',  # ALL BLUE (most recent)
    '19d19e658470acd4',  # ALL BLUE (earlier)
    '19d19ab7e2860338',  # Job35423
]

for email_id in email_ids:
    msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
    body = decode_body(msg['payload'])
    
    email = {'subject': subject, 'sender': sender, 'body': body}
    print(f"\n=== {email['subject']} ===")
    print(f"From: {email['sender']}")
    
    # Extract URLs
    urls = re.findall(r'https://crowdworks\.jp[^\s<>\"\'\)]+', email['body'])
    urls = [url.rstrip('.') for url in urls]  # Remove trailing dots
    
    if urls:
        print(f"URLs found:")
        for url in urls[:3]:
            print(f"  {url}")
    else:
        print("No URLs found")
