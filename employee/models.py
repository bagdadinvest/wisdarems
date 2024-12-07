import os
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from tinymce.models import HTMLField
from dirtyfields import DirtyFieldsMixin
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Max


# Designation Options
designations_opt = (
    (_('Executive and Management'), (
        ('human_resources_manager', _('Human Resources Manager')),
        ('administrative_officer', _('Administrative Officer')),
        ('chief_marketing_officer', _('Chief Marketing Officer')),
    )),
    (_('Creative and Media'), (
        ('journalist', _('Journalist')),
        ('proofreader', _('Proofreader')),
        ('video_editor', _('Video Editor')),
        ('graphic_designer', _('Graphic Designer')),
        ('content_writer', _('Content Writer')),
        ('voiceover_artist', _('Voiceover Artist')),
    )),
    (_('Technical and IT'), (
        ('software_developer', _('Software Developer')),
        ('authentication_supervisor', _('Authentication Supervisor')),
    )),
    (_('Support and Coordination'), (
        ('executive_secretary', _('Executive Secretary')),
        ('logistics_coordinator', _('Logistics Coordinator')),
        ('project_coordinator', _('Project Coordinator')),
        ('executive_assistant', _('Executive Assistant')),
    )),
    (_('Compliance and Quality Assurance'), (
        ('internal_auditor', _('Internal Auditor')),
    )),
    (_('Maintenance and Facility'), (
        ('janitorial_staff', _('Janitorial Staff')),
    )),
)
flattened_designations = [
    (designation[0], designation[1])
    for category, designations in designations_opt
    for designation in designations
]

# Employee Model
class Employee(DirtyFieldsMixin, AbstractUser):
    job_number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='Job Number')
    name = models.CharField(max_length=255, verbose_name=_('Full Name'))
    nationality = CountryField(verbose_name=_('Nationality'))
    job_title = MultiSelectField(choices=flattened_designations, verbose_name=_('Job Title'))
    is_superadmin = models.BooleanField(default=False)
    department = models.CharField(blank=True, null=True, max_length=100, verbose_name=_('Department'))
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Enter a valid phone number."))],
        verbose_name=_('Phone Number')
    )
    start_date = models.DateField(blank=True, null=True, verbose_name=_('Start Date'))
    salary = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2, verbose_name=_('Salary'))
    bank_account = models.CharField(blank=True, null=True, max_length=50, verbose_name=_('Bank Account Number'))
    account_holder = models.CharField(blank=True, null=True, max_length=100, verbose_name=_('Account Holder'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Address'))
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_('Slug'))
    notes = HTMLField(blank=True, null=True, verbose_name=_('Notes'))

    def save(self, *args, **kwargs):
        if not self.job_number:
            current_month = timezone.now().strftime('%m')
            current_year = timezone.now().strftime('%Y')
            employee_count = Employee.objects.filter(job_number__startswith=f"{current_month}{current_year}").count() + 1
            self.job_number = f"{current_month}{current_year}-{employee_count:02d}"
        
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Employee.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# EmployeeFile Model
def employee_file_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.file_type}.{ext}" if instance.file_type else filename
    return f'employee/{instance.employee.job_number}/{filename}'


class EmployeeFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('cv', 'CV'),
        ('profile_picture', 'Profile Picture'),
        ('document', 'Document'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    file = models.FileField(upload_to=employee_file_upload_path)

    def clean(self):
        ext = os.path.splitext(self.file.name)[1].lower()
        valid_extensions = {
            'profile_picture': ['.jpg', '.jpeg', '.png'],
            'cv': ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'],
            'document': ['.pdf', '.jpg', '.jpeg', '.png', '.docx'],
        }
        if ext not in valid_extensions.get(self.file_type, []):
            raise ValidationError(_('Invalid file format for this type.'))

    def __str__(self):
        return f'{self.file_type} for {self.employee}'


# Request Model with Foreign Keys for all categories
class Request(models.Model):
    requestId = models.CharField(max_length=20, verbose_name=_('Request ID'), unique=True, blank=True, null=True)
    requesterId = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="requesterId", verbose_name=_('Requester'))
    requestMessage = models.TextField(verbose_name=_('Request Message'))
    requestDate = models.DateTimeField(default=timezone.now, verbose_name=_('Request Date'))
    destinationEmployeeId = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="toEmployeeId", verbose_name=_('Destination Employee'))

    # Foreign Keys to different request categories
    advance_payment = models.ForeignKey('AdvancePayment', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Advance Payment'))
    work_assignment = models.ForeignKey('WorkAssignment', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Work Assignment'))
    file_attachment = models.ForeignKey(EmployeeFile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('File Attachment'))

    def save(self, *args, **kwargs):
        if not self.requestId:
            today = timezone.now().strftime('%Y-%m-%d')
            base_request_id = f"{self.requesterId.job_number}-ADR{today}" if self.advance_payment else f"{self.requesterId.job_number}-WA{today}"
            existing_requests = Request.objects.filter(requestId__startswith=base_request_id)
            max_suffix = existing_requests.aggregate(Max('requestId'))['requestId__max']
            suffix_number = int(max_suffix.split('-')[-1]) + 1 if max_suffix else 1
            self.requestId = f"{base_request_id}-{suffix_number:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request by {self.requesterId.name} ({self.requestId})"


# AdvancePayment Model
class AdvancePayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))
    request_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Request Date'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    notes = HTMLField(blank=True, null=True, verbose_name=_('Notes'))

    def __str__(self):
        return f"Advance Payment of {self.amount} by {self.employee.name} - Status: {self.get_status_display()}"


