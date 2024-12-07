import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_http_methods
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io
from .converters.text import HeadingBlockConverter, ParagraphBlockConverter
from .converters.images import ImageBlockConverter
from .converters.videos import VideoBlockConverter

# Set up logging
logger = logging.getLogger(__name__)

# Import converters for handling different types of content (assuming these are defined elsewhere)

########################################################################

def get_google_drive_service():
    """Authenticate using the service account and return Google Drive service."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE, 
            scopes=settings.GOOGLE_API_SCOPES  # Make sure the required scopes are defined
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        logger.error(f"Error loading service account: {str(e)}")
        raise
########################################################################

def google_drive_picker(request):
    """View to select a file from Google Drive based on file type."""
    try:
        logger.debug("Starting Google Drive file picker view...")

        drive_service = get_google_drive_service()

        # Get the filter from URL parameters (default is 'docs')
        file_type = request.GET.get('file_type', 'docs')
        logger.debug(f"Requested file type: {file_type}")

        # Modify the query based on the file type requested
        if file_type == 'docs':
            query = "mimeType='application/vnd.google-apps.document'"
        elif file_type == 'images':
            query = "mimeType contains 'image/'"
        elif file_type == 'videos':
            query = "mimeType contains 'video/'"
        else:
            query = ""  # Fetch all files if no filter is provided

        logger.debug(f"Google Drive query: {query}")

        # Query Google Drive for files
        results = drive_service.files().list(
            q=query,  # Apply the query for the file type
            pageSize=10,  # Limit the results to 10 files
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()

        # Get the files
        files = results.get('files', [])
        logger.debug(f"Received {len(files)} files from Google Drive.")

        # Return the rendered template with the files and file type
        return render(request, 'googledrive/google_drive_picker.html', {
            'files': files,
            'file_type': file_type
        })

    except Exception as e:
        logger.error(f"Error fetching files from Google Drive: {str(e)}")
        return HttpResponse("Error fetching files.", status=500)

########################################################################

def convert_content_to_blocks(parsed_content, user):
    """Converts parsed content into blocks."""
    logger.debug("Starting content conversion to blocks...")

    # List to store the converted blocks
    converted_blocks = []

    # Iterate over parsed content and apply the appropriate converter
    for element in parsed_content:
        logger.debug(f"Processing element: {element['type']}")

        if element['type'] == 'heading':
            converted_blocks.append(HeadingBlockConverter()(element))
        elif element['type'] == 'paragraph':
            converted_blocks.append(ParagraphBlockConverter()(element))
        elif element['type'] == 'image':
            converted_blocks.append(ImageBlockConverter()(element, user))
        elif element['type'] == 'video':
            converted_blocks.append(VideoBlockConverter()(element))
    
    logger.debug("Content conversion complete.")
    return converted_blocks

########################################################################

import logging
from googleapiclient.http import MediaIoBaseDownload
from django.http import HttpResponse
import io

logger = logging.getLogger(__name__)

def download_google_drive_file(request, file_id):
    """Downloads a file from Google Drive using the Service Account credentials."""
    try:
        logger.debug(f"Starting download for file ID: {file_id}")

        # Authenticate using the Service Account (use the same service as in google_drive_picker)
        drive_service = get_google_drive_service()
        logger.debug("Google Drive service initialized successfully with service account credentials.")

        # Get the file metadata to check its MIME type
        file_metadata = drive_service.files().get(fileId=file_id, fields='name, mimeType').execute()
        mime_type = file_metadata['mimeType']
        file_name = file_metadata['name']
        logger.debug(f"File metadata: {file_metadata}")

        # If the file is a Google Docs Editors file (Docs, Sheets, Slides), export it to a specific format
        if mime_type.startswith('application/vnd.google-apps.'):
            if mime_type == 'application/vnd.google-apps.document':
                export_mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # Export to DOCX
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                export_mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # Export to XLSX
            elif mime_type == 'application/vnd.google-apps.presentation':
                export_mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'  # Export to PPTX
            else:
                return HttpResponse("Unsupported Google Docs Editors file type for export.", status=400)

            logger.debug(f"Exporting Google Docs Editors file with MIME type: {export_mime_type}")

            # Export the file
            request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime_type)
        else:
            # If it's a binary file (like an image, PDF, etc.), download it as usual
            logger.debug(f"Requesting media for file ID: {file_id}")
            request = drive_service.files().get_media(fileId=file_id)

        # Download the file in chunks
        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False

        logger.debug(f"Downloading file with ID: {file_id} in chunks.")
        while not done:
            status, done = downloader.next_chunk()
            logger.debug(f"Download progress for file {file_id}: {status.progress() * 100}%")

        # Ensure the file is at the start before sending it in the response
        file_data.seek(0)

        # Determine content type for the response based on the file type
        content_type = export_mime_type if mime_type.startswith('application/vnd.google-apps.') else 'application/octet-stream'
        response = HttpResponse(file_data.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'

        logger.debug(f"File {file_id} downloaded successfully.")
        return response

    except Exception as e:
        logger.error(f"Error downloading file from Google Drive: {str(e)}", exc_info=True)
        return HttpResponse(f"An error occurred while downloading the file: {str(e)}", status=500)
