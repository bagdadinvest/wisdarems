# Standard library imports
import os

# Django imports
from django.contrib import admin

# Third-party imports
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Local imports
from .models import Command

# Define a resource for import/export functionality for the Command model
class CommandResource(resources.ModelResource):
    class Meta:
        model = Command
        fields = ('id', 'name', 'definition', 'usage', 'created_at')  # Specify the fields for import/export

# Register the Command model with the admin using ImportExportModelAdmin
@admin.register(Command)
class CommandAdmin(ImportExportModelAdmin):
    resource_class = CommandResource
    list_display = ('name', 'definition', 'usage', 'created_at')  # Fields to display in the admin list view
    search_fields = ('name', 'definition', 'usage')  # Enable search functionality

