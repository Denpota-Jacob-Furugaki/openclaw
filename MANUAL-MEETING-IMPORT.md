# Manual Meeting Import Guide

Since Fireflies and Tactiq don't provide direct API access (or require paid plans), use this manual import system instead.

## 📁 Import Folder

Place your exported meeting files here:
```
C:\Users\denpo\.openclaw\meeting_imports\
```

## How to Export and Import

### From Tactiq (app.tactiq.io)

1. **Open a meeting transcript:**
   - Go to https://app.tactiq.io/#/transcripts
   - Click on any meeting

2. **Export the meeting:**
   - Click the "Export" or "Download" button
   - Choose one of these formats:
     - **JSON** (best option - includes all metadata)
     - **TXT** (text only)
     - **MD** (Markdown)
   
3. **Save to import folder:**
   - Save the file to: `C:\Users\denpo\.openclaw\meeting_imports\`
   - Filename doesn't matter - the script will detect and organize it

4. **Run import script:**
   ```powershell
   cd C:\Users\denpo\.openclaw\integrations
   python manual_import.py
   ```

### From Fireflies (app.fireflies.ai)

1. **Open a meeting:**
   - Go to https://app.fireflies.ai/notebook/all
   - Click on any meeting

2. **Export the meeting:**
   - Look for "Export" or download icon (usually top-right)
   - Choose format:
     - **JSON** (recommended)
     - **TXT** or **Docx** (will be converted)

3. **Save to import folder:**
   - Save to: `C:\Users\denpo\.openclaw\meeting_imports\`

4. **Run import script:**
   ```powershell
   cd C:\Users\denpo\.openclaw\integrations
   python manual_import.py
   ```

### Manual Copy/Paste Method

If export isn't available:

1. **Copy the transcript:**
   - Open the meeting in your browser
   - Select and copy all the text (Ctrl+A, Ctrl+C)

2. **Create a text file:**
   - Create a new `.txt` file in `C:\Users\denpo\.openclaw\meeting_imports\`
   - Name it something like: `2026-03-25_Team_Meeting.txt`
   - Paste the content

3. **Add a title (first line):**
   ```
   Team Meeting - Q1 Planning
   
   [rest of the transcript...]
   ```

4. **Run import script:**
   ```powershell
   cd C:\Users\denpo\.openclaw\integrations
   python manual_import.py
   ```

## Bulk Import Multiple Meetings

To import many meetings at once:

1. **Export multiple meetings** from Tactiq/Fireflies
2. **Save all to the import folder** (can be 10, 20, 100+ files)
3. **Run the import script once** - it will process all files

```powershell
cd C:\Users\denpo\.openclaw\integrations
python manual_import.py
```

The script will:
- ✅ Detect the source (Fireflies, Tactiq, or generic)
- ✅ Extract all metadata (title, date, participants, action items)
- ✅ Create searchable markdown files
- ✅ Move processed files to `meeting_imports/processed/`
- ✅ Organize everything in the knowledge base

## Automatic Processing (Optional)

Set up a cron job to automatically import any new files dropped into the folder:

```powershell
cd C:\Users\denpo\.openclaw
npx --no openclaw cron add "Auto Import Meetings" "*/30 * * * *" "python C:\Users\denpo\.openclaw\integrations\manual_import.py"
```

This checks for new meeting files every 30 minutes.

## Where Meetings Are Stored

After import, meetings are organized here:

```
C:\Users\denpo\.openclaw\knowledge_base\meetings\
├── fireflies/          # Fireflies meetings
│   ├── 2026-03-25_Team_Meeting_abc123.json
│   └── 2026-03-25_Team_Meeting_abc123.md
│
├── tactiq/             # Tactiq meetings
│   ├── 2026-03-24_Client_Call_xyz789.json
│   └── 2026-03-24_Client_Call_xyz789.md
│
└── manual/             # Manually imported meetings
    └── 2026-03-23_Quick_Sync.md
```

## Search Your Meetings

After importing, use the knowledge base to search:

```python
from integrations.meeting_knowledge_base import MeetingKnowledgeBase

kb = MeetingKnowledgeBase()

# Search by keyword
results = kb.search_meetings(query="budget")

# Get recent meetings
recent = kb.get_recent_meetings(limit=10)

# Get meetings from last week
last_week = kb.search_meetings(days_ago=7)
```

## Browser Extension Alternative (Advanced)

If you have many meetings, you could also:

1. Use a browser extension to scrape Tactiq pages
2. Create a simple Python script with Selenium to automate exports
3. Set up a bookmark that exports the current page

Let me know if you want help with any of these!

## Example Workflow

**Weekly meeting import routine:**

1. Monday morning: Export last week's meetings from Tactiq/Fireflies
2. Drop all files into `C:\Users\denpo\.openclaw\meeting_imports\`
3. Run: `python integrations\manual_import.py`
4. Done! OpenClaw now has context from all your meetings

Takes 2-3 minutes per week for ~10 meetings.

## Troubleshooting

**"No files found"**
- Check you saved files to the correct folder
- Verify file extensions are `.json`, `.txt`, or `.md`

**"Error importing"**
- Check the file isn't corrupted
- Try opening it in a text editor first
- File might be in an unexpected format

**"File already exists"**
- The meeting was already imported
- Check `meeting_imports/processed/` folder
- Or check the knowledge base folders

## Tips

- **JSON format is best** - includes all metadata, action items, participants
- **Name files clearly** - helps you find them later
- **Regular imports** - weekly routine keeps knowledge base current
- **Backup originals** - keep a backup of raw exports somewhere safe
