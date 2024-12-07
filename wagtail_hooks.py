from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from .models import Employee, EmployeeFile, Request, AdvancePayment, WorkAssignment, Notice

@register_snippet
class EmployeeSnippetViewSet(SnippetViewSet):
    model = Employee
    list_display = ('name', 'job_number', 'email', 'department')
    search_fields = ('name', 'email', 'job_number', 'department')
    list_filter = ('department', 'job_title', 'start_date')
    ordering = ['name', 'job_number']

    # Inline editing for related EmployeeFile objects
    panels = [
        FieldPanel('name'),
        FieldPanel('job_number'),
        FieldPanel('email'),
        FieldPanel('department'),
        FieldPanel('phone_number'),
        FieldPanel('address'),
        FieldPanel('start_date'),
        InlinePanel('files', label='Files'),  # Inline related EmployeeFile objects
    ]

@register_snippet
class EmployeeFileSnippetViewSet(SnippetViewSet):
    model = EmployeeFile
    list_display = ('employee', 'file_type', 'file')

@register_snippet
class RequestSnippetViewSet(SnippetViewSet):
    model = Request
    list_display = ('requestId', 'requesterId', 'requestMessage', 'requestDate', 'destinationEmployeeId')
    search_fields = ('requestId', 'requesterId__name', 'destinationEmployeeId__name')
    list_filter = ('requestDate', 'destinationEmployeeId')
    ordering = ['-requestDate']

    panels = [
        FieldPanel('requestId'),
        FieldPanel('requesterId'),
        FieldPanel('requestMessage'),
        FieldPanel('requestDate'),
        FieldPanel('destinationEmployeeId'),
        FieldPanel('advance_payment'),
        FieldPanel('work_assignment'),
        FieldPanel('file_attachment'),
    ]

@register_snippet
class AdvancePaymentSnippetViewSet(SnippetViewSet):
    model = AdvancePayment
    list_display = ('employee', 'amount', 'status')

@register_snippet
class WorkAssignmentSnippetViewSet(SnippetViewSet):
    model = WorkAssignment
    list_display = ('assignmentId', 'assignerId', 'taskerId', 'assignDate')

@register_snippet
class NoticeSnippetViewSet(SnippetViewSet):
    model = Notice
    list_display = ('title', 'publishDate')
    