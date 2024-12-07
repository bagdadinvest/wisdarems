from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from formtools.wizard.views import SessionWizardView
from .models import Request, Employee, AdvancePayment, WorkAssignment, SuperadminAssignment
from .wizforms import RequestTypeForm, AdvancePaymentForm, WorkAssignmentForm, RequestDetailsForm
from .forms import UnifiedRequestForm
from crispy_forms.helper import FormHelper
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define the forms for each step in the wizard
FORMS = [
    ("step1", RequestTypeForm),
    ("step2_admin", AdvancePaymentForm),
    ("step2_assignment", WorkAssignmentForm),
    ("step3", RequestDetailsForm),
]

TEMPLATES = {
    "step1": "requests/request_step1.html",
    "step2_admin": "requests/request_step2_admin.html",
    "step2_assignment": "requests/request_step2_assignment.html",
    "step3": "requests/request_step3.html",
}

class RequestWizard(SessionWizardView):
    form_list = FORMS

    # Conditions to determine which forms are shown
    condition_dict = {
        'step2_admin': lambda wizard: wizard.get_cleaned_data_for_step('step1') and wizard.get_cleaned_data_for_step('step1')['request_type'] == 'administrative',
        'step2_assignment': lambda wizard: wizard.get_cleaned_data_for_step('step1') and wizard.get_cleaned_data_for_step('step1')['request_type'] == 'work_assignment',
    }

    # Log the current step and the forms used
    def get_template_names(self):
        current_step = self.steps.current
        logger.debug(f"Current step: {current_step}")
        return [TEMPLATES.get(current_step, 'requests/request_step1.html')]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        logger.debug(f"Current step: {self.steps.current}, Context data: {context}")

        # For admin requests, find the superadmin for assignment
        if self.steps.current == 'step2_admin':
            superadmin_assignment = SuperadminAssignment.objects.filter(request_type='advance_payment').first()
            if superadmin_assignment:
                context['superadmin'] = superadmin_assignment.superadmin
            else:
                logger.warning(f"No superadmin found for request type: advance_payment.")
        return context

    def done(self, form_list, **kwargs):
        step1_data = self.get_cleaned_data_for_step('step1')
        step3_data = self.get_cleaned_data_for_step('step3')
        employee = self.request.user
        logger.debug(f"Form data from step 1: {step1_data}, step 3: {step3_data}")

        if step1_data['request_type'] == 'administrative':
            step2_data = self.get_cleaned_data_for_step('step2_admin')
            advance_payment = AdvancePayment.objects.create(
                employee=employee,
                amount=step2_data['amount'],
                notes=step2_data.get('notes', ''),
                status='pending'
            )
            superadmin_assignment = SuperadminAssignment.objects.filter(request_type='advance_payment').first()
            if superadmin_assignment:
                new_request = Request.objects.create(
                    requesterId=employee,
                    requestMessage=step3_data['requestMessage'],
                    advance_payment=advance_payment,
                    destinationEmployeeId=superadmin_assignment.superadmin
                )
                messages.success(self.request, 'Administrative request submitted successfully.')
            else:
                messages.error(self.request, 'No superadmin assigned for this request type.')

        elif step1_data['request_type'] == 'work_assignment':
            step2_data = self.get_cleaned_data_for_step('step2_assignment')
            work_assignment = WorkAssignment.objects.create(
                assignerId=employee,
                taskerId=step2_data['taskerId'],
                work=step2_data['work'],
                assignDate=step2_data['assignDate'],
                dueDate=step2_data['dueDate'],
            )
            new_request = Request.objects.create(
                requesterId=employee,
                requestMessage=step3_data['requestMessage'],
                work_assignment=work_assignment,
                destinationEmployeeId=step2_data['taskerId']
            )
            messages.success(self.request, 'Work assignment request submitted successfully.')
        return redirect('employee:request_dashboard')

@login_required(login_url='/')
def request_dashboard(request):
    employee = Employee.objects.get(username=request.user.username)
    employees = Employee.objects.exclude(id=employee.id)
    
    unified_form = UnifiedRequestForm(request.POST or None, request.FILES or None, employee_queryset=employees)

    if request.method == 'POST':
        if unified_form.is_valid():
            request_type = unified_form.cleaned_data.get('request_type')
            if request_type == 'administrative':
                superadmin_assignment = SuperadminAssignment.objects.filter(
                    request_type=unified_form.cleaned_data.get('admin_request_type')).first()
                if not superadmin_assignment:
                    messages.error(request, 'No superadmin assigned for this request type.')
                else:
                    Request.objects.create(
                        requesterId=employee,
                        requestMessage=unified_form.cleaned_data.get('request_message'),
                        destinationEmployeeId=superadmin_assignment.superadmin
                    )
                    messages.success(request, 'Administrative request submitted successfully.')
            elif request_type == 'work_assignment':
                recipient = unified_form.cleaned_data.get('recipient_id')
                Request.objects.create(
                    requesterId=employee,
                    requestMessage=unified_form.cleaned_data.get('request_message'),
                    destinationEmployeeId=recipient
                )
                messages.success(request, 'Work assignment request submitted successfully.')
            return redirect('employee:request_dashboard')

    incoming_requests = Request.objects.filter(destinationEmployeeId=employee)
    outgoing_requests = Request.objects.filter(requesterId=employee)

    context = {
        'employees': employees,
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
        'unified_form': unified_form,
    }
    return render(request, "employee/request_dashboard.html", context)
