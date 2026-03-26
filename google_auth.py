"""Google OAuth2 authentication helper for OpenClaw.
Handles authentication for Gmail, Calendar, Drive, Docs, and Sheets APIs.
"""
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# All scopes we need
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
]

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'google_token.json')
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'google_credentials.json')


def get_google_credentials():
    """Get valid Google OAuth2 credentials, refreshing or re-authenticating as needed."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}. Download it from Google Cloud Console:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Create a project or select existing\n"
                    "3. Enable Gmail, Calendar, Drive, Docs, Sheets APIs\n"
                    "4. Create OAuth 2.0 credentials (Desktop app)\n"
                    "5. Download JSON and save as google_credentials.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


if __name__ == '__main__':
    print("Authenticating with Google...")
    try:
        creds = get_google_credentials()
        print(f"✓ Success! Token saved to {TOKEN_FILE}")
        print(f"✓ Token valid: {creds.valid}")
        print(f"✓ Scopes: {len(SCOPES)}")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
