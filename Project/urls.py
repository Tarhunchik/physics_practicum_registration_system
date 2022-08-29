"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views. Home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import to include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Application import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page),
    path('main/', views.index_page),
    path('register/', views.register_page),
    path('test/', views.test_page),
    path('logout/', views.logout_view),
    path('login/', views.login_page),
    path('non_auth_user/', views.non_authorised_user_page),
    path('schedule/', views.schedule_page3),
    path('telegram_bot/', views.tg_bot_page),
    path('contacts/', views.contacts_page),
    path('rules/', views.rules_page),
    path('recording_error/', views.recording_error_page),
    path('recording_success/', views.recording_success_page),
    path('account/', views.account_page),
]
