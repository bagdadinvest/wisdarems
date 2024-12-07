from django.urls import path
from . import views
from . import shell_views

urlpatterns = [
    path('', views.metrics_view, name='metrics_view'),
    
    # View to execute predefined Django commands from the database
    path('run-predefined-command/', views.run_predefined_command, name='run_predefined_command'),
    
    # View to execute custom commands input by the user
    path('run-custom-command/', views.run_custom_command, name='run_custom_command'),
    path('shell/', shell_views.shell_view, name='shell_view'),

]
