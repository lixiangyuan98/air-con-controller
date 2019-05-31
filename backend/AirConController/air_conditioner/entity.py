"""实体类"""
import datetime
import threading
from typing import List, Dict, Optional

from air_conditioner.models import DetailModel, Log
from utils import master_machine_mode, master_machine_status, room_status, logger, room_ids, operations, DBFacade


class MasterMachine:
    """
    主控机

    Attributes:
        __mode:             工作模式
        __status:           工作状态
        __start_time:       开机时间，在start()方法里设置
        __temp_low_limit:   最低温度，在set_param()方法里设置
        __temp_high_limit:  最高温度，在set_param()方法里设置
        __default_target_temp: 默认温度
        __default_speed:     默认风速
        __speed:            工作风速
        __fee_rate:         费率，tuple类型，对应每一级风速的费用
        __room_list:        房间列表
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        """初始化主控机"""
        self.__mode = master_machine_mode.NOT_SET
        self.__status = master_machine_status.STANDBY
        self.__start_time = None
        self.__temp_low_limit = None
        self.__temp_high_limit = None
        self.__default_target_temp = None
        self.__default_speed = None
        self.__speed = None
        self.__fee_rate = None
        self.__room_list = []
        logger.info('初始化主控机')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def set_param(self, mode: str, temp_low_limit: float, temp_high_limit: float,
                  default_target_temp: float, default_speed: int, fee_rate: tuple) -> None:
        """
        设置运行参数

        Args:
            mode: 运行模式，master_machine_mode中的其中一个值
            temp_low_limit: 最低温度
            temp_high_limit: 最高温度
            default_target_temp: 默认温度
            default_speed: 默认风速
            fee_rate: 费率tuple，分别对应每级风速的费率
        """
        self.__mode = mode
        self.__temp_low_limit = temp_low_limit
        self.__temp_high_limit = temp_high_limit
        self.__default_target_temp = default_target_temp
        self.__default_speed = default_speed
        self.__speed = default_speed
        self.__fee_rate = fee_rate
        for _ in room_ids:
            self.__room_list.append(Room(_, self.default_target_temp, self.default_speed))
        logger.info('设置主控机参数为: mode=' + self.__mode + ' temp_low_limit=' + str(self.__temp_low_limit) +
                    ' temp_high_limit=' + str(self.__temp_high_limit) + ' default_target_temp=' +
                    str(self.__default_target_temp) + 'default_speed=' + str(self.__default_speed) +
                    'fee_rate=' + str(self.__fee_rate))

    @property
    def mode(self):
        return self.__mode

    @property
    def status(self):
        return self.__status

    @property
    def start_time(self):
        return self.__start_time

    @property
    def temp_low_limit(self):
        return self.__temp_low_limit

    @property
    def temp_high_limit(self):
        return self.__temp_high_limit

    @property
    def default_target_temp(self):
        return self.__default_target_temp

    @property
    def default_speed(self):
        return self.__default_speed

    @property
    def speed(self):
        return self.__speed

    @property
    def fee_rate(self):
        return self.__fee_rate

    def get_room(self, room_id):
        if room_id not in room_ids:
            logger.error('房间号不存在')
            raise RuntimeError('房间号不存在')
        return self.__room_list[room_ids.index(room_id)]

    def start(self) -> dict:
        """启动主控机"""
        self.__status = master_machine_status.RUNNING
        self.__start_time = datetime.datetime.now()
        logger.info('主控机启动')
        return {
            'temp_low_limit': self.__temp_low_limit,
            'temp_high_limit': self.__temp_high_limit
        }

    def stop(self) -> None:
        """关闭主控机"""
        self.__status = master_machine_status.STOPPED
        for room in self.__room_list:
            room.status = room_status.CLOSED
        logger.info('主控机关机')

    def get_detail(self, room_id: str):
        """获取指定房间的详单"""
        room = self.get_room(room_id)
        if room.status != room_status.AVAILABLE:
            logger.error('需先退房')
            raise RuntimeError('需先退房')
        details = DBFacade.exec(DetailModel.objects.filter, room_id=room_id, start_time__gte=room.check_in_time,
                                finish_time__lte=room.check_out_time)
        return room.check_in_time, [Detail(d.detail_id, d.room_id, d.start_time, d.finish_time, d.speed, d.fee_rate,
                                           d.fee) for d in details]

    def get_invoice(self, room_id: str):
        """获取指定房间的账单"""
        room = self.get_room(room_id)
        details = self.get_detail(room_id)[1]
        details.sort(key=lambda x: x.start_time)
        total_fee = 0
        for detail in details:
            total_fee += detail.fee
        return Invoice(room_id, room.check_in_time, room.check_out_time, round(total_fee, 2))

    def get_report(self, room_id: str, start_time: datetime.datetime, finish_time: datetime.datetime):
        """获取指定房间的报表"""
        details = DBFacade.exec(DetailModel.objects.filter, room_id=room_id, start_time__gte=start_time,
                                finish_time__lte=finish_time)
        logs = DBFacade.exec(Log.objects.filter, room_id=room_id, op_time__gte=start_time, op_time__lte=finish_time)
        duration = 0
        fee = 0.0
        for d in details:
            duration += (d.finish_time - d.start_time).seconds
            fee += d.fee
        times_of_on_off = 0
        times_of_dispatch = 0
        times_of_change_temp = 0
        times_of_change_speed = 0
        for l in logs:
            times_of_on_off += 1 if l.operation == operations.POWER_ON or l.operation == operations.POWER_OFF else 0
            times_of_dispatch += 1 if l.operation == operations.DISPATCH else 0
            times_of_change_temp += 1 if l.operation == operations.CHANGE_TEMP else 0
            times_of_change_speed += 1 if l.operation == operations.CHANGE_SPEED else 0
        return Report(room_id, start_time, finish_time, duration, times_of_on_off, times_of_dispatch,
                      times_of_change_temp, times_of_change_speed, len(details), round(fee, 2))

    def get_slave_status(self, room) -> Dict:
        """获取指定从机的状态"""
        mode = 0 if self.__mode == master_machine_mode.COOL else 1
        logger.debug('获取房间' + room.room_id + '状态')
        return {
            'room_id': room.room_id,
            'status': room.status,
            'mode': mode,
            'current_temper': round(room.current_temp, 2) if room.current_temp is not None else None,
            'speed': room.current_speed,
            'service_time': room.service_time,
            'target_temper': room.target_temp,
            'highest_temper': self.temp_high_limit,
            'lowest_temper': self.temp_low_limit,
            'fee': round(room.fee, 2),
            'fee_rate': self.__fee_rate[room.current_speed]
        }

    def get_all_status(self) -> List[dict]:
        """获取主机关联的所有从机的状态"""
        slave_status = []
        for room in self.__room_list:
            slave_status.append(self.get_slave_status(room))
        logger.info('获取所有从机状态')
        return slave_status

    def check_in(self, room_id):
        self.get_room(room_id).check_in()

    def check_out(self, room_id):
        self.get_room(room_id).check_out()


class Room:
    """
    房间

    Attributes:
        __room_id: 房间号
        __status: 房间状态
        __current_temp: 房间当前温度
        __current_speed: 房间当前风速
        __target_temp: 房间目标温度
        __fee: 房间当前费用
        __service_time: 房间服务时长
        __check_in_time: 入住时间
        __check_out_time: 退房时间
    """

    def __init__(self, room_id: str, target_temp: float, target_speed: int):
        """
        初始化房间

        Args:
            room_id: 房间号
            target_temp: 目标温度
            target_speed: 目标风速
        """
        self.__room_id = room_id
        self.__status = room_status.AVAILABLE
        self.__current_temp = ...  # type: float
        self.__current_speed = target_speed
        self.__target_temp = target_temp
        self.__fee = 0
        self.__service_time = 0
        self.__check_in_time = ...  # type: datetime.datetime
        self.__check_out_time = ...  # type: datetime.datetime
        logger.info('初始化房间' + room_id)

    @property
    def room_id(self):
        return self.__room_id

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    def check_in(self):
        """办理入住"""
        self.__status = room_status.CLOSED
        self.__fee = 0
        self.__service_time = 0
        self.__check_in_time = datetime.datetime.now()
        logger.info('房间' + self.__room_id + '入住')

    def power_on(self, current_temp):
        """开机"""
        self.__status = room_status.STANDBY
        self.__current_temp = current_temp
        logger.info('房间' + self.__room_id + '开机,' + '当前温度:' + str(current_temp))

    def close_up(self):
        """关机"""
        self.__status = room_status.CLOSED
        logger.info('房间' + self.__room_id + '关机')

    def check_out(self):
        """退房"""
        if self.__status != room_status.CLOSED:
            logger.error('需先关机才能退房')
            raise RuntimeError('需先关机才能退房')
        self.__status = room_status.AVAILABLE
        self.__check_out_time = datetime.datetime.now()
        logger.info('房间' + self.__room_id + '退房')

    @property
    def current_temp(self):
        return self.__current_temp if self.__current_temp is not ... else None

    @current_temp.setter
    def current_temp(self, current_temp):
        self.__current_temp = current_temp

    @property
    def current_speed(self):
        return self.__current_speed

    @current_speed.setter
    def current_speed(self, current_speed):
        self.__current_speed = current_speed

    @property
    def target_temp(self):
        return self.__target_temp

    @target_temp.setter
    def target_temp(self, target_temp):
        self.__target_temp = target_temp

    @property
    def fee(self):
        return self.__fee

    @fee.setter
    def fee(self, fee):
        self.__fee = fee

    @property
    def service_time(self):
        return self.__service_time

    @service_time.setter
    def service_time(self, service_time):
        self.__service_time = service_time

    @property
    def check_in_time(self):
        return self.__check_in_time

    @property
    def check_out_time(self):
        return self.__check_out_time


class Detail:
    """
    详单

    Attributes:
        __detail_id: 详单号
        __room_id: 房间号
        __start_time: 记录起始时间
        __finish_time: 记录结束时间
        __target_speed: 目标风速
        __fee_rate: 费率
        __fee: 费用
    """

    def __init__(self, detail_id: Optional[int], room_id: str, start_time: datetime.datetime,
                 finish_time: datetime.datetime, target_speed: int, fee_rate: float, fee: float):
        """
        初始化详单

        新建Detail时，不需要传入detail_id
        从DetailModel创建Detail时，需传入detail_id

        Args:
            detail_id: 详单号
            room_id: 房间号
            start_time: 记录起始时间
            finish_time: 记录结束时间
            target_speed: 目标风速
            fee_rate: 费率
            fee: 费用
        """
        self.__detail_id = detail_id
        self.__room_id = room_id
        self.__start_time = start_time
        self.__finish_time = finish_time
        self.__target_speed = target_speed
        self.__fee_rate = fee_rate
        self.__fee = fee
        if detail_id is not None:
            logger.info('读取详单' + str(self.__detail_id))
        else:
            logger.info('新建详单(room_id=' + str(self.__room_id) + ' start_time=' + str(self.__start_time) +
                        ' finish_time=' + str(self.__finish_time))

    @property
    def detail_id(self):
        return self.__detail_id

    @property
    def room_id(self):
        return self.__room_id

    @property
    def start_time(self):
        return self.__start_time

    @property
    def finish_time(self):
        return self.__finish_time

    @property
    def target_speed(self):
        return self.__target_speed

    @property
    def fee_rate(self):
        return self.__fee_rate

    @property
    def fee(self):
        return self.__fee

    @staticmethod
    def get_detail_file(room_id, check_in_time, detail_list):
        """
        生成详单文件

        Args:
            room_id: 房间号
            check_in_time: 入住时间
            detail_list: 入住时间段的详单列表
        """
        return DetailFile(room_id, check_in_time, detail_list)


class Invoice:
    """
    账单

    Attributes:
        __room_id: 房间号
        __check_in_time: 入住时间
        __check_out_time: 退房时间
        __total_fee: 总费用
    """

    def __init__(self, room_id, check_in_time, check_out_time, total_fee):
        """
        初始化账单

        新建Invoice时，不需要传入invoice_id
        从InvoiceModel创建Invoice时，需传入invoice_id

        Args:
            room_id: 房间号
            check_in_time: 入住时间
            check_out_time: 退房时间
            total_fee: 总费用
        """
        self.__room_id = room_id
        self.__check_in_time = check_in_time
        self.__check_out_time = check_out_time
        self.__total_fee = total_fee
        logger.info('新建账单(room_id=' + str(self.__room_id) + ' check_in_time=' + str(self.__check_in_time) +
                    ' check_out_time=' + str(self.__check_out_time))

    @property
    def room_id(self):
        return self.__room_id

    @property
    def check_in_time(self):
        return self.__check_in_time

    @property
    def check_out_time(self):
        return self.__check_out_time

    @property
    def total_fee(self):
        return self.__total_fee

    def get_invoice_file(self):
        """生成账单文件"""
        return InvoiceFile(self)


class Report:
    """
    报表

    Attributes:
        __room_id: 房间号
        __start_time: 起始时间
        __finish_time: 终止时间
        __duration: 服务时长
        __times_of_on_off: 开关机次数
        __times_of_dispatch: 调度次数
        __times_of_change_temp: 改变温度次数
        __times_of_change_speed: 改变风速次数
        __number_of_detail: 详单条目数
        __fee: 总费用
    """

    def __init__(self, room_id, start_time, finish_time, duration, times_of_on_off, times_of_dispatch,
                 times_of_change_temp, times_of_change_speed, number_of_detail, fee):
        """
        初始化报表

        Args:
            room_id: 房间号
            start_time: 起始时间
            finish_time: 终止时间
            duration: 服务时长
            times_of_on_off: 开关机次数
            times_of_dispatch: 调度次数
            times_of_change_temp: 改变温度次数
            times_of_change_speed: 改变风速次数
            number_of_detail: 详单条目数
            fee: 总费用
        """
        self.__room_id = room_id
        self.__start_time = start_time
        self.__finish_time = finish_time
        self.__duration = duration
        self.__times_of_on_off = times_of_on_off
        self.__times_of_dispatch = times_of_dispatch
        self.__times_of_change_temp = times_of_change_temp
        self.__times_of_change_speed = times_of_change_speed
        self.__number_of_detail = number_of_detail
        self.__fee = fee
        logger.info('新建报表(room_id=' + str(self.__room_id) + ' start_time=' + str(self.__start_time) +
                    ' finish_time=' + str(self.__finish_time))

    @property
    def room_id(self):
        return self.__room_id

    @property
    def start_time(self):
        return self.__start_time

    @property
    def finish_time(self):
        return self.__finish_time

    @property
    def duration(self):
        return self.__duration

    @property
    def times_of_on_off(self):
        return self.__times_of_on_off

    @property
    def times_of_dispatch(self):
        return self.__times_of_dispatch

    @property
    def times_of_change_temp(self):
        return self.__times_of_change_temp

    @property
    def times_of_change_speed(self):
        return self.__times_of_change_speed

    @property
    def number_of_detail(self):
        return self.__number_of_detail

    @property
    def fee(self):
        return self.__fee

    def get_report_file(self):
        """生成报表文件"""
        return ReportFile(self)


class DetailFile:
    """
    详单文件

    Attributes:
        __structured_detail: 结构化的详单信息的list
        __filename: 文件名
    """

    def __init__(self, room_id: str, check_in_time: datetime.datetime, detail_list: List[Detail]):
        """
        初始化详单文件

        Args:
            detail_list:    要输出到文件的详单列表
        """
        detail_list.sort(key=lambda item: item.start_time)
        self.__structured_detail = [
            'ROOM ID, ' + str(room_id),
            'START TIME, END TIME, SPEED, SERVICE TIME, FEE RATE, FEE',
        ]
        for detail in detail_list:
            self.__structured_detail.append(
                detail.start_time.strftime('%Y-%m-%d %H:%M:%S') + ', ' +
                detail.finish_time.strftime('%Y-%m-%d %H:%M:%S') + ', ' +
                str(detail.target_speed) + ', ' +
                str((detail.finish_time - detail.start_time).seconds) + ', ' +
                str(detail.fee_rate) + ', ' +
                str(round(detail.fee, 2))
            )
        self.__filename = room_id + '-' + check_in_time.strftime('%Y%m%d%H%M%S') + '-detail.csv'

    @property
    def structured_detail(self):
        return self.__structured_detail

    @property
    def filename(self):
        return self.__filename

    def save(self):
        """
        保存详单文件

        Returns:
            生成的详单文件的文件名
        """
        with open(self.__filename, 'w') as detail_file:
            detail_file.write('\r\n'.join(self.__structured_detail))
        logger.info('保存详单文件' + self.__filename)

        return self.__filename


class InvoiceFile:
    """
    账单文件

    Attributes:
        __structured_invoice: 结构化的账单信息list
        __filename: 文件名
    """

    def __init__(self, invoice):
        """
        初始化账单文件

        Args:
            invoice: 账单
        """
        self.__structured_invoice = [
            'ROOM ID, ' + str(invoice.room_id),
            'CHECK IN TIME, ' + invoice.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            'CHECK OUT TIME, ' + invoice.check_out_time.strftime('%Y-%m-%d %H:%M:%S'),
            'TOTAL FEE, ' + str(round(invoice.total_fee, 2)),
        ]
        self.__filename = invoice.room_id + '-' + invoice.check_in_time.strftime('%Y%m%d%H%M%S') + '-invoice.csv'

    @property
    def structured_invoice(self):
        return self.__structured_invoice

    @property
    def filename(self):
        return self.__filename

    def save(self):
        """
        保存账单文件

        Returns:
            生成的账单文件的文件名
        """
        with open(self.__filename, 'w') as invoice_file:
            invoice_file.write('\r\n'.join(self.__structured_invoice))
        logger.info('保存账单文件' + self.__filename)

        return self.__filename


class ReportFile:
    """
    报表文件

    Attributes:
        __structured_report: 结构化的账单信息list
        __filename: 文件名
    """

    def __init__(self, report):
        self.__structured_report = [
            'ROOM ID, ' + report.room_id,
            'START TIME, ' + report.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'FINISH TIME, ' + report.finish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'TIMES OF ON AND OFF, ' + str(report.times_of_on_off),
            'TIMES OF DISPATCH, ' + str(report.times_of_dispatch),
            'TIMES OF CHANGE TEMPERATURE, ' + str(report.times_of_change_temp),
            'TIMES OF CHANGE FAN SPEED, ' + str(report.times_of_change_speed),
            'RDR NUMBER, ' + str(report.number_of_detail),
            'SERVICE TIME, ' + str(report.duration),
            'FEE, ' + str(round(report.fee, 2)),
        ]
        self.__filename = report.room_id + '-' + report.start_time.strftime('%Y%m%d%H%M%S') + '-report.csv'

    @property
    def structured_report(self):
        return self.__structured_report

    @property
    def filename(self):
        return self.__filename

    def save(self):
        """
        保存报表文件

        Returns:
            生成的报表文件的文件名
        """
        with open(self.__filename, 'w') as report_file:
            report_file.write('\r\n'.join(self.__structured_report))
        logger.info('保存报表文件' + self.__filename)

        return self.__filename
