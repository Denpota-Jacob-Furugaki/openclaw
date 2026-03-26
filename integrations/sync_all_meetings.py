"""
Sync All Meeting Notes
Main script to sync meetings from both Fireflies and Tactiq
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.fireflies_sync import FirefliesSync
from integrations.tactiq_sync import TactiqSync
from integrations.meeting_knowledge_base import MeetingKnowledgeBase

def main():
    print("=" * 60)
    print("  Meeting Notes Sync for OpenClaw")
    print("=" * 60)
    print()
    
    total_synced = 0
    
    # Sync Fireflies
    print("📝 Syncing Fireflies.ai meetings...")
    print("-" * 60)
    try:
        fireflies = FirefliesSync()
        count = fireflies.sync_all()
        if count:
            total_synced += count
            print(f"✓ Synced {count} meetings from Fireflies\n")
    except Exception as e:
        print(f"✗ Fireflies sync failed: {e}\n")
    
    # Sync Tactiq
    print("📝 Syncing Tactiq meetings...")
    print("-" * 60)
    try:
        tactiq = TactiqSync()
        count = tactiq.sync_all()
        if count:
            total_synced += count
            print(f"✓ Synced {count} meetings from Tactiq\n")
    except Exception as e:
        print(f"✗ Tactiq sync failed: {e}\n")
    
    # Show summary
    print("=" * 60)
    print("  Knowledge Base Summary")
    print("=" * 60)
    kb = MeetingKnowledgeBase()
    summary = kb.get_meeting_summary()
    print(f"Total meetings in knowledge base: {summary['total_meetings']}")
    print(f"  • Fireflies: {summary['fireflies_meetings']}")
    print(f"  • Tactiq: {summary['tactiq_meetings']}")
    print()
    
    if summary['total_meetings'] > 0:
        print("Recent meetings:")
        recent = kb.get_recent_meetings(limit=5)
        for i, meeting in enumerate(recent, 1):
            print(f"  {i}. [{meeting['source']}] {meeting['title']}")
    
    print()
    print("✓ Sync complete! OpenClaw can now access your meeting notes.")
    print(f"  Location: C:\\Users\\denpo\\.openclaw\\knowledge_base\\meetings\\")

if __name__ == "__main__":
    main()
