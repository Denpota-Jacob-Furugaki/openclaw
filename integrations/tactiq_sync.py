"""
Tactiq Meeting Notes Integration
Fetches meeting transcripts from Tactiq
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from google_auth import get_google_creds

class TactiqSync:
    def __init__(self):
        self.base_url = "https://api.tactiq.io/v1"
        self.knowledge_base = Path("C:/Users/denpo/.openclaw/knowledge_base/meetings/tactiq")
        self.knowledge_base.mkdir(parents=True, exist_ok=True)
        self.api_key = os.getenv("TACTIQ_API_KEY")
        
    def get_headers(self):
        """Get API headers with authentication"""
        if self.api_key:
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        else:
            # Tactiq might use Google OAuth directly
            creds = get_google_creds()
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {creds.token}"
            }
    
    def fetch_transcripts(self, limit=50):
        """Fetch recent meeting transcripts from Tactiq"""
        try:
            response = requests.get(
                f"{self.base_url}/transcripts",
                headers=self.get_headers(),
                params={"limit": limit},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Tactiq transcripts: {e}")
            print("Note: You may need to get an API key from Tactiq settings")
            return None
    
    def save_meeting(self, transcript):
        """Save meeting to knowledge base"""
        meeting_id = transcript.get("id", "unknown")
        title = transcript.get("title", "Untitled Meeting")
        date = transcript.get("createdAt", transcript.get("date", "unknown"))
        
        # Create filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        if isinstance(date, str):
            date_str = date[:10]
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        filename = f"{date_str}_{safe_title}_{meeting_id}.json"
        filepath = self.knowledge_base / filename
        
        # Save full transcript
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        # Create markdown summary
        md_filepath = filepath.with_suffix('.md')
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Date:** {date}\n")
            
            participants = transcript.get('participants', [])
            if participants:
                f.write(f"**Participants:** {', '.join(participants)}\n\n")
            
            # Add summary if available
            summary = transcript.get('summary', '')
            if summary:
                f.write(f"## Summary\n{summary}\n\n")
            
            # Add key points
            key_points = transcript.get('keyPoints', [])
            if key_points:
                f.write(f"## Key Points\n")
                for point in key_points:
                    f.write(f"- {point}\n")
                f.write("\n")
            
            # Add action items
            action_items = transcript.get('actionItems', [])
            if action_items:
                f.write(f"## Action Items\n")
                for item in action_items:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # Add transcript
            content = transcript.get('content', transcript.get('transcript', ''))
            if content:
                f.write(f"## Transcript\n\n{content}\n")
        
        return filepath
    
    def sync_all(self):
        """Sync all recent meetings"""
        print("Fetching meetings from Tactiq...")
        data = self.fetch_transcripts(limit=100)
        
        if not data:
            print("Failed to fetch meetings")
            print("\nTo get Tactiq API access:")
            print("1. Go to https://app.tactiq.io/#/settings")
            print("2. Look for 'API' or 'Integrations' section")
            print("3. Generate an API key")
            print("4. Add it to your .env file: TACTIQ_API_KEY=your_key_here")
            return 0
        
        transcripts = data.get('transcripts', data if isinstance(data, list) else [])
        print(f"Found {len(transcripts)} meetings")
        
        for transcript in transcripts:
            try:
                filepath = self.save_meeting(transcript)
                print(f"✓ Saved: {transcript.get('title', 'Untitled')}")
            except Exception as e:
                print(f"✗ Error saving {transcript.get('title', 'Untitled')}: {e}")
        
        print(f"\nSync complete! Meetings saved to: {self.knowledge_base}")
        return len(transcripts)

if __name__ == "__main__":
    sync = TactiqSync()
    sync.sync_all()
