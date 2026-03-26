"""Google Calendar integration for OpenClaw.
Auto-accept invites, create events, list upcoming meetings.
"""
import os
import json
from datetime import datetime, timedelta

from google_auth import get_google_credentials
from googleapiclient.discovery import build


def get_calendar_service():
    """Build and return a Google Calendar API service."""
    creds = get_google_credentials()
    return build('calendar', 'v3', credentials=creds)


def get_upcoming_events(days_ahead=7, max_results=10):
    """Get upcoming calendar events.
    
    Args:
        days_ahead: Number of days to look ahead
        max_results: Maximum number of events to return
    
    Returns:
        List of event dictionaries
    """
    service = get_calendar_service()
    
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    result = []
    for event in events:
        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
        end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
        
        result.append({
            'id': event['id'],
            'summary': event.get('summary', 'No title'),
            'start': start,
            'end': end,
            'location': event.get('location', ''),
            'description': event.get('description', ''),
            'attendees': event.get('attendees', []),
            'status': event.get('status', '')
        })
    
    return result


def get_pending_invites(days_ahead=30):
    """Get calendar events where the user hasn't responded (needsAction).
    
    Args:
        days_ahead: Number of days to look ahead
    
    Returns:
        List of pending event dictionaries
    """
    service = get_calendar_service()
    
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime',
        maxResults=50
    ).execute()
    
    events = events_result.get('items', [])
    pending = []
    
    for event in events:
        attendees = event.get('attendees', [])
        for attendee in attendees:
            if attendee.get('self', False) and attendee.get('responseStatus') == 'needsAction':
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                pending.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'organizer': event.get('organizer', {}).get('email', 'Unknown')
                })
                break
    
    return pending


def accept_invite(event_id):
    """Accept a calendar invite.
    
    Args:
        event_id: The calendar event ID
    
    Returns:
        True if successful, False otherwise
    """
    service = get_calendar_service()
    
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        attendees = event.get('attendees', [])
        
        for attendee in attendees:
            if attendee.get('self', False):
                attendee['responseStatus'] = 'accepted'
        
        updated = service.events().patch(
            calendarId='primary',
            eventId=event_id,
            body={'attendees': attendees},
            sendUpdates='all'
        ).execute()
        
        return True
    except Exception as e:
        print(f"Failed to accept event: {e}")
        return False


def accept_all_pending():
    """Auto-accept all pending calendar invites.
    
    Returns:
        Number of invites accepted
    """
    pending = get_pending_invites()
    accepted_count = 0
    
    for event in pending:
        if accept_invite(event['id']):
            print(f"✓ Accepted: {event['summary']}")
            accepted_count += 1
        else:
            print(f"✗ Failed: {event['summary']}")
    
    return accepted_count


def create_event(summary, start_time, end_time, description='', location='', attendees=None):
    """Create a new calendar event.
    
    Args:
        summary: Event title
        start_time: Start datetime (ISO format or datetime object)
        end_time: End datetime (ISO format or datetime object)
        description: Event description
        location: Event location
        attendees: List of attendee email addresses
    
    Returns:
        Created event object
    """
    service = get_calendar_service()
    
    # Convert datetime to ISO format if needed
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()
    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()
    
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Tokyo',
        }
    }
    
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    created = service.events().insert(calendarId='primary', body=event).execute()
    return created


def delete_event(event_id):
    """Delete a calendar event.
    
    Args:
        event_id: The calendar event ID
    
    Returns:
        True if successful, False otherwise
    """
    service = get_calendar_service()
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"Failed to delete event: {e}")
        return False


if __name__ == '__main__':
    print("=== Upcoming Events (Next 7 days) ===")
    events = get_upcoming_events(days_ahead=7)
    
    if not events:
        print("No upcoming events.")
    else:
        for event in events:
            print(f"\n📅 {event['summary']}")
            print(f"   Start: {event['start']}")
            if event['location']:
                print(f"   Location: {event['location']}")
    
    print("\n\n=== Pending Invites ===")
    pending = get_pending_invites()
    
    if not pending:
        print("No pending invites.")
    else:
        for event in pending:
            print(f"\n⏳ {event['summary']}")
            print(f"   Start: {event['start']}")
            print(f"   From: {event['organizer']}")
        
        # Ask to auto-accept
        response = input("\nAuto-accept all pending invites? (y/n): ")
        if response.lower() == 'y':
            count = accept_all_pending()
            print(f"\n✓ Accepted {count} invite(s)")
