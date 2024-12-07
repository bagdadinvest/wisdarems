# Standard library imports
import os
from datetime import datetime
import json
import time
import ast
from django.db.models import Q  # Add this import for Q objects

# Django imports
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from .forms import EmployeeProfileForm, EmployeeFileUploadForm, WorkScheduleForm, DayScheduleForm, MakeRequestForm

from .models import Employee, Request, WorkAssignment, AdvancePayment, SalaryDetails, Attendance, WorkSchedule, EmployeeFile, SuperadminAssignment
from django.contrib.auth.decorators import login_required
from django.utils.translation import get_language, activate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django_countries.fields import CountryField
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect, JsonResponse

from formtools.wizard.views import SessionWizardView
from .forms import RequestTypeForm, AdminRequestForm, WorkAssignmentForm, RequestDetailsForm, UnifiedRequestForm



def dark_mode(request, mode):
    # Get the referer URL (the page the user was on)
    referer = request.META.get('HTTP_REFERER', '/')
    
    # Set the darkMode cookie based on the mode provided
    response = HttpResponseRedirect(referer)  # Redirect back to the previous page
    if mode == 'enabled':
        response.set_cookie('darkMode', 'enabled', max_age=7*24*60*60)
    else:
        response.set_cookie('darkMode', 'disabled', max_age=7*24*60*60)

    return response



 
def set_language(request):
    next_url = request.POST.get('next', request.GET.get('next'))
    if not next_url or not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
        next_url = request.META.get('HTTP_REFERER', '/')

    response = redirect(next_url)
    lang_code = request.POST.get('language', request.GET.get('language'))
    if lang_code and lang_code in dict(settings.LANGUAGES).keys():
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        activate(lang_code)  # Activate the language immediately for the current request

    # Debugging output
    print(f"Session language: {request.session.get('django_language')}")
    print(f"Cookie language: {request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)}")
    print(f"Current language: {get_language()}")

    return response

@login_required(login_url='/ems/login/')
def dashboard(request):
    # Fetch the employee instance based on the logged-in user's username
    employee = Employee.objects.filter(username=request.user.username).first()

    # Redirect or handle if no employee is found for the logged-in user
    if not employee:
        return redirect('some_error_page')  # Replace with your error handling

    # Prepare a list of field names and values (ignoring sensitive fields)
    exclude_fields = ['id', 'password', 'is_superuser', 'is_staff', 'is_active', 'slug']
    fields = []

    for field in employee._meta.get_fields():
        # Skip relations, many-to-many, one-to-many, and fields we don't want to show
        if field.concrete and not field.many_to_many and not field.one_to_many and field.name not in exclude_fields:
            field_name = field.verbose_name
            field_value = getattr(employee, field.name)

            # For fields with choices, display the human-readable name
            if field.choices:
                field_value = getattr(employee, f'get_{field.name}_display')()

            fields.append((field_name, field_value))

    # Pass the fields and the employee to the template
    return render(request, "employee/index.html", {'employee': employee, 'fields': fields})

# Attendance view
@login_required(login_url='/ems/login/')
def attendance(request):
    # Fetch Attendance for the current employee by filtering with the 'username'
    employee = Employee.objects.get(username=request.user.username)
    attendance = Attendance.objects.filter(employee=employee)
    return render(request, "employee/attendance.html", {"attendance": attendance})

# Notice view
@login_required(login_url='/ems/login/')
def notice(request):
    notices = Notice.objects.all()
    return render(request, "employee/notice.html", {"notices": notices})

# Notice detail view
@login_required(login_url='/ems/login/')
def noticedetail(request, id):
    # Fetch the notice by its ID
    noticedetail = get_object_or_404(Notice, noticeId=id)
    return render(request, "employee/noticedetail.html", {"noticedetail": noticedetail})

# Assign work view
@login_required(login_url='/ems/login/')
def assignWork(request):
    context = {}
    employee = Employee.objects.get(username=request.user.username)
    initialData = {
        "assignerId": employee.id,
    }
    flag = ""
    form = WorkForm(request.POST or None, initial=initialData)
    if form.is_valid():
        currentTaskerId = form.cleaned_data["taskerId"]
        if currentTaskerId == employee.id:
            flag = "Invalid ID Selected..."
        else:
            flag = "Work Assigned Successfully!!"
            form.save()
    context['form'] = form
    context['flag'] = flag
    return render(request, "employee/workassign.html", context)

