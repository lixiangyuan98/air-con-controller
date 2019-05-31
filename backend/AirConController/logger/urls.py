from django.urls import path, re_path, include
from logger import views

urlpatterns = [
    re_path(r'^query_report$', views.query_report),
    re_path(r'^print_report$', views.print_report),
    re_path(r'^query_invoice$', views.query_invoice),
    re_path(r'^print_invoice$', views.print_invoice),
    re_path(r'^query_rdr$', views.query_rdr),
    re_path(r'^print_rdr$', views.print_rdr),
]