# WorkAssignment Model
class WorkAssignment(models.Model):
    assignmentId = models.CharField(max_length=20, verbose_name=_('Assignment ID'))
    assignerId = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assignerId", verbose_name=_('Assigner'))
    work = models.TextField(verbose_name=_('Work Details'))
    assignDate = models.DateTimeField(verbose_name=_('Assign Date'))
    dueDate = models.DateTimeField(verbose_name=_('Due Date'))
    taskerId = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="taskerId", verbose_name=_('Tasker'))

    def __str__(self):
        return _("Assignment by %(assigner)s to %(tasker)s") % {'assigner': self.assignerId, 'tasker': self.taskerId}

###########################################################################################

class SuperadminAssignment(models.Model):
    """
    This model allows assigning specific superadmins to specific request types.
    """
    ADMIN_REQUEST_TYPES = [
        ('advance_payment', 'Advance Payment'),
        ('salary_details', 'Salary Details'),
        ('attendance', 'Attendance'),
        ('work_schedule', 'Work Schedule'),
    ]

    superadmin = models.ForeignKey(Employee, on_delete=models.CASCADE, limit_choices_to={'is_superadmin': True})
    request_type = models.CharField(max_length=50, choices=ADMIN_REQUEST_TYPES, unique=True)

    class Meta:
        verbose_name = "Superadmin Assignment"
        verbose_name_plural = "Superadmin Assignments"

    def __str__(self):
        return f"{self.request_type} handled by {self.superadmin}"


###########################################################################################
# Updated Attendance Model
class Attendance(models.Model):
    """
    Attendance model: Tracks attendance, overtime, and absences for employees.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))  # ForeignKey to Employee
    workdays = models.PositiveIntegerField(verbose_name=_('Workdays'))
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_('Overtime Hours'))
    absence_days = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Absence Days'))
    deductions = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Deductions'))

    def __str__(self):
        return f"Attendance for {self.employee.name}"


class WorkSchedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_schedules', verbose_name='Employee')

    def __str__(self):
        return f"Work Schedule for {self.employee}"

class DaySchedule(models.Model):
    WORK_TYPE_CHOICES = [
        ('office', 'Office'),
        ('remote', 'Remote'),
    ]

    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.CASCADE, related_name='schedules')  # ForeignKey to WorkSchedule
    day_of_week = models.CharField(max_length=9, choices=[
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ])
    active = models.BooleanField(default=False)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    work_type = models.CharField(max_length=6, choices=WORK_TYPE_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = ('work_schedule', 'day_of_week')  # Enforce unique day for each schedule
        # Or using Django 2.2+ UniqueConstraint
        # constraints = [
        #     models.UniqueConstraint(fields=['work_schedule', 'day_of_week'], name='unique_day_per_schedule')
        # ]

    def __str__(self):
        return f"{self.day_of_week}: {'Active' if self.active else 'Off'}"


    # SalaryDetails Model
class SalaryDetails(models.Model):
    """
    SalaryDetails model: Stores salary information like bonuses and deductions.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))  # ForeignKey to Employee
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Base Salary'))
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Bonuses'))
    deductions = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Deductions'))
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_('Overtime Hours'))
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Overtime Pay'))
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Salary'))

    def __stsr__(self):
        return f"Salary details for {self.employee.name}"



# Notice Model
class Notice(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))  # ForeignKey to Employee
    noticeId = models.CharField(primary_key=True, max_length=20, verbose_name=_('Notice ID'))
    title = models.CharField(max_length=250, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    publishDate = models.DateTimeField(verbose_name=_('Publish Date'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Notice')
        verbose_name_plural = _('Notices')

