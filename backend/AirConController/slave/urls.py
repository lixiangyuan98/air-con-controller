from django.urls import path, re_path, include
from slave import views

urlpatterns = [
    re_path(r'^check_in$', views.check_in),
    re_path(r'^request_on$', views.request_on),
    re_path(r'^request_off$', views.request_off),
    re_path(r'^change_temper$', views.change_temper),
    re_path(r'^change_speed$', views.change_speed),
    re_path(r'^request_fee$', views.request_fee),
    re_path(r'^check_out$', views.check_out),
]
