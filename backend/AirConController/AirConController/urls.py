"""
系统HTTP URL路由
"""
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^receptionist', include('receptionist.urls')),
    re_path(r'^administrator', include('administrator.urls')),
    re_path(r'^manager', include('manager.urls')),
    re_path(r'^customer', include('customer.urls')),
]
