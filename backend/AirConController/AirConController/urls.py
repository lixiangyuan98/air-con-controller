"""
系统HTTP URL路由
"""
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^charger', include('charger.urls')),
    re_path(r'^controller', include('controller.urls')),
    re_path(r'^monitor', include('monitor.urls')),
    re_path(r'^syslogger', include('syslogger.urls')),
]
