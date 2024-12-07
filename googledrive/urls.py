from django.urls import path
from . import views
from django.conf import settings


app_name = 'gsuite'


urlpatterns = [
    # URL for the Google Drive file picker
    path('drive/', views.google_drive_picker, name='drive'),

    # URL for downloading a specific file from Google Drive
    path('drive/download/<str:file_id>/', views.download_google_drive_file, name='download_google_drive_file'),
]
