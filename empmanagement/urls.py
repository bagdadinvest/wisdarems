from django.contrib import admin
from django.urls import include, path  # Use path for modern Django routing
from django.conf.urls.static import static
from django.conf import settings

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from wagtail_content_import import urls as wagtail_content_import_urls

# Define your URL patterns
urlpatterns = [
    path('gsuite/', include('googledrive.urls')),  # Include the googledrive app URLs
    path('cms/', include(wagtail_content_import_urls)),  # Add the content import URL patterns

    # Django Admin URL
    path('django-admin/', admin.site.urls),

    # Google Docs list view (custom view)

    # Wagtail Admin interface URLs
    path('admin/', include(wagtailadmin_urls)),

    # Wagtail Documents serving URLs
    path('documents/', include(wagtaildocs_urls)),

    # Your custom app URLs (Accounts)
    path('', include('accounts.urls')),

    # Your Employee management app URLs
    path('ems/', include('employee.urls')),

    # Silk profiling tool URLs (only include if you have this installed)
    path('silk/', include('silk.urls', namespace='silk')),

    # Metrics URLs (if using a custom metrics app)
    path('metrics/', include('metrics.urls')),
]

# Add static files URL handling
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Include Django Debug Toolbar if in DEBUG mode
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
