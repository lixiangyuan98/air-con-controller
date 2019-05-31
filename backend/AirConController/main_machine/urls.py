from django.urls import path, re_path, include
from main_machine import views

urlpatterns = [
    re_path(r'^power_on', views.power_on),
    re_path(r'^init_param$', views.init_param),
    re_path(r'^start_up', views.start_up),
    re_path(r'^check_room_state', views.check_room_state),
    re_path(r'^close', views.close),
]
