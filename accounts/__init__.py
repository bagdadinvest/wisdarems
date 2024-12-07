from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.shortcuts import render
from wagtail.admin import messages
from django.conf import settings

# Function to authenticate using the service account and access Google Drive
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=settings.GOOGLE_API_SCOPES)
    
    # Build the Google Drive service
    service = build('drive', 'v3', credentials=credentials)
    return service

# View to list files from Google Drive
def list_google_drive_files(request):
    drive_service = get_drive_service()
    
    try:
        # List first 10 files from Google Drive
        results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
    except Exception as e:
        messages.error(request, f"Error accessing Google Drive: {e}")
        items = []

    # Render the files in the Wagtail admin template
    return render(request, 'admin/google_drive_files.html', {'files': items})
