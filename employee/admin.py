from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Employee, EmployeeFile, WorkAssignment, Request, AdvancePayment, 
    SuperadminAssignment, Attendance, WorkSchedule, DaySchedule, 
    SalaryDetails, Notice
)

# Resource classes for import/export functionality
class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee

class EmployeeFileResource(resources.ModelResource):
    class Meta:
        model = EmployeeFile

class WorkAssignmentResource(resources.ModelResource):
    class Meta:
        model = WorkAssignment

class RequestResource(resources.ModelResource):
    class Meta:
        model = Request

class AdvancePaymentResource(resources.ModelResource):
    class Meta:
        model = AdvancePayment

class SuperadminAssignmentResource(resources.ModelResource):
    class Meta:
        model = SuperadminAssignment

class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance

class WorkScheduleResource(resources.ModelResource):
    class Meta:
        model = WorkSchedule

class DayScheduleResource(resources.ModelResource):
    class Meta:
        model = DaySchedule

class SalaryDetailsResource(resources.ModelResource):
    class Meta:
        model = SalaryDetails

class NoticeResource(resources.ModelResource):
    class Meta:
        model = Notice


# Admin for Employee with import/export functionality
@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = ['name', 'job_number', 'email', 'nationality', 'department']
    search_fields = ('name', 'job_number', 'email', 'nationality')


# Admin for EmployeeFile with import/export functionality
@admin.register(EmployeeFile)
class EmployeeFileAdmin(ImportExportModelAdmin):
    resource_class = EmployeeFileResource
    list_display = ['employee', 'file_type', 'get_file_name']
    search_fields = ('employee__name', 'file_type')
    list_filter = ('file_type',)

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name)
    get_file_name.short_description = 'File Name'


# Admin for WorkAssignment with import/export functionality
@admin.register(WorkAssignment)
class WorkAssignmentAdmin(ImportExportModelAdmin):
    resource_class = WorkAssignmentResource
    list_display = ('assignmentId', 'assignerId', 'taskerId', 'assignDate', 'dueDate')
    search_fields = ('assignerId__name', 'taskerId__name')


# Admin for Request with import/export functionality
@admin.register(Request)
class RequestAdmin(ImportExportModelAdmin):
    resource_class = RequestResource
    list_display = (
        'requestId', 'requesterId', 'destinationEmployeeId', 'requestMessage',
        'requestDate', 'advance_payment', 'work_assignment', 'file_attachment'
    )
    search_fields = ('requesterId__name', 'destinationEmployeeId__name', 'requestMessage')
    list_filter = ('requestDate', 'destinationEmployeeId')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.work_assignment is None:
            readonly_fields += ('destinationEmployeeId',)
        return readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'requesterId', 'destinationEmployeeId', 'advance_payment', 'work_assignment', 'file_attachment'
        )


# Admin for AdvancePayment with import/export functionality
@admin.register(AdvancePayment)
class AdvancePaymentAdmin(ImportExportModelAdmin):
    resource_class = AdvancePaymentResource
    list_display = ('employee', 'request_date', 'amount', 'status')
    search_fields = ('employee__name',)


# Admin for SuperadminAssignment with import/export functionality
@admin.register(SuperadminAssignment)
class SuperadminAssignmentAdmin(ImportExportModelAdmin):
    resource_class = SuperadminAssignmentResource
    list_display = ('superadmin', 'request_type')
    search_fields = ('superadmin__name', 'request_type')


# Admin for Attendance with import/export functionality
@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin):
    resource_class = AttendanceResource
    list_display = ('employee', 'workdays', 'overtime_hours', 'absence_days', 'deductions')
    search_fields = ('employee__name',)


# Admin for WorkSchedule with import/export functionality
@admin.register(WorkSchedule)
class WorkScheduleAdmin(ImportExportModelAdmin):
    resource_class = WorkScheduleResource
    list_display = ('employee',)
    search_fields = ('employee__name',)


# Admin for DaySchedule with import/export functionality
@admin.register(DaySchedule)
class DayScheduleAdmin(ImportExportModelAdmin):
    resource_class = DayScheduleResource
    list_display = ('work_schedule', 'day_of_week', 'active', 'start_time', 'end_time', 'work_type')
    search_fields = ('work_schedule__employee__name', 'day_of_week')


# Admin for SalaryDetails with import/export functionality
@admin.register(SalaryDetails)
class SalaryDetailsAdmin(ImportExportModelAdmin):
    resource_class = SalaryDetailsResource
    list_display = ('employee', 'base_salary', 'bonuses', 'deductions', 'overtime_hours', 'total_salary')
    search_fields = ('employee__name',)


# Admin for Notice with import/export functionality
@admin.register(Notice)
class NoticeAdmin(ImportExportModelAdmin):
    resource_class = NoticeResource
    list_display = ('employee', 'title', 'noticeId', 'publishDate')
    search_fields = ('employee__name', 'title')
