from django import forms
from .models import Request, AdvancePayment, WorkAssignment, Employee, SuperadminAssignment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Step 1: Form for selecting the type of request (Administrative or Work Assignment)
class RequestTypeForm(forms.Form):
    REQUEST_TYPE_CHOICES = [
        ('administrative', 'Administrative Request'),
        ('work_assignment', 'Work Assignment'),
    ]
    request_type = forms.ChoiceField(
        choices=REQUEST_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Request Type",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("RequestTypeForm initialized with data: %s", self.data)

# Step 2 (Administrative Requests): Form for creating an Advance Payment request
class AdvancePaymentForm(forms.ModelForm):
    class Meta:
        model = AdvancePayment
        fields = ['amount', 'notes']  # Removed request_date because it's set automatically

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('amount', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'notes',  # Notes that the employee inputs
            Submit('submit', 'Next', css_class='btn btn-primary')
        )

# Step 2 (Work Assignment Requests): Form for assigning work to another employee
class WorkAssignmentForm(forms.ModelForm):
    class Meta:
        model = WorkAssignment
        fields = ['taskerId', 'work', 'assignDate', 'dueDate']
        widgets = {
            'assignDate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'dueDate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'work': forms.Textarea(attrs={'placeholder': 'Describe the work details'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("WorkAssignmentForm initialized with data: %s", self.data)
        
        self.fields['taskerId'].queryset = Employee.objects.all()  # Allows the user to pick any employee for the task.
        logger.debug("Tasker queryset set with %s employees", self.fields['taskerId'].queryset.count())

# Step 3: Form for finalizing the request message and attaching a file
class RequestDetailsForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['requestMessage', 'file_attachment']
        widgets = {
            'requestMessage': forms.Textarea(attrs={'placeholder': 'Describe your request'}),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)  # Pass the employee from the view
        super().__init__(*args, **kwargs)
        
        # Limit the file attachment selection to the employee's files
        if self.employee:
            self.fields['file_attachment'].queryset = EmployeeFile.objects.filter(employee=self.employee)
        
        self.helper = FormHelper()  # Initialize Crispy Form Helper
        self.helper.layout = Layout(
            'requestMessage',  # Request message field for general input
            'file_attachment',  # Optional file attachment
            Submit('submit', 'Submit Request', css_class='btn btn-success')  # Submit button styled with Bootstrap 5
        )

# Step 2 (Administrative Requests): Hidden field for superadmin assignment
class AdminSuperadminAssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request_type = kwargs.pop('request_type', None)
        super().__init__(*args, **kwargs)
        
        logger.debug("AdminSuperadminAssignmentForm initialized with request_type: %s", request_type)

        if request_type:
            # Look up the superadmin based on the request type (e.g., advance payment)
            superadmin_assignment = SuperadminAssignment.objects.filter(request_type=request_type).first()
            if superadmin_assignment:
                self.fields['destinationEmployeeId'] = forms.ModelChoiceField(
                    queryset=Employee.objects.filter(pk=superadmin_assignment.superadmin.pk),
                    initial=superadmin_assignment.superadmin,
                    widget=forms.HiddenInput()
                )
                logger.debug("Superadmin %s assigned to request type %s", superadmin_assignment.superadmin, request_type)
            else:
                logger.warning("No superadmin found for request type: %s", request_type)
