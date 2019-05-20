"""实体类"""
import datetime
import threading

from utils import MasterMachineMode, MasterMachineStatus, RoomStatus, logger


class MasterMachine:
    """
    主控机

    Attributes:
        __mode:             工作模式
        __status:           工作状态
        __start_time:       开机时间，在start()方法里设置
        __temp_low_limit:   最低温度，在set_param()方法里设置
        __temp_high_limit:  最高温度，在set_param()方法里设置
        __fee_rate:         费率，tuple类型，对应每一级风速的费用
        __room_list:        房间列表
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        """初始化主控机"""
        self.__mode = MasterMachineMode.NOT_SET
        self.__status = MasterMachineStatus.STANDBY
        self.__start_time = None
        self.__temp_low_limit = None
        self.__temp_high_limit = None
        self.__default_target_temp = None
        self.__fee_rate = None
        self.__room_list = []
        logger.info('初始化主控机')

    def __new__(cls, *args, **kwargs):
        """Singleton"""
        if not hasattr(MasterMachine, '__instance'):
            with MasterMachine.__instance_lock:
                if not hasattr(MasterMachine, '__instance'):
                    MasterMachine.__instance = object.__new__(cls)
        return MasterMachine.__instance

    def set_param(self, mode, temp_low_limit, temp_high_limit, default_target_temp, fee_rate):
        """
        设置运行参数

        Args:
            mode: 运行模式，MasterMachineMode中的其中一个值
            temp_low_limit: 最低温度
            temp_high_limit: 最高温度
            default_target_temp: 默认温度
            fee_rate: 费率list，分别对应每级风速的费率
        """
        self.__mode = mode
        self.__temp_low_limit = temp_low_limit
        self.__temp_high_limit = temp_high_limit
        self.__default_target_temp = default_target_temp
        self.__fee_rate = fee_rate
        logger.info('设置主控机参数为: mode=' + self.__mode + ' temp_low_limit=' + str(self.__temp_low_limit) +
                    ' temp_high_limit=' + str(self.__temp_high_limit) + ' default_target_temp=' +
                    str(self.__default_target_temp) + ' fee_rate=' + str(self.__fee_rate))

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
    def fee_rate(self):
        return self.__fee_rate

    def start(self):
        """启动主控机"""
        self.__status = MasterMachineStatus.RUNNING
        logger.info('主控机启动')

    def stop(self):
        """关闭主控机"""
        self.__status = MasterMachineStatus.STOPPED
        logger.info('主控机关机')

    def get_detail(self, room_id, check_in_time, check_out_time):
        """获取指定房间的详单"""
        # TODO
        pass

    def create_invoice(self, room_id, check_in_time, check_out_time):
        """获取指定房间的账单"""
        # TODO
        pass

    def create_report(self, room_id, start_time, finish_time):
        """获取指定房间的报表"""
        # TODO
        pass

    def get_slave_status(self):
        """
        获取主机关联的所有从机的状态

        Returns:
            所有从机的状态，为一个list，每个元素包含一个dict，如：

            [
                {
                    'room_id': 0,
                    'status': 'OCCUPIED',
                    'current_temp': 20.5,
                    'current_speed': 2,
                }
            ]
        """
        slave_status = []
        for room in self.__room_list:
            slave_status.append({
                'room_id': room.room_id,
                'status': room.status,
                'current_temp': room.current_temp,
                'current_speed': room.current_speed,
            })
        logger.info('获取从机状态')
        return slave_status


class Room:
    """
    房间

    Attributes:
        __room_id: 房间号
        __status: 房间状态
        __current_temp: 房间当前温度
        __current_speed: 房间当前风速
        __check_in_time: 入住时间
        __check_out_time: 退房时间
    """

    def __init__(self, room_id):
        """
        初始化房间

        Args:
            room_id: 房间号
        """
        self.__room_id = room_id
        self.__status = RoomStatus.AVAILABLE
        self.__current_temp = None
        self.__current_speed = None
        self.__check_in_time = datetime.datetime.now()
        self.__check_out_time = None
        logger.info('房间' + str(self.room_id) + '办理入住')

    @property
    def room_id(self):
        return self.__room_id

    @property
    def status(self):
        return self.__status

    def check_in(self):
        """办理入住"""
        self.__status = RoomStatus.OCCUPIED

    def close_up(self):
        """关机"""
        self.__status = RoomStatus.CHARGING

    def check_out(self):
        """退房"""
        self.__status = RoomStatus.AVAILABLE

    @property
    def current_temp(self):
        return self.__current_temp

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
    def check_in_time(self):
        return self.__check_in_time

    @property
    def check_out_time(self):
        return self.__check_out_time

    @check_out_time.setter
    def check_out_time(self, check_out_time):
        self.__check_out_time = check_out_time
        logger.info('房间' + str(self.__room_id) + '退房')


class Detail:
    """
    详单

    Attributes:
        __detail_id: 详单号
        __room_id: 房间号
        __start_time: 记录起始时间
        __finish_time: 记录结束时间
        __target_temp: 目标温度
        __target_speed: 目标风速
        __fee_rate: 费率
        __fee: 费用
    """

    def __init__(self, detail_id, room_id, start_time, finish_time, target_temp, target_speed, fee_rate, fee):
        """
        初始化详单

        新建Detail时，不需要传入detail_id
        从DetailModel创建Detail时，需传入detail_id

        Args:
            detail_id: 详单号
            room_id: 房间号
            start_time: 记录起始时间
            finish_time: 记录结束时间
            target_temp: 目标温度
            target_speed: 目标风速
            fee_rate: 费率
            fee: 费用
        """
        self.__detail_id = detail_id
        self.__room_id = room_id
        self.__start_time = start_time
        self.__finish_time = finish_time
        self.__target_temp = target_temp
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
    def target_temp(self):
        return self.__target_temp

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
    def get_detail_file(detail_list):
        """
        生成详单文件

        Args:
            detail_list: 入住时间段的详单列表
        """
        return DetailFile(detail_list)


class Invoice:
    """
    账单

    Attributes:
        __invoice_id: 账单号
        __room_id: 房间号
        __check_in_time: 入住时间
        __check_out_time: 退房时间
        __total_fee: 总费用
    """

    def __init__(self, invoice_id, room_id, check_in_time, check_out_time, total_fee):
        """
        初始化账单

        新建Invoice时，不需要传入invoice_id
        从InvoiceModel创建Invoice时，需传入invoice_id

        Args:
            invoice_id: 账单号
            room_id: 房间号
            check_in_time: 入住时间
            check_out_time: 退房时间
            total_fee: 总费用
        """
        self.__invoice_id = invoice_id
        self.__room_id = room_id
        self.__check_in_time = check_in_time
        self.__check_out_time = check_out_time
        self.__total_fee = total_fee
        if invoice_id is not None:
            logger.info("读取账单" + str(self.__invoice_id))
        else:
            logger.info('新建账单(room_id=' + str(self.__room_id) + ' check_in_time=' + str(self.__check_in_time) +
                        ' check_out_time=' + str(self.__check_out_time))

    @property
    def invoice_id(self):
        return self.__invoice_id

    @property
    def room_id(self):
        return self.__room_id

    @property
    def check_in_time(self):
        return self.__check_in_time

    @property
    def check_out_time(self):
        return self.check_out_time

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
        __report_id: 报表号
        __room_id: 房间号
        __start_time: 起始时间
        __finish_time: 终止时间
        __times_of_on_off: 开关机次数
        __times_of_dispatch: 调度次数
        __times_of_change_temp: 改变温度次数
        __times_of_change_speed: 改变风速次数
        __number_of_detail: 详单条目数
    """

    def __init__(self, report_id, room_id, start_time, finish_time, times_of_on_off, times_of_dispatch,
                 times_of_change_temp, times_of_change_speed, number_of_detail):
        """
        初始化报表

        新建Report时，不需要传入report_id
        从ReportModel创建Report时，需传入report_id

        Args:
            report_id: 报表号
            room_id: 房间号
            start_time: 起始时间
            finish_time: 终止时间
            times_of_on_off: 开关机次数
            times_of_dispatch: 调度次数
            times_of_change_temp: 改变温度次数
            times_of_change_speed: 改变风速次数
            number_of_detail: 详单条目数
        """
        self.__report_id = report_id
        self.__room_id = room_id
        self.__start_time = start_time
        self.__finish_time = finish_time
        self.__times_of_on_off = times_of_on_off
        self.__times_of_dispatch = times_of_dispatch
        self.__times_of_change_temp = times_of_change_temp
        self.__times_of_change_speed = times_of_change_speed
        self.__number_of_detail = number_of_detail
        if report_id is not None:
            logger.info('读取报表' + str(self.__report_id))
        else:
            logger.info('新建报表(room_id=' + str(self.__room_id) + ' start_time=' + str(self.__start_time) +
                        ' finish_time=' + str(self.__finish_time))

    @property
    def report_id(self):
        return self.__report_id

    @property
    def room_id(self):
        return self.__room_id

    @property
    def start_time(self):
        return self.start_time

    @property
    def finish_time(self):
        return self.__finish_time

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

    def __init__(self, detail_list):
        """
        初始化详单文件

        Args:
            detail_list:    要输出到文件的详单列表
        """
        detail_list.sort(key=lambda item: item.start_time)
        self.__structured_detail = [
            '==================== DETAIL ====================',
            'ROOM ID: ' + detail_list[0].room_id,
        ]
        for detail in detail_list:
            self.__structured_detail.append(
                str(detail.detail_id) + '\t' +
                str(detail.start_time) + '\t' +
                str(detail.finish_time) + '\t' +
                str(detail.fee_rate) + '\t' +
                str(detail.fee)
            )
        self.__structured_detail.append('====================== END ======================')
        self.__filename = '{0}_{1}_{2}.txt'.format(
            str(detail_list[0].room_id),
            str(detail_list[0].start_time),
            str(detail_list[-1].finish_time)
        )

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
            detail_file.writelines(self.__structured_detail)
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
            '==================== INVOICE ====================',
            'ROOM ID: ' + invoice.room_id,
            'CHECK IN TIME: ' + str(invoice.check_in_time),
            'CHECK OUT TIME: ' + str(invoice.check_out_time),
            '-------------------------------------------------',
            'TOTAL FEE:' + str(invoice.total_fee),
            '====================== END ======================',
        ]
        self.__filename = '{0}_{1}_{2}.txt'.format(
            str(invoice.room_id),
            str(invoice.check_in_time),
            str(invoice.check_out_time)
        )

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
            invoice_file.writelines(self.__structured_invoice)
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
            '==================== REPORT ====================',
            'ROOM ID: ' + report.room_id,
            'START TIME: ' + str(report.start_time),
            'FINISH TIME: ' + str(report.finish_time),
            '-------------------------------------------------',
            'TIMES OF ON AND OFF: ' + str(report.times_of_on_off),
            'TIMES OF DISPATCH: ' + str(report.times_of_dispatch),
            'TIMES OF CHANGE TEMPERATURE: ' + str(report.times_of_change_temp),
            'TIMES OF CHANGE FAN SPEED: ' + str(report.times_of_change_speed),
            '====================== END ======================',
        ]
        self.__filename = '{0}_{1}_{2}.txt'.format(
            str(report.room_id),
            str(report.start_time),
            str(report.finish_time)
        )

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
            report_file.writelines(self.__structured_report)
        logger.info('保存报表文件' + self.__filename)

        return self.__filename
