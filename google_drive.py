"""Google Drive and Sheets integration for OpenClaw.
Access files, read/write spreadsheets, manage documents.
"""
import os
import io
from datetime import datetime

from google_auth import get_google_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


def get_drive_service():
    """Build and return a Google Drive API service."""
    creds = get_google_credentials()
    return build('drive', 'v3', credentials=creds)


def get_sheets_service():
    """Build and return a Google Sheets API service."""
    creds = get_google_credentials()
    return build('sheets', 'v4', credentials=creds)


def list_files(query='', max_results=20):
    """List files in Google Drive.
    
    Args:
        query: Drive query (e.g., "name contains 'report'")
        max_results: Maximum number of results
    
    Returns:
        List of file dictionaries
    """
    service = get_drive_service()
    
    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields="files(id, name, mimeType, createdTime, modifiedTime, size, webViewLink)"
    ).execute()
    
    return results.get('files', [])


def search_files(name_contains='', file_type=None):
    """Search for files in Drive.
    
    Args:
        name_contains: Search for files containing this in the name
        file_type: Filter by mime type (e.g., 'spreadsheet', 'document', 'folder')
    
    Returns:
        List of matching files
    """
    query_parts = []
    
    if name_contains:
        query_parts.append(f"name contains '{name_contains}'")
    
    if file_type:
        type_map = {
            'spreadsheet': 'application/vnd.google-apps.spreadsheet',
            'document': 'application/vnd.google-apps.document',
            'folder': 'application/vnd.google-apps.folder',
            'pdf': 'application/pdf',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        mime_type = type_map.get(file_type, file_type)
        query_parts.append(f"mimeType='{mime_type}'")
    
    query = ' and '.join(query_parts) if query_parts else ''
    
    return list_files(query=query)


def download_file(file_id, destination_path):
    """Download a file from Google Drive.
    
    Args:
        file_id: The file ID in Drive
        destination_path: Local path to save the file
    
    Returns:
        True if successful
    """
    service = get_drive_service()
    
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")
        
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def upload_file(file_path, parent_folder_id=None):
    """Upload a file to Google Drive.
    
    Args:
        file_path: Local file path to upload
        parent_folder_id: Optional folder ID to upload into
    
    Returns:
        Uploaded file object
    """
    service = get_drive_service()
    
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()
    
    return file


def read_spreadsheet(spreadsheet_id, range_name='Sheet1!A1:Z1000'):
    """Read data from a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The spreadsheet ID
        range_name: Range to read (e.g., 'Sheet1!A1:D10')
    
    Returns:
        List of rows (each row is a list of values)
    """
    service = get_sheets_service()
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    return result.get('values', [])


def write_spreadsheet(spreadsheet_id, range_name, values):
    """Write data to a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The spreadsheet ID
        range_name: Range to write (e.g., 'Sheet1!A1')
        values: List of rows (each row is a list of values)
    
    Returns:
        Update response
    """
    service = get_sheets_service()
    
    body = {
        'values': values
    }
    
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    return result


def append_to_spreadsheet(spreadsheet_id, range_name, values):
    """Append data to a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The spreadsheet ID
        range_name: Range to append to (e.g., 'Sheet1!A:D')
        values: List of rows to append
    
    Returns:
        Append response
    """
    service = get_sheets_service()
    
    body = {
        'values': values
    }
    
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    
    return result


def create_spreadsheet(title, sheet_names=None):
    """Create a new Google Spreadsheet.
    
    Args:
        title: Spreadsheet title
        sheet_names: List of sheet names (default: ['Sheet1'])
    
    Returns:
        Created spreadsheet object with id and url
    """
    service = get_sheets_service()
    
    if sheet_names is None:
        sheet_names = ['Sheet1']
    
    spreadsheet = {
        'properties': {
            'title': title
        },
        'sheets': [{'properties': {'title': name}} for name in sheet_names]
    }
    
    result = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
    
    return {
        'id': result.get('spreadsheetId'),
        'url': result.get('spreadsheetUrl')
    }


if __name__ == '__main__':
    print("=== Recent Files ===")
    files = list_files(max_results=10)
    
    for file in files:
        print(f"\n📄 {file['name']}")
        print(f"   Type: {file['mimeType']}")
        print(f"   Modified: {file.get('modifiedTime', 'Unknown')}")
        if file.get('webViewLink'):
            print(f"   Link: {file['webViewLink']}")
    
    print("\n\n=== Spreadsheets ===")
    sheets = search_files(file_type='spreadsheet')
    
    for sheet in sheets[:5]:
        print(f"\n📊 {sheet['name']}")
        print(f"   ID: {sheet['id']}")
        if sheet.get('webViewLink'):
            print(f"   Link: {sheet['webViewLink']}")
