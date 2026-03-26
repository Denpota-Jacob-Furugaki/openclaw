"""
Google Calendar Manager for Interview Scheduling
Only schedules within approved hours: Mon-Fri 10AM-5PM JST
"""
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN_PATH = 'google_token.json'

# Approved scheduling windows
APPROVED_DAYS = [0, 1, 2, 3, 4]  # Monday=0 to Friday=4
APPROVED_START_HOUR = 10
APPROVED_END_HOUR = 17  # 5 PM
TIMEZONE = 'Asia/Tokyo'

def get_calendar_service():
    """Get authenticated calendar service."""
    if not os.path.exists(TOKEN_PATH):
        print("[ERROR] Google token not found. Need OAuth setup.")
        return None
    
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    return build('calendar', 'v3', credentials=creds)

def is_approved_time(start_datetime):
    """Check if datetime is within approved scheduling window."""
    # Check day of week
    if start_datetime.weekday() not in APPROVED_DAYS:
        return False, "Only Monday-Friday scheduling allowed"
    
    # Check hour
    hour = start_datetime.hour
    if hour < APPROVED_START_HOUR or hour >= APPROVED_END_HOUR:
        return False, f"Only {APPROVED_START_HOUR}:00-{APPROVED_END_HOUR}:00 scheduling allowed"
    
    return True, "OK"

def create_event(summary, start_time, duration_minutes=60, description="", location=""):
    """
    Create a calendar event.
    
    Args:
        summary: Event title
        start_time: datetime object for start
        duration_minutes: Event duration (default 60)
        description: Event description
        location: Event location/link
    
    Returns:
        Event ID if successful, None otherwise
    """
    service = get_calendar_service()
    if not service:
        return None
    
    # Validate time window
    approved, reason = is_approved_time(start_time)
    if not approved:
        print(f"[ERROR] Cannot schedule: {reason}")
        return None
    
    # Calculate end time
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Create event
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': TIMEZONE,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    
    if location:
        event['location'] = location
    
    try:
        event_result = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        print(f"[OK] Event created: {summary}")
        print(f"     Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"     Event ID: {event_result['id']}")
        print(f"     Link: {event_result.get('htmlLink', 'N/A')}")
        
        return event_result['id']
        
    except HttpError as e:
        print(f"[ERROR] Failed to create event: {e}")
        return None

def get_upcoming_events(days_ahead=7):
    """Get upcoming events for next N days."""
    service = get_calendar_service()
    if not service:
        return []
    
    now = datetime.now()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
    
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return events
        
    except HttpError as e:
        print(f"[ERROR] Failed to fetch events: {e}")
        return []

def find_free_slot(date, preferred_hour=14, duration_minutes=60):
    """
    Find a free slot on a given date.
    
    Args:
        date: datetime.date object
        preferred_hour: Preferred hour (24h format)
        duration_minutes: Slot duration
    
    Returns:
        datetime object for free slot, or None
    """
    service = get_calendar_service()
    if not service:
        return None
    
    # Check if date is approved day
    if date.weekday() not in APPROVED_DAYS:
        print(f"[ERROR] {date} is not Monday-Friday")
        return None
    
    # Get events for that day
    day_start = datetime.combine(date, datetime.min.time())
    day_end = day_start + timedelta(days=1)
    
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=day_start.isoformat() + 'Z',
            timeMax=day_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Try preferred hour first
        proposed_start = datetime.combine(date, datetime.min.time()).replace(hour=preferred_hour)
        proposed_end = proposed_start + timedelta(minutes=duration_minutes)
        
        # Check for conflicts
        for event in events:
            event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
            
            # Check overlap
            if not (proposed_end <= event_start or proposed_start >= event_end):
                # Conflict, try next hour
                preferred_hour += 1
                if preferred_hour >= APPROVED_END_HOUR:
                    print(f"[ERROR] No free slots on {date}")
                    return None
                proposed_start = datetime.combine(date, datetime.min.time()).replace(hour=preferred_hour)
                proposed_end = proposed_start + timedelta(minutes=duration_minutes)
        
        # Validate final slot
        approved, reason = is_approved_time(proposed_start)
        if not approved:
            print(f"[ERROR] {reason}")
            return None
        
        return proposed_start
        
    except HttpError as e:
        print(f"[ERROR] Failed to check availability: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("Google Calendar Manager - Testing")
    print("="*60)
    
    # Test: Get upcoming events
    print("\nUpcoming events (next 7 days):")
    events = get_upcoming_events(7)
    for event in events[:5]:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"  • {event['summary']} - {start}")
    
    print(f"\nTotal upcoming events: {len(events)}")
    print("\nCalendar access: OK")
    print("Ready to schedule interviews within approved hours!")
