import datetime

from django.http import JsonResponse, StreamingHttpResponse

from air_conditioner.controller import Controller


# Create your views here.

def query_report(request):
    qtype_get = request.GET.get('qtype')
    room_id_get = request.GET.get('room_id')
    date_get = request.GET.get('date')
    date_get_sp = date_get.split("-")
    date_get_da = datetime.datetime(int(date_get_sp[0]), int(date_get_sp[1]), int(date_get_sp[2]))
    try:
        controller = Controller.instance()
        content = controller.dispatch(service='REPORT', operation='query report',
                                      room_id=room_id_get, date=date_get_da,
                                      qtype=qtype_get)
        content = {'message': "OK",
                   'result': {
                       'room_id': content.room_id,
                       'on_off_times': content.times_of_on_off,
                       'service_time': content.duration,
                       'fee': content.fee,
                       'dispatch_time': content.times_of_dispatch,
                       'rdr_number': content.number_of_detail,
                       'change_temp_times': content.times_of_change_temp,
                       'change_speed_times': content.times_of_change_speed,
                   }
                   }
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def print_report(request):
    qtype_get = request.GET.get('qtype')
    room_id_get = request.GET.get('room_id')
    date_get = request.GET.get('date')
    date_get_sp = date_get.split("-")
    date_get_da = datetime.datetime(int(date_get_sp[0]), int(date_get_sp[1]), int(date_get_sp[2]))
    try:
        controller = Controller.instance()
        filename = controller.dispatch(service='REPORT', operation='print report', room_id=room_id_get, date=date_get_da,
                            qtype=qtype_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def query_invoice(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        content = controller.dispatch(service='INVOICE', operation='query invoice', room_id=room_id_get)
        content = {'message': 'OK',
                   'result': {
                       'room_id': content.room_id,
                       'check_in_time': content.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                       'check_out_time': content.check_out_time.strftime('%Y-%m-%d %H:%M:%S'),
                       'fee': content.total_fee
                   }
                   }
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def print_invoice(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        filename = controller.dispatch(service='INVOICE', operation='print invoice', room_id=room_id_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def query_rdr(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        content = controller.dispatch(service='DETAIL', operation='query detail', room_id=room_id_get)
        content = {'message': 'OK',
                   'result': [
                       {
                           'room_id': c.room_id,
                           'start_time': c.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                           'end_time': c.finish_time.strftime('%Y-%m-%d %H:%M:%S'),
                           'speed': c.target_speed,
                           'fee_rate': c.fee_rate,
                           'fee': round(c.fee, 2)
                       }
                       for c in content
                   ]
                   }
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def print_rdr(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = Controller.instance()
        filename = controller.dispatch(service='DETAIL', operation='print detail', room_id=room_id_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
