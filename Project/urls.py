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
    path('schedule/1/', views.schedule_page1),
    path('schedule/2/', views.schedule_page2),
    path('schedule/3/', views.schedule_page3, name='schedule/3'),
    path('reschedule/1/', views.date_changer_page1),
    path('reschedule/2/', views.date_changer_page2, name='reschedule/2'),
    path('time_interval/', views.new_time_interval),
    path('telegram_bot/', views.tg_bot_page),
    path('contacts/', views.contacts_page),
    path('account/', views.account_page),
    path('rules/', views.rules_page),
    path('record_rules/', views.records_rules_page),
]

handler404 = "Application.views.error_404"
handler500 = "Application.views.error_500"
