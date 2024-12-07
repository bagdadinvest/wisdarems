from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from employee.models import Employee
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template.loader import get_template
from .forms import SignupForm  # Import the form
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


# Magic Link Login View
def magic_login(request, uidb64, token):
    try:
        # Decode the uid from base64 and get the use
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Log the user in and redirect them
        login(request, user)
        return redirect('employee:dashboard')  # Redirect after successful login
    else:
        return HttpResponse("Invalid or expired magic link.", status=400)


# Debug Template View
def debug_template_view(request):
    try:
        template = get_template('employee/Login.html')
        return HttpResponse("Template found!")
    except Exception as e:
        return HttpResponse(f"Template not found: {e}")


# Login User View
def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"Email: {email}, Password: {password}")  # Debugging print statements

        # Authenticate using the email
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("employee:dashboard")
        else:
            print("Invalid Credentials")  # Debugging
            messages.error(request, "Invalid Credentials")
            return redirect("accounts:login_user")

    return render(request, "employee/login.html")


# Logout User View
def logout_user(request):
    logout(request)
    return redirect("/")


# Signup View
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data.get('job_number')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            print(f"Job number: {id}, Email: {email}, Password: {password}")

            if Employee.objects.filter(job_number=id).exists():
                messages.error(request, "Employee with this ID already exists.")
            else:
                employee = form.save(commit=False)
                employee.username = employee.email  # Assign email to username
                employee.set_password(password)  # Hash the password
                employee.save()  # Save the employee instance
                messages.success(request, "Employee created successfully.")

                # Log the user in after successful signup
                # Explicitly specify the backend as ModelBackend
                login(request, employee, backend='django.contrib.auth.backends.ModelBackend')

                # Redirect to the welcome view
                dashboard_url = reverse('accounts:welcome_view')
                return redirect(dashboard_url)
        else:
            messages.error(request, "Invalid employee data.")
    else:
        form = SignupForm()

    return render(request, 'employee/signup.html', {'form': form})


# Welcome View
def welcome_view(request):
    print('Welcome view triggered')

    # Use the custom user model
    User = get_user_model()
    
    user_count = User.objects.count()
    print(f'User count: {user_count}')

    if request.user.is_authenticated:
        print(f'Authenticated user: {request.user.username}')
    else:
        print('User is not authenticated')

    context = {
        'user_count': user_count,
        'user': request.user
    }
    return render(request, 'check_email.html', context)


# Index View
def index(request, error=None):
    return render(request, 'index.html')
