import json
from django.shortcuts import render
from air_conditioner.controller import Controller
from air_conditioner.service import PowerService
from _ast import operator
from django.http import JsonResponse


# Create your views here.

def check_in(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        controller.dispatch(service='ADMINISTRATOR', operation='check in', room_id=room_id_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def request_on(request):
    room_id_get = request.GET.get('room_id')
    current_temp_get = float(request.GET.get('current_temper'))
    try:
        controller = Controller.instance()
        content = controller.dispatch(service='POWER', operation='power on', room_id=room_id_get,
                                      current_temp=current_temp_get)
        content = {'message': "OK", 'result': content}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def request_off(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        controller.dispatch(service='POWER', operation='power off', room_id=room_id_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def change_temper(request):
    room_id_get = request.GET.get('room_id')
    target_temper_get = float(request.GET.get('target_temper'))
    try:
        controller = Controller.instance()
        controller.dispatch(service='SLAVE', operation='change temp', room_id=room_id_get,
                            target_temp=target_temper_get)
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def change_speed(request):
    room_id_get = request.GET.get('room_id')
    speed_get = int(request.GET.get('speed'))
    try:
        controller = Controller.instance()
        controller.dispatch(service='SLAVE', operation='change speed', room_id=room_id_get, target_speed=speed_get)
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def request_fee(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        content = {'message': 'OK', 'result': controller.dispatch(service='GET_FEE', room_id=room_id_get)}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def check_out(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id=room_id_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
