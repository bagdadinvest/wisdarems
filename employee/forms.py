from django import forms
from .models import (
    Employee, WorkAssignment, Request, WorkSchedule, DaySchedule,
    EmployeeFile, AdvancePayment, Attendance, SalaryDetails, WorkAssignment
)
from django.utils.timezone import now
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


# Form for WorkAssignment
class WorkForm(forms.ModelForm):
    class Meta:
        model = WorkAssignment
        widgets = {
            "assignDate": forms.DateInput(attrs={'type': 'datetime-local'}),
            "dueDate": forms.DateInput(attrs={'type': 'datetime-local'}),
        }
        labels = {"assignerId": "Select Your ID"}
        fields = [
            "assignerId",
            "work",
            "assignDate",
            "dueDate",
            "taskerId",
        ]


    def __init__(self, *args, **kwargs):
        # Automatically set request date to the current time
        super(MakeRequestForm, self).__init__(*args, **kwargs)
        self.fields['requestDate'].initial = now()

        # Dynamically adjust the destination based on request type (e.g., work assignment)
        if not self.instance.work_assignment:
            self.fields['destinationEmployeeId'].widget.attrs['readonly'] = True  # Auto-assign for non-work requests


# Form for managing individual day schedules
class DayScheduleForm(forms.ModelForm):
    class Meta:
        model = DaySchedule
        fields = ['day_of_week', 'active', 'start_time', 'end_time', 'work_type']


# WorkSchedule form doesn't need individual days anymore
class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = ['employee']  # Only the employee field


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone_number', 'nationality', 'address', 'bank_account', 'account_holder', 'notes']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                Column('nationality', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('address', css_class='form-group col-md-6 mb-0'),
                Column('bank_account', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('account_holder', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-0'),
            ),
        )

# Employee File Upload Form
class EmployeeFileUploadForm(forms.ModelForm):
    class Meta:
        model = EmployeeFile
        fields = ['file_type', 'file']
        widgets = {
            'file_type': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control form-control-lg'}),
        }
        
        
#####################################################################################


# forms.py
from django import forms

class RequestTypeForm(forms.Form):
    REQUEST_CHOICES = [
        ('administrative', 'Administrative Request'),
        ('work_assignment', 'Work Assignment'),
    ]
    request_type = forms.ChoiceField(choices=REQUEST_CHOICES, widget=forms.RadioSelect)

class AdminRequestForm(forms.Form):
    ADMIN_CHOICES = [
        ('advance_payment', 'Advance Payment'),
        ('salary_details', 'Salary Details'),
        ('attendance', 'Attendance'),
    ]
    admin_request_type = forms.ChoiceField(choices=ADMIN_CHOICES)

class WorkAssignmentForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=Employee.objects.all())

class RequestDetailsForm(forms.Form):
    request_message = forms.CharField(widget=forms.Textarea)
    request_file = forms.FileField(required=False)

            

#####################################################################################

class MakeRequestForm(forms.ModelForm):
    advance_payment = forms.ModelChoiceField(
        queryset=AdvancePayment.objects.all(),
        required=False,
        label="Advance Payment Request",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    work_schedule = forms.ModelChoiceField(
        queryset=WorkSchedule.objects.all(),
        required=False,
        label="Work Schedule Change",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    day_schedule = forms.ModelChoiceField(
        queryset=DaySchedule.objects.all(),
        required=False,
        label="Day Schedule Change",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    salary_details = forms.ModelChoiceField(
        queryset=SalaryDetails.objects.all(),
        required=False,
        label="Salary Details Request",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    attendance = forms.ModelChoiceField(
        queryset=Attendance.objects.all(),
        required=False,
        label="Attendance Request",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    work_assignment = forms.ModelChoiceField(
        queryset=WorkAssignment.objects.all(),
        required=False,
        label="Work Assignment Request",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    file_attachment = forms.ModelChoiceField(
        queryset=EmployeeFile.objects.all(),
        required=False,
        label="Attach File",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Request
        widgets = {
            "requestDate": forms.DateInput(attrs={'type': 'datetime-local'}),
        }
        labels = {"requesterId": "Select Your ID"}
        fields = [
            "requestMessage",
            "requestDate",
            "destinationEmployeeId",
            "advance_payment",
            "work_schedule",
            "day_schedule",
            "salary_details",
            "attendance",
            "work_assignment",
            "file_attachment",
        ]

#################################################################################################

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Employee, Request

class UnifiedRequestForm(forms.Form):
    REQUEST_TYPES = [
        ('administrative', 'Administrative Request'),
        ('work_assignment', 'Work Assignment'),
    ]

    request_type = forms.ChoiceField(choices=REQUEST_TYPES, label='Request Type')
    request_message = forms.CharField(widget=forms.Textarea, label='Request Message')
    recipient_id = forms.ModelChoiceField(
        queryset=Employee.objects.all(), required=False, label="Assign Work To"
    )
    admin_request_type = forms.CharField(required=False, label='Administrative Request Type')

    def __init__(self, *args, **kwargs):
        employee_queryset = kwargs.pop('employee_queryset', None)
        super(UnifiedRequestForm, self).__init__(*args, **kwargs)
        if employee_queryset:
            self.fields['recipient_id'].queryset = employee_queryset

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('request_type', css_class='form-group col-md-6 mb-0'),
                Column('recipient_id', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'request_message',
            'admin_request_type',
            Submit('submit', 'Submit')
        )

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get("request_type")

        if request_type == "administrative" and not cleaned_data.get("admin_request_type"):
            self.add_error('admin_request_type', 'This field is required for administrative requests.')

        if request_type == "work_assignment" and not cleaned_data.get("recipient_id"):
            self.add_error('recipient_id', 'You must select a recipient for work assignments.')

        return cleaned_data
