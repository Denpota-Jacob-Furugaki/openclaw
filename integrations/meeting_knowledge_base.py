"""
Meeting Knowledge Base Manager
Manages and queries meeting notes for OpenClaw context
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

class MeetingKnowledgeBase:
    def __init__(self):
        self.base_path = Path("C:/Users/denpo/.openclaw/knowledge_base/meetings")
        self.fireflies_path = self.base_path / "fireflies"
        self.tactiq_path = self.base_path / "tactiq"
        
    def search_meetings(self, query=None, days_ago=None, participant=None):
        """Search meetings by keyword, date range, or participant"""
        results = []
        
        # Search both sources
        for source_path in [self.fireflies_path, self.tactiq_path]:
            if not source_path.exists():
                continue
                
            for md_file in source_path.glob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Filter by date
                    if days_ago:
                        file_date = md_file.stem.split('_')[0]
                        file_datetime = datetime.strptime(file_date, "%Y-%m-%d")
                        cutoff = datetime.now() - timedelta(days=days_ago)
                        if file_datetime < cutoff:
                            continue
                    
                    # Filter by query
                    if query and query.lower() not in content.lower():
                        continue
                    
                    # Filter by participant
                    if participant and participant.lower() not in content.lower():
                        continue
                    
                    results.append({
                        "file": str(md_file),
                        "title": md_file.stem,
                        "source": "Fireflies" if "fireflies" in str(source_path) else "Tactiq",
                        "content": content[:500] + "..." if len(content) > 500 else content
                    })
                except Exception as e:
                    print(f"Error reading {md_file}: {e}")
        
        return results
    
    def get_recent_meetings(self, limit=10):
        """Get most recent meetings"""
        all_files = []
        
        for source_path in [self.fireflies_path, self.tactiq_path]:
            if not source_path.exists():
                continue
            all_files.extend(source_path.glob("*.md"))
        
        # Sort by modification time
        all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        results = []
        for md_file in all_files[:limit]:
            try:
                content = md_file.read_text(encoding='utf-8')
                results.append({
                    "file": str(md_file),
                    "title": md_file.stem,
                    "source": "Fireflies" if "fireflies" in str(md_file) else "Tactiq",
                    "preview": content[:300] + "..."
                })
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        return results
    
    def get_meeting_summary(self):
        """Get overall meeting statistics"""
        fireflies_count = len(list(self.fireflies_path.glob("*.md"))) if self.fireflies_path.exists() else 0
        tactiq_count = len(list(self.tactiq_path.glob("*.md"))) if self.tactiq_path.exists() else 0
        
        return {
            "total_meetings": fireflies_count + tactiq_count,
            "fireflies_meetings": fireflies_count,
            "tactiq_meetings": tactiq_count,
            "last_sync": datetime.now().isoformat()
        }
    
    def export_context_for_agent(self, query=None, max_meetings=5):
        """Export meeting context for OpenClaw agent"""
        meetings = self.search_meetings(query=query) if query else self.get_recent_meetings(limit=max_meetings)
        
        context = "# Meeting Notes Context\n\n"
        context += f"Found {len(meetings)} relevant meetings:\n\n"
        
        for meeting in meetings[:max_meetings]:
            context += f"## {meeting['title']}\n"
            context += f"**Source:** {meeting['source']}\n\n"
            
            # Read full content
            try:
                full_content = Path(meeting['file']).read_text(encoding='utf-8')
                context += full_content + "\n\n---\n\n"
            except:
                context += meeting.get('content', meeting.get('preview', '')) + "\n\n---\n\n"
        
        return context

if __name__ == "__main__":
    kb = MeetingKnowledgeBase()
    summary = kb.get_meeting_summary()
    print(f"Knowledge Base Summary:")
    print(f"  Total meetings: {summary['total_meetings']}")
    print(f"  Fireflies: {summary['fireflies_meetings']}")
    print(f"  Tactiq: {summary['tactiq_meetings']}")
    
    if summary['total_meetings'] == 0:
        print("\nNo meetings found. Run fireflies_sync.py and tactiq_sync.py first!")
