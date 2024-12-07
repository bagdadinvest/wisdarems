from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_user, name="login_user"),  # Add trailing slash
    path('logout/', views.logout_user, name="logout_user"),
    path('signup/', views.signup, name="signup"),
    path('welcome/', views.welcome_view, name='welcome_view'),  # Ensure the name matches 'welcome_view'

    path('magic-login/<uidb64>/<token>/', views.magic_login, name="magic_login"),  # Add magic link login route

    path('', views.index, name="index"),
]
