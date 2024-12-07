from django.db import models

class Command(models.Model):
    name = models.CharField(max_length=100)  # Command name (e.g., 'show_urls')
    definition = models.TextField()  # A description of what the command does
    usage = models.CharField(max_length=255)  # Example usage (e.g., 'python manage.py show_urls')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
