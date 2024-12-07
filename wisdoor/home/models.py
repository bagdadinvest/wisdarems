# models.py
import os
from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtailmarkdown.fields import MarkdownField
from wagtailmedia.edit_handlers import MediaChooserPanel
from wagtail_color_panel.fields import ColorField
from wagtail import blocks
from wagtailcodeblock.blocks import CodeBlock
from employee.models import Employee  # Import Employee model


class TaskPage(Page):
    """A page for employees to submit tasks"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="tasks", verbose_name=_('Employee'))
    employee_name = models.CharField(max_length=255)
    task_description = MarkdownField()  # Markdown support for task description
    task_media = models.ForeignKey(
        'wagtailmedia.Media',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    task_color = ColorField(default='#FF0000')  # Optional: categorize tasks by color
    task_content = StreamField([
        ('code', CodeBlock(label="Code")),
    ], blank=True)

    # Panels to show in the Wagtail admin interface
    content_panels = Page.content_panels + [
        FieldPanel('employee'),
        FieldPanel('employee_name'),
        FieldPanel('task_description'),
        MediaChooserPanel('task_media'),
        FieldPanel('task_color'),
        FieldPanel('task_content'),
    ]

    def __str__(self):
        return f"Task: {self.title} by {self.employee.name}"
