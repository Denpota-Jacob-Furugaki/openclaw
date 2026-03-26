"""
Fireflies.ai Meeting Notes Integration
Fetches meeting transcripts and summaries from Fireflies.ai
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

class FirefliesSync:
    def __init__(self):
        self.base_url = "https://api.fireflies.ai/graphql"
        self.api_key = os.getenv("FIREFLIES_API_KEY")
        self.knowledge_base = Path("C:/Users/denpo/.openclaw/knowledge_base/meetings/fireflies")
        self.knowledge_base.mkdir(parents=True, exist_ok=True)
        
    def get_headers(self):
        """Get API headers with authentication"""
        return {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
    
    def verify_api_key(self):
        """Verify API key is working"""
        query = """
        query {
          user {
            email
            name
          }
        }
        """
        
        try:
            response = requests.post(
                self.base_url,
                json={"query": query},
                headers=self.get_headers(),
                timeout=10
            )
            print(f"API Response Status: {response.status_code}")
            print(f"API Response: {response.text[:500]}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error verifying API key: {e}")
            return None
    
    def fetch_transcripts(self, limit=50):
        """Fetch recent meeting transcripts"""
        query = """
        query {
          transcripts {
            id
            title
            date
            duration
          }
        }
        """
        
        try:
            response = requests.post(
                self.base_url,
                json={"query": query},
                headers=self.get_headers(),
                timeout=30
            )
            print(f"Fetch Response Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response body: {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Fireflies transcripts: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response body: {e.response.text[:500]}")
            return None
    
    def save_meeting(self, transcript):
        """Save meeting to knowledge base"""
        meeting_id = transcript.get("id")
        title = transcript.get("title", "Untitled Meeting")
        date = transcript.get("date", "unknown")
        
        # Create filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{date[:10]}_{safe_title}_{meeting_id}.json"
        filepath = self.knowledge_base / filename
        
        # Save full transcript
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        # Create markdown summary
        md_filepath = filepath.with_suffix('.md')
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Date:** {date}\n")
            f.write(f"**Duration:** {transcript.get('duration', 'N/A')} minutes\n")
            
            participants = transcript.get('participants', [])
            if participants:
                f.write(f"**Participants:** {', '.join([p['name'] for p in participants])}\n\n")
            
            summary = transcript.get('summary', {})
            if summary:
                if summary.get('overview'):
                    f.write(f"## Overview\n{summary['overview']}\n\n")
                
                if summary.get('action_items'):
                    f.write(f"## Action Items\n")
                    for item in summary['action_items']:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                if summary.get('keywords'):
                    f.write(f"**Keywords:** {', '.join(summary['keywords'])}\n\n")
            
            # Add transcript
            sentences = transcript.get('sentences', [])
            if sentences:
                f.write(f"## Transcript\n\n")
                for sentence in sentences:
                    speaker = sentence.get('speaker_name', 'Unknown')
                    text = sentence.get('text', '')
                    f.write(f"**{speaker}:** {text}\n\n")
        
        return filepath
    
    def sync_all(self):
        """Sync all recent meetings"""
        print("Verifying Fireflies API key...")
        verify_result = self.verify_api_key()
        if verify_result:
            print(f"✓ API key verified")
        
        print("\nFetching meetings from Fireflies.ai...")
        data = self.fetch_transcripts(limit=100)
        
        if not data or 'data' not in data:
            print("Failed to fetch meetings")
            return
        
        transcripts = data['data'].get('transcripts', [])
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
    sync = FirefliesSync()
    sync.sync_all()
