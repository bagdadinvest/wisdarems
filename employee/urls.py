from django.contrib.auth import views as auth_views

from django.urls import path
from . import views
from . import scheduleview
from .scheduleview import  manage_work_schedules, edit_work_schedule, delete_work_schedule, employee_schedule_view
from . import reqview
from django.conf import settings


app_name = 'employee'

urlpatterns = [
    
    path('set_language/', views.set_language, name='set_language'),
    path('login/', auth_views.LoginView.as_view(template_name='login_modal.html'), name='login'),

    
    path('dashboard/', views.dashboard, name="dashboard"),
    path('attendance/', views.attendance, name="attendance"),
    path('notice/', views.notice, name="notice"),
    path('noticedetail/<str:id>/', views.noticedetail, name="noticedetail"),
    path('assignwork/', views.assignWork, name="assignwork"),
    path('mywork/', views.mywork, name="mywork"),
    path('workdetails/<str:wid>/', views.workdetails, name="workdetails"),
    path('editAW/', views.assignedworklist, name="assignedworklist"),
    path('deletework/<str:wid>/', views.deletework, name="deletework"),
    path('updatework/<str:wid>/', views.updatework, name="updatework"),
    path('virtual-reality/', views.virtual_reality, name='virtual-reality'),
    path('profile/', views.profile, name='profile'),
   # path('messages/', views.messages, name='messages'),
    path('upload/', views.upload_employee_file, name='employee_file_upload'),
    path('notice/', views.notice, name='notice'),
    path('request-details-modal/<int:request_id>/', views.request_details_modal, name='request_details_modal'),
    path('toggle-dark-mode/<str:mode>/', views.dark_mode, name='toggle-dark-mode'),

    
    path('requests/', reqview.request_dashboard, name='request_dashboard'),
    path('requests-wizard/', reqview.RequestWizard.as_view(), name='request_wizard'),

    
    # Employee Schedule Views
    path('my-schedule/', scheduleview.employee_schedule_view, name='employee-schedule'),

    # Admin Schedule Views
    path('manage-schedules/', manage_work_schedules, name='manage-work-schedules'),
    path('edit-schedule/<int:schedule_id>/', edit_work_schedule, name='edit-work-schedule'),
    path('delete-schedule/<int:schedule_id>/', delete_work_schedule, name='delete-work-schedule'),
    path('employees/', views.employee_list_view, name='employee_list'),

]