# View my work
@login_required(login_url='/ems/login/')
def mywork(request):
    # Fetch the employee and their assigned work
    employee = Employee.objects.get(username=request.user.username)
    work = WorkAssignment.objects.filter(taskerId=employee)
    return render(request, "employee/mywork.html", {"work": work})

# Work details view
@login_required(login_url='/ems/login/')
def workdetails(request, wid):
    # Fetch work assignment details by ID
    workdetails = get_object_or_404(WorkAssignment, id=wid)
    return render(request, "employee/workdetails.html", {"workdetails": workdetails})



# List of assigned works by the employee
@login_required(login_url='/ems/login/')
def assignedworklist(request):
    # Fetch works assigned by the logged-in user
    employee = Employee.objects.get(username=request.user.username)
    works = WorkAssignment.objects.filter(assignerId=employee)
    return render(request, "employee/assignedworklist.html", {"works": works})

# Delete work assignment
@login_required(login_url='/ems/login/')
def deletework(request, wid):
    # Delete the work assignment
    obj = get_object_or_404(WorkAssignment, id=wid)
    obj.delete()
    return redirect('assignedworklist')

# Update work assignment
@login_required(login_url='/ems/login/')
def updatework(request, wid):
    # Fetch and update a specific work assignment
    work = get_object_or_404(WorkAssignment, id=wid)
    form = WorkForm(request.POST or None, instance=work)
    flag = ""
    if form.is_valid():
        currentTaskerId = form.cleaned_data["taskerId"]
        employee = Employee.objects.get(username=request.user.username)
        if currentTaskerId == employee.id:
            flag = "Invalid ID Selected..."
        else:
            flag = "Work Updated Successfully!!"
            form.save()
    return render(request, "employee/updatework.html", {'currentWork': work, "filledForm": form, "flag": flag})


@login_required
def virtual_reality(request):
   return render(request, 'virtual-reality.html')

@login_required
def profile(request):
    print("Entered the profile view")

    # Get the logged-in employee
    employee = Employee.objects.filter(username=request.user.username).first()
    if employee:
        print(f"Employee found: {employee.first_name} {employee.last_name}")
    else:
        print("Employee not found!")

    if request.method == 'POST':
        print("Handling POST request")

        # Handling the profile form
        profile_form = EmployeeProfileForm(request.POST, request.FILES, instance=employee)
        file_form = EmployeeFileUploadForm(request.POST, request.FILES)

        # Check if profile form is valid
        if profile_form.is_valid():
            profile_form.save()
            print("Profile form is valid and saved")
            messages.success(request, 'Profile updated successfully.')
        else:
            print(f"Profile form errors: {profile_form.errors}")

        # Check if file upload form is valid
        if file_form.is_valid():
            employee_file = file_form.save(commit=False)
            employee_file.employee = employee  # Associate the file with the current employee
            employee_file.save()
            print("File form is valid and file uploaded")
            messages.success(request, 'File uploaded successfully.')
        else:
            print(f"File form errors: {file_form.errors}")
            messages.error(request, 'There was an error uploading the file.')

        # Redirect after POST to avoid re-submitting the form
        return redirect('employee:profile')
    else:
        print("Handling GET request")

        # Initialize forms for GET request
        profile_form = EmployeeProfileForm(instance=employee)
        file_form = EmployeeFileUploadForm()

    # Query the profile picture and CV if they exist
    profile_picture = EmployeeFile.objects.filter(employee=employee, file_type='profile_picture').first()
    if profile_picture:
        print(f"Profile picture found: {profile_picture.file.url}")
    else:
        print("No profile picture found")

    cv = EmployeeFile.objects.filter(employee=employee, file_type='cv').first()
    if cv:
        print(f"CV found: {cv.file.url}")
    else:
        print("No CV found")

    # Check if the tutorial should be shown (for first-time login)
    show_tutorial = not request.session.get('tutorial_shown', False)
    if show_tutorial:
        print("Showing tutorial for the first time")
        request.session['tutorial_shown'] = True  # Mark tutorial as shown
    else:
        print("Tutorial already shown before")

    # Debug the context being passed to the template
    context = {
        'profile_form': profile_form,
        'file_form': file_form,
        'profile_picture': profile_picture,
        'cv': cv,
        'uploaded_files': EmployeeFile.objects.filter(employee=employee),
        'show_tutorial': show_tutorial,  # Pass tutorial flag to the template
    }

    print(f"Context being passed: {context}")

    return render(request, 'profile (2).html', context)




