import datetime
import time
from threading import Thread

from django.test import TestCase

from air_conditioner.controller import Controller
from air_conditioner.models import Log
from utils import master_machine_mode, fan_speed, RepeatTimer, DBFacade


class ControllerTest(TestCase):

    def test_api(self):
        # 取得控制器对象
        controller = Controller.instance()
        # 主机开机
        controller.dispatch(service='ADMINISTRATOR', operation='power on')
        # 参数初始化
        controller.dispatch(service='ADMINISTRATOR', operation='set param', mode=master_machine_mode.COOL,
                            temp_low_limit=16, temp_high_limit=30, default_target_temp=24,
                            default_speed=fan_speed.NORMAL, fee_rate=(0.5, 0.75, 1.5))
        # 开始执行
        controller.dispatch(service='ADMINISTRATOR', operation='start')
        # 监视空调
        room_status = controller.dispatch(service='ADMINISTRATOR', operation='get status')
        print(room_status)
        # 主机关机
        # controller.dispatch(service='ADMINISTRATOR', operation='stop')
        # 入住
        controller.dispatch(service='ADMINISTRATOR', operation='check in', room_id='309c')
        # 房间开机
        controller.dispatch(service='POWER', operation='power on', room_id='309c', current_temp=23.5)
        time.sleep(5)
        # 改变目标温度
        # controller.dispatch(service='SLAVE', operation='change temp', room_id='309c', target_temp=25)
        time.sleep(5)
        # 改变目标风速
        # controller.dispatch(service='SLAVE', operation='change speed', room_id='309c', target_speed=2)
        time.sleep(5)
        # 获取费用
        room_status = controller.dispatch(service='GET_FEE', room_id='309c')
        print(room_status)
        # 房间关机
        controller.dispatch(service='POWER', operation='power off', room_id='309c')
        # 退房
        controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id='309c')
        # 获取详单
        details = controller.dispatch(service='DETAIL', operation='query detail', room_id='309c')
        # 打印详单
        filename = controller.dispatch(service='DETAIL', operation='print detail', room_id='309c')
        # 获取账单
        invoice = controller.dispatch(service='INVOICE', operation='query invoice', room_id='309c')
        # 打印账单
        filename = controller.dispatch(service='INVOICE', operation='print invoice', room_id='309c')
        # 获取报表
        report = controller.dispatch(service='REPORT', operation='query report', room_id='309c',
                                     date=datetime.datetime.now(), qtype='day')
        filename = controller.dispatch(service='REPORT', operation='print report', room_id='309c',
                                       date=datetime.datetime.now(), qtype='day')
        # 主机关机
        controller.dispatch(service='ADMINISTRATOR', operation='stop')

    def get_status(self):
        controller = Controller.instance()
        # 监视空调
        room_status = controller.dispatch(service='ADMINISTRATOR', operation='get status')
        print(room_status)

    def test_run(self):
        controller = Controller.instance()

        # 主机开机
        controller.dispatch(service='ADMINISTRATOR', operation='power on')
        # 参数初始化
        controller.dispatch(service='ADMINISTRATOR', operation='set param', mode=master_machine_mode.COOL,
                            temp_low_limit=16, temp_high_limit=30, default_target_temp=24,
                            default_speed=fan_speed.NORMAL, fee_rate=(0.5, 0.75, 1.5))
        controller.dispatch(service='ADMINISTRATOR', operation='start')
        timer = RepeatTimer(1, self.get_status)
        timer.start()

        # 入住
        controller.dispatch(service='ADMINISTRATOR', operation='check in', room_id='309c')
        # 房间开机
        controller.dispatch(service='POWER', operation='power on', room_id='309c', current_temp=29)
        time.sleep(5)

        # 入住
        controller.dispatch(service='ADMINISTRATOR', operation='check in', room_id='310c')
        # 房间开机
        controller.dispatch(service='POWER', operation='power on', room_id='310c', current_temp=27)
        time.sleep(3)

        # 入住
        controller.dispatch(service='ADMINISTRATOR', operation='check in', room_id='311c')
        # 房间开机
        controller.dispatch(service='POWER', operation='power on', room_id='311c', current_temp=30)
        time.sleep(4)

        # 入住
        controller.dispatch(service='ADMINISTRATOR', operation='check in', room_id='312c')
        # 房间开机
        controller.dispatch(service='POWER', operation='power on', room_id='312c', current_temp=25)
        controller.dispatch(service='SLAVE', operation='change speed', room_id='312c', target_speed=2)
        time.sleep(10)

        controller.dispatch(service='POWER', operation='power off', room_id='309c')
        controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id='309c')
        controller.dispatch(service='DETAIL', operation='print detail', room_id='309c')
        controller.dispatch(service='POWER', operation='power off', room_id='310c')
        # controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id='310c')
        # controller.dispatch(service='DETAIL', operation='print detail', room_id='310c')
        """
        controller.dispatch(service='POWER', operation='power off', room_id='311c')
        controller.dispatch(service='POWER', operation='power off', room_id='312c')
        # 退房
        controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id='309c')
        controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id='310c')
        controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id='311c')
        controller.dispatch(service='ADMINISTRATOR', operation='check out', room_id='312c')
        # 打印详单
        controller.dispatch(service='DETAIL', operation='print detail', room_id='309c')
        controller.dispatch(service='DETAIL', operation='print detail', room_id='310c')
        controller.dispatch(service='DETAIL', operation='print detail', room_id='311c')
        controller.dispatch(service='DETAIL', operation='print detail', room_id='312c')
        """

        # 主机关机
        controller.dispatch(service='ADMINISTRATOR', operation='stop')
        timer.cancel()

    def test_db(self):

        class MyThread(Thread):

            def run(self) -> None:
                DBFacade.exec(Log.objects.create, room_id='100c', operation='test', op_time=datetime.datetime.now())

        DBFacade.exec(Log.objects.filter, room_id='100c')
        MyThread().start()
        res = DBFacade.exec(Log.objects.filter, room_id='100c')
        print(res[0].operation)
        MyThread().start()
