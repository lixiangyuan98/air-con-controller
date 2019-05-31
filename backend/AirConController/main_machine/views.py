import json
from air_conditioner.controller import Controller
from django.http import JsonResponse


def power_on(request):
    try:
        controller = Controller.instance()
        controller.dispatch(service='ADMINISTRATOR', operation='power on')
        content = json.dumps({'message': 'OK', 'result': None}, ensure_ascii=False)
        return JsonResponse(content,safe=False)
    except RuntimeError as error:
        return JsonResponse(json.dumps({'message': str(error)}, ensure_ascii=False), safe=False)


def init_param(request):
    highest_temper_get = float(request.GET.get('highest_temper'))
    lowest_temper_get = float(request.GET.get('lowest_temper'))
    low_speed_fee_get = float(request.GET.get('low_speed_fee'))
    middle_speed_fee_get = float(request.GET.get('middle_speed_fee'))
    high_speed_fee_get = float(request.GET.get('high_speed_fee'))
    default_temper_get = float(request.GET.get('default_temper'))
    default_speed_get = int(request.GET.get('default_speed'))
    mode_get = int(request.GET.get('mode'))
    if mode_get==0:
        mode_get="制冷"
    else:
        mode_get="制热"

    try:
        controller = Controller.instance()
        controller.dispatch(service='ADMINISTRATOR', operation='set param', mode=mode_get,
                            temp_low_limit=lowest_temper_get, temp_high_limit=highest_temper_get,
                            default_target_temp=default_temper_get,
                            default_speed=default_speed_get,
                            fee_rate=(low_speed_fee_get, middle_speed_fee_get, high_speed_fee_get))
        content = json.dumps({'message': "OK", 'result': None}, ensure_ascii=False)
        return JsonResponse(content,safe=False)
    except RuntimeError as error:
        return JsonResponse(json.dumps({'message': str(error)}, ensure_ascii=False), safe=False)


def start_up(request):
    try:
        controller = Controller.instance()
        controller.dispatch(service='ADMINISTRATOR', operation='start')
        content = json.dumps({'message': 'OK', 'result': None}, ensure_ascii=False)
        return JsonResponse(content,safe=False)
    except RuntimeError as error:
        return JsonResponse(json.dumps({'message': str(error)}, ensure_ascii=False), safe=False)


def check_room_state(request):
    try:
        controller = Controller.instance()
        content = json.dumps(
            {'message': 'OK', 'result': controller.dispatch(service='ADMINISTRATOR', operation='get status')},
            ensure_ascii=False)
        return JsonResponse(content,safe=False)
    except RuntimeError as error:
        return JsonResponse(json.dumps({'message': str(error)}, ensure_ascii=False), safe=False)


def close(request):
    try:
        controller = Controller.instance()
        controller.dispatch(service='ADMINISTRATOR', operation='stop')
        content = json.dumps({'message': 'OK', 'result': None}, ensure_ascii=False)
        return JsonResponse(content,safe=False)
    except RuntimeError as error:
        return JsonResponse(json.dumps({'message': str(error)}, ensure_ascii=False), safe=False)
