"""
URL configuration for operational_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import manpower.user_manager
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from manpower.api_handler import handle_api_request, user_login_api
import event_management.views
from event_management.report_handler import *
from system_log import views
from system_log.group_sms import handle_sms_request
import system_log.notification_manager as notif_man

urlpatterns = [
    path('admin_roef_control/', admin.site.urls),
    path('', event_management.views.homepage,name='homepage'),
    path('event/', include('event_management.urls')),
    path('manpower/', include('manpower.urls')),
    path('system_log/', include('system_log.urls')),
    path('login/',manpower.user_manager.user_login,name='userlogin'),
    path('logout/',manpower.user_manager.logout_user,name='userlogout'),
    path('signup/',manpower.user_manager.signup,name='signup'),
    path('visitor_signup/',manpower.user_manager.visitor_signup,name='visitor_signup'),
    path('api/login',user_login_api,name='login_api'),
    path('api/<action>',handle_api_request,name='api'),
    path('group_sms/',handle_sms_request,name='group_sms'),
    path('notifications/',notif_man.notification_handler,name='notification_handler'),
    path('notifications/<action>',notif_man.notification_handler,name='notification_handler'),
    path('notifications/<action>/<id>',notif_man.notification_handler,name='notification_handler'),
]
