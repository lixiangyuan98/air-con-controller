"""
系统HTTP URL路由
"""
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^logger/', include('logger.urls')),
    re_path(r'^main_machine/', include('main_machine.urls')),
    re_path(r'^slave/', include('slave.urls')),
]
