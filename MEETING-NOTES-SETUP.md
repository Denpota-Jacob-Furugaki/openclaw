# Meeting Notes Integration for OpenClaw

This integration allows OpenClaw to access your meeting notes from Fireflies.ai and Tactiq to better understand context and support you.

## Features

- ✅ **Sync meeting transcripts** from Fireflies.ai and Tactiq
- ✅ **Search meetings** by keyword, date, or participant
- ✅ **Export context** for OpenClaw agent to use in conversations
- ✅ **Automatic cron job** to keep meetings up-to-date
- ✅ **Knowledge base** organized by date and source

## Setup Instructions

### 1. Get API Keys

#### Fireflies.ai API Key
1. Go to https://app.fireflies.ai/integrations
2. Look for "API" or "Developer" section
3. Generate an API key
4. Add to `.env`: `FIREFLIES_API_KEY=your_key_here`

#### Tactiq API Key
1. Go to https://app.tactiq.io/#/settings
2. Look for "API Access" or "Integrations"
3. Generate an API key
4. Add to `.env`: `TACTIQ_API_KEY=your_key_here`

**Note:** Both services use your Google account (denpotafurugaki@gmail.com) for authentication.

### 2. Initial Sync

Run the sync script to download all your meeting notes:

```powershell
cd C:\Users\denpo\.openclaw\integrations
python sync_all_meetings.py
```

This will:
- Fetch all meetings from Fireflies and Tactiq
- Save transcripts as JSON and markdown files
- Create a searchable knowledge base

### 3. Set Up Automatic Sync (Optional)

Add a cron job to sync meetings daily:

```powershell
cd C:\Users\denpo\.openclaw
npx --no openclaw cron add "Daily Meeting Sync" "0 8 * * *" "python C:\Users\denpo\.openclaw\integrations\sync_all_meetings.py"
```

This runs every morning at 8 AM to fetch new meetings.

## Usage

### Search Meetings

```python
from integrations.meeting_knowledge_base import MeetingKnowledgeBase

kb = MeetingKnowledgeBase()

# Search by keyword
results = kb.search_meetings(query="budget discussion")

# Get recent meetings
recent = kb.get_recent_meetings(limit=10)

# Search meetings from last 7 days
recent_week = kb.search_meetings(days_ago=7)

# Export context for OpenClaw
context = kb.export_context_for_agent(query="project timeline")
```

### In OpenClaw Agent

Create a skill that loads meeting context:

```python
# In your agent prompt or skill:
from integrations.meeting_knowledge_base import MeetingKnowledgeBase

kb = MeetingKnowledgeBase()
context = kb.export_context_for_agent(max_meetings=5)

# Use context in conversation
print(context)
```

## File Structure

```
C:\Users\denpo\.openclaw\
├── integrations/
│   ├── fireflies_sync.py       # Fireflies API integration
│   ├── tactiq_sync.py           # Tactiq API integration
│   ├── meeting_knowledge_base.py # Search and query meetings
│   └── sync_all_meetings.py     # Main sync script
│
└── knowledge_base/
    └── meetings/
        ├── fireflies/
        │   ├── 2026-03-24_Team-Meeting_abc123.json
        │   ├── 2026-03-24_Team-Meeting_abc123.md
        │   └── ...
        └── tactiq/
            ├── 2026-03-23_Client-Call_xyz789.json
            ├── 2026-03-23_Client-Call_xyz789.md
            └── ...
```

## Benefits for OpenClaw

With this integration, OpenClaw can:

1. **Understand past decisions** - Reference previous meetings when discussing projects
2. **Track action items** - Know what was promised and follow up
3. **Remember participants** - Understand team dynamics and roles
4. **Provide context** - Answer questions like "What did we decide about X in that meeting?"
5. **Suggest next steps** - Based on action items from meetings

## Privacy & Security

- All meeting notes are stored **locally** on your machine
- API keys are stored in `.env` (already in .gitignore)
- No data is shared externally except API calls to Fireflies/Tactiq
- You have full control over what meetings are synced

## Troubleshooting

### "Failed to fetch meetings"
- Check your API keys in `.env`
- Verify you're logged into Fireflies/Tactiq with denpotafurugaki@gmail.com
- Check internet connection

### "No meetings found"
- Run the initial sync: `python sync_all_meetings.py`
- Check if you have meetings in the web interfaces first

### "Import error"
- Make sure you're in the correct directory
- Check Python packages are installed: `pip install requests`

## Next Steps

1. ✅ Set up API keys
2. ✅ Run initial sync
3. ✅ Test search functionality
4. ✅ Set up cron job for automatic syncing
5. ✅ Create OpenClaw skills that use meeting context