#@login_required
#def messages(request, error=None):
 #   
  #  return render(request, 'messages.html', context)


from django.http import JsonResponse

@login_required
def upload_employee_file(request):
    if request.method == 'POST':
        file_form = EmployeeFileUploadForm(request.POST, request.FILES)

        if file_form.is_valid():
            # Create the instance but don't save it yet
            employee_file = file_form.save(commit=False)
            employee_file.employee = request.user  # Set the employee to the logged-in user
            employee_file.save()
            messages.success(request, 'File uploaded successfully.')

            # If it's an AJAX request, return JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"message": "File uploaded successfully."}, status=200)
            else:
                # Non-AJAX request, redirect to the profile
                return redirect('employee:profile')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"errors": file_form.errors}, status=400)
            else:
                messages.error(request, 'There was an error uploading the file.')

    # Handle GET request (if needed)
    else:
        file_form = EmployeeFileUploadForm()

    return render(request, 'upload_file.html', {'file_form': file_form})

################################################################################

@login_required(login_url='/ems/login/')
def request_details_modal(request, request_id):
    print(f"Fetching request details for request ID: {request_id}")  # Debug statement
    employee = request.user
    print(f"Logged in user: {employee.username}")  # Debug statement

    try:
        # Fetch the request object and check if the employee is either the requester or the destination
        requestdetail = get_object_or_404(
            Request,
            Q(id=request_id) & (Q(requesterId=employee) | Q(destinationEmployeeId=employee))
        )
        print(f"Request found: {requestdetail}")  # Debug statement
    except Exception as e:
        print(f"Error fetching request details: {str(e)}")  # Debug statement
        raise  # Reraise the error for proper handling

    data = {
    'requestId': requestdetail.id,  # Use the correct field for the request ID
    'requester': requestdetail.requesterId.name,
    'message': requestdetail.requestMessage,
    'requestDate': requestdetail.requestDate.strftime('%d %b %Y %H:%M'),
    'destinationEmployee': requestdetail.destinationEmployeeId.name,
    }

    print(f"Returning JSON data: {data}")  # Debug statement
    return JsonResponse(data)


################################################################################3

@login_required(login_url='/ems/login/')
def request_dashboard(request):
    employee = Employee.objects.get(username=request.user.username)
    employees = Employee.objects.exclude(id=employee.id)

    # Step 1: Form initialization
    unified_form = UnifiedRequestForm(request.POST or None, request.FILES or None, employee_queryset=employees)

    if request.method == 'POST':
        request_type = request.POST.get('request_type')

        if unified_form.is_valid():
            # Handle administrative requests
            if request_type == 'administrative':
                superadmin_assignment = SuperadminAssignment.objects.filter(
                    request_type=unified_form.cleaned_data.get('admin_request_type')).first()
                if not superadmin_assignment:
                    messages.error(request, 'No superadmin assigned for this request type.')
                else:
                    new_request = Request(
                        requesterId=employee,
                        requestMessage=unified_form.cleaned_data.get('request_message'),
                        destinationEmployeeId=superadmin_assignment.superadmin
                    )
                    new_request.save()
                    messages.success(request, 'Administrative request submitted successfully.')
            
            # Handle work assignment requests
            elif request_type == 'work_assignment':
                recipient = Employee.objects.get(id=unified_form.cleaned_data.get('recipient_id').id)
                new_request = Request(
                    requesterId=employee,
                    requestMessage=unified_form.cleaned_data.get('request_message'),
                    destinationEmployeeId=recipient
                )
                new_request.save()
                messages.success(request, 'Work assignment request submitted successfully.')

            return redirect('employee:request_dashboard')

    # Retrieve requests for context
    incoming_requests = Request.objects.filter(destinationEmployeeId=employee)
    outgoing_requests = Request.objects.filter(requesterId=employee)

    context = {
        'employees': employees,
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
        'unified_form': unified_form,
    }
    return render(request, "employee/request_dashboard.html", context)


def employee_list_view(request):
    # Retrieve all employees from the Employee model
    employees = Employee.objects.all()

    # Pass the employee list to the template
    return render(request, 'employee_list.html', {'employees': employees})
