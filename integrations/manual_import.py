"""
Manual Meeting Import System
Imports meeting transcripts from exported files (Fireflies, Tactiq, etc.)
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re

class ManualMeetingImporter:
    def __init__(self):
        self.import_folder = Path("C:/Users/denpo/.openclaw/meeting_imports")
        self.knowledge_base = Path("C:/Users/denpo/.openclaw/knowledge_base/meetings")
        self.processed_folder = self.import_folder / "processed"
        
        # Create folders
        self.import_folder.mkdir(parents=True, exist_ok=True)
        self.processed_folder.mkdir(parents=True, exist_ok=True)
        (self.knowledge_base / "fireflies").mkdir(parents=True, exist_ok=True)
        (self.knowledge_base / "tactiq").mkdir(parents=True, exist_ok=True)
        (self.knowledge_base / "manual").mkdir(parents=True, exist_ok=True)
    
    def detect_source(self, data):
        """Detect if file is from Fireflies, Tactiq, or generic"""
        if isinstance(data, dict):
            # Check for Fireflies indicators
            if 'fireflies' in str(data).lower() or 'sentences' in data:
                return 'fireflies'
            # Check for Tactiq indicators
            if 'tactiq' in str(data).lower() or 'source' in data and data.get('source') == 'tactiq':
                return 'tactiq'
            # Generic meeting format
            if 'transcript' in data or 'title' in data:
                return 'manual'
        return 'unknown'
    
    def import_fireflies_json(self, filepath, data):
        """Import Fireflies JSON export"""
        title = data.get('title', 'Untitled Meeting')
        date = data.get('date', data.get('created_at', datetime.now().isoformat()))
        meeting_id = data.get('id', data.get('meeting_id', Path(filepath).stem))
        
        # Extract date for filename
        date_str = date[:10] if isinstance(date, str) and len(date) >= 10 else datetime.now().strftime("%Y-%m-%d")
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:50]
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        output_dir = self.knowledge_base / "fireflies"
        json_path = output_dir / f"{date_str}_{safe_title}_{meeting_id}.json"
        md_path = json_path.with_suffix('.md')
        
        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Create markdown
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Date:** {date}\n")
            f.write(f"**Source:** Fireflies.ai\n")
            
            duration = data.get('duration', data.get('duration_minutes'))
            if duration:
                f.write(f"**Duration:** {duration} minutes\n")
            
            participants = data.get('participants', [])
            if participants:
                names = [p.get('name', p) if isinstance(p, dict) else p for p in participants]
                f.write(f"**Participants:** {', '.join(names)}\n")
            
            f.write("\n")
            
            # Summary section
            summary = data.get('summary', {})
            if summary:
                if summary.get('overview'):
                    f.write(f"## Overview\n{summary['overview']}\n\n")
                
                action_items = summary.get('action_items', summary.get('actionItems', []))
                if action_items:
                    f.write(f"## Action Items\n")
                    for item in action_items:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                keywords = summary.get('keywords', [])
                if keywords:
                    f.write(f"**Keywords:** {', '.join(keywords)}\n\n")
            
            # Transcript
            transcript = data.get('transcript', data.get('transcript_text', ''))
            sentences = data.get('sentences', [])
            
            if sentences:
                f.write(f"## Transcript\n\n")
                for sentence in sentences:
                    if isinstance(sentence, dict):
                        speaker = sentence.get('speaker_name', sentence.get('speaker', 'Unknown'))
                        text = sentence.get('text', '')
                        f.write(f"**{speaker}:** {text}\n\n")
                    else:
                        f.write(f"{sentence}\n\n")
            elif transcript:
                f.write(f"## Transcript\n\n{transcript}\n")
        
        return md_path
    
    def import_tactiq_json(self, filepath, data):
        """Import Tactiq JSON export"""
        title = data.get('title', data.get('name', 'Untitled Meeting'))
        date = data.get('date', data.get('createdAt', data.get('created_at', datetime.now().isoformat())))
        meeting_id = data.get('id', Path(filepath).stem)
        
        # Extract date for filename
        date_str = date[:10] if isinstance(date, str) and len(date) >= 10 else datetime.now().strftime("%Y-%m-%d")
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:50]
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        output_dir = self.knowledge_base / "tactiq"
        json_path = output_dir / f"{date_str}_{safe_title}_{meeting_id}.json"
        md_path = json_path.with_suffix('.md')
        
        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Create markdown
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Date:** {date}\n")
            f.write(f"**Source:** Tactiq\n")
            
            participants = data.get('participants', [])
            if participants:
                f.write(f"**Participants:** {', '.join(participants)}\n")
            
            f.write("\n")
            
            # Summary
            summary = data.get('summary', '')
            if summary:
                f.write(f"## Summary\n{summary}\n\n")
            
            # Key points
            key_points = data.get('keyPoints', data.get('key_points', []))
            if key_points:
                f.write(f"## Key Points\n")
                for point in key_points:
                    f.write(f"- {point}\n")
                f.write("\n")
            
            # Action items
            action_items = data.get('actionItems', data.get('action_items', []))
            if action_items:
                f.write(f"## Action Items\n")
                for item in action_items:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # Transcript
            transcript = data.get('transcript', data.get('content', ''))
            if transcript:
                f.write(f"## Transcript\n\n{transcript}\n")
        
        return md_path
    
    def import_text_file(self, filepath):
        """Import plain text meeting notes"""
        content = Path(filepath).read_text(encoding='utf-8')
        filename = Path(filepath).stem
        
        # Try to extract title from first line
        lines = content.split('\n')
        title = lines[0].strip('#').strip() if lines else filename
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:50]
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        output_dir = self.knowledge_base / "manual"
        md_path = output_dir / f"{date_str}_{safe_title}.md"
        
        # Save with metadata header
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Date:** {date_str}\n")
            f.write(f"**Source:** Manual Import\n\n")
            f.write(content)
        
        return md_path
    
    def import_file(self, filepath):
        """Import a single file"""
        filepath = Path(filepath)
        
        try:
            if filepath.suffix.lower() == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                source = self.detect_source(data)
                
                if source == 'fireflies':
                    result = self.import_fireflies_json(filepath, data)
                    print(f"✓ Imported Fireflies meeting: {result.name}")
                elif source == 'tactiq':
                    result = self.import_tactiq_json(filepath, data)
                    print(f"✓ Imported Tactiq meeting: {result.name}")
                else:
                    # Try generic import
                    result = self.import_tactiq_json(filepath, data)
                    print(f"✓ Imported meeting (generic): {result.name}")
                
            elif filepath.suffix.lower() in ['.txt', '.md']:
                result = self.import_text_file(filepath)
                print(f"✓ Imported text meeting: {result.name}")
            
            else:
                print(f"✗ Unsupported file type: {filepath.suffix}")
                return False
            
            # Move to processed folder
            processed_path = self.processed_folder / filepath.name
            filepath.rename(processed_path)
            print(f"  → Moved to processed folder")
            
            return True
            
        except Exception as e:
            print(f"✗ Error importing {filepath.name}: {e}")
            return False
    
    def scan_and_import(self):
        """Scan import folder and import all files"""
        files = list(self.import_folder.glob('*'))
        files = [f for f in files if f.is_file() and f.suffix.lower() in ['.json', '.txt', '.md']]
        
        if not files:
            print(f"No files found in {self.import_folder}")
            print("\nTo import meetings:")
            print(f"1. Export meetings from Fireflies/Tactiq")
            print(f"2. Save them to: {self.import_folder}")
            print(f"3. Run this script again")
            return 0
        
        print(f"Found {len(files)} file(s) to import\n")
        
        success_count = 0
        for file in files:
            if self.import_file(file):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"Import complete: {success_count}/{len(files)} successful")
        print(f"{'='*60}")
        
        return success_count

if __name__ == "__main__":
    try:
        importer = ManualMeetingImporter()
        
        print("="*60)
        print("  Manual Meeting Import Tool")
        print("="*60)
        print(f"\nImport folder: {importer.import_folder}")
        print(f"Knowledge base: {importer.knowledge_base}")
        print()
        
        importer.scan_and_import()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
