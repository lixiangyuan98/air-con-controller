import threading

from utils import logger
from .service import (
    AdministratorService, GetFeeService, DetailService,
    InvoiceService, ReportService, PowerService,
    ChangeTempAndSpeedService, UpdateService)


class Controller:
    """
    控制器类

    负责将接收到的请求转发至对应的处理模块
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        """初始化Controller"""
        self.__started = False
        self.__update_service = UpdateService.instance()
        logger.info('初始化Controller')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def dispatch(self, **kwargs):
        """
        处理来自视图的请求

        Keyword Args:
            service: 请求的服务, 可选值为:
                'ADMINISTRATOR': 管理服务
                'AIR_CONDITIONER': 空调服务
                'DETAIL': 详单服务
                'GET_FEE': 获取费用服务
                'INVOICE': 账单服务
                'POWER': 从机开关机服务
                'REPORT': 报表服务
        """
        service_type = kwargs.get('service')
        if service_type == 'ADMINISTRATOR':
            return self.__dispatch_administrator_service(**kwargs)
        elif service_type == 'SLAVE':
            return self.__dispatch_slave_service(**kwargs)
        elif service_type == 'DETAIL':
            return self.__dispatch_detail_service(**kwargs)
        elif service_type == 'GET_FEE':
            return self.__dispatch_get_fee_service(**kwargs)
        elif service_type == 'INVOICE':
            return self.__dispatch_invoice_service(**kwargs)
        elif service_type == 'POWER':
            return self.__dispatch_power_service(**kwargs)
        elif service_type == 'REPORT':
            return self.__dispatch_report_service(**kwargs)
        else:
            logger.warn('不支持的service')
            raise RuntimeError('不支持的service')

    def __dispatch_administrator_service(self, **kwargs):
        """
        处理管理请求

        Keyword Args:
            operation: 执行的具体操作, 具体为
                'power on': 开机
                'set param': 设置参数
                'start': 启动
                'stop':  停机
                'get status': 获取从机状态
                'check in': 入住
                'check out': 退房

            当operation为'set param'时，需提供以下参数:
            mode: 运行模式
            temp_low_limit: 最低温度
            temp_high_limit: 最高温度
            default_target_temp: 默认温度
            fee_rate: 阶梯费率的tuple

            当operation为'check in'或'check out'时，需提供以下参数:
            room_id: 房间号
        """
        administrator_service = AdministratorService.instance()
        operation = kwargs.get('operation')
        if operation == 'power on':
            administrator_service.init_master_machine()
        elif operation == 'set param':
            administrator_service.set_master_machine_param(
                kwargs.get('mode'), kwargs.get('temp_low_limit'), kwargs.get('temp_high_limit'),
                kwargs.get('default_target_temp'), kwargs.get('default_speed'), kwargs.get('fee_rate')
            )
        elif operation == 'start':
            result = administrator_service.start_master_machine()
            self.__started = True
            return result
        elif operation == 'stop':
            administrator_service.stop_master_machine()
            self.__started = False
        elif operation == 'get status':
            return administrator_service.get_status()
        elif operation == 'check in':
            room_id = kwargs.get('room_id')
            return administrator_service.check_in(room_id)
        elif operation == 'check out':
            room_id = kwargs.get('room_id')
            return administrator_service.check_out(room_id)
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')

    def __dispatch_slave_service(self, **kwargs):
        """
        处理房间空调请求

        Keyword Args:
            operation: 要执行的操作, 具体为:
                'change temp': 改变目标温度
                'change speed': 改变目标风速

            当operation为'change temp'时，需提供的参数为:
            room_id: 房间号
            target_temp: 目标温度

            当operation为'change speed'时, 需提供的参数为:
            room_id: 房间号
            target_speed: 目标风速

        """
        if not self.__started:
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        operation = kwargs.get('operation')
        change_temp_and_speed_service = ChangeTempAndSpeedService.instance()
        room_id = kwargs.get('room_id')
        if room_id is None:
            logger.error('缺少参数room_id')
            raise RuntimeError('缺少参数room_id')
        if operation == 'change temp':
            target_temp = kwargs.get('target_temp')
            change_temp_and_speed_service.change_temp(room_id, target_temp)
        elif operation == 'change speed':
            target_speed = kwargs.get('target_speed')
            change_temp_and_speed_service.change_speed(room_id, target_speed)

    def __dispatch_power_service(self, **kwargs):
        """
        处理房间开关机请求

        Keyword Args:
            operation: 要执行的操作, 具体为:
                'power on': 开机
                'power off': 关机

            当operation为'power on'时, 要提供的参数为:
            room_id: 要开启的从机的房间号
            current_temp: 房间当前温度

            当operation为'power off'时, 要提供的参数为:
            room_id: 要关闭的从机的房间号
        """
        change_temp_and_speed_service = ChangeTempAndSpeedService.instance()
        if not self.__started:
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        operation = kwargs.get('operation')
        power_service = PowerService.instance()
        room_id = kwargs.get('room_id')
        if room_id is None:
            logger.error('缺少参数room_id')
            raise RuntimeError('缺少参数room_id')
        if operation == 'power on':
            current_temp = kwargs.get('current_temp')
            target_temp, speed = power_service.slave_machine_power_on(room_id, current_temp)
            return change_temp_and_speed_service.init_temp_and_speed(room_id, target_temp, speed)
        elif operation == 'power off':
            power_service.slave_machine_power_off(room_id)
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')

    def __dispatch_get_fee_service(self, **kwargs):
        """
        处理获取费用请求

        Keyword Args:
            room_id: 要关闭的从机的房间号
        """
        if not self.__started:
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        get_fee_service = GetFeeService.instance()
        room_id = kwargs.get('room_id')
        if room_id is None:
            logger.error('缺少参数room_id')
            raise RuntimeError('缺少参数room_id')
        return get_fee_service.get_current_fee(room_id)

    def __dispatch_detail_service(self, **kwargs):
        """
        处理详单请求

        Keyword Args:
            operation: 请求的操作, 可选值为:
                'query detail': 查询详单
                'print detail': 打印详单
            room_id: 房间号
        """
        if not self.__started:
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        detail_service = DetailService.instance()
        operation = kwargs.get('operation')
        room_id = kwargs.get('room_id')
        if room_id is None:
            logger.error('缺少参数room_id')
            raise RuntimeError('缺少参数room_id')
        if operation == 'query detail':
            return detail_service.get_detail(room_id)
        elif operation == 'print detail':
            return detail_service.print_detail(room_id)
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')

    def __dispatch_invoice_service(self, **kwargs):
        """
        处理账单请求

        Keyword Args:
            operation: 请求的操作, 可选值为:
                'query invoice': 查询账单
                'print invoice': 打印账单
            room_id: 房间号
        """
        if not self.__started:
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        invoice_service = InvoiceService.instance()
        operation = kwargs.get('operation')
        room_id = kwargs.get('room_id')
        if room_id is None:
            logger.error('缺少参数room_id')
            raise RuntimeError('缺少参数room_id')
        if operation == 'query invoice':
            return invoice_service.get_invoice(room_id)
        elif operation == 'print invoice':
            return invoice_service.print_invoice(room_id)
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')

    def __dispatch_report_service(self, **kwargs):
        """
        处理账单请求

        Keyword Args:
            operation: 请求的操作, 可选值为:
                'query report': 获得报表
                'print report': 打印报表
            room_id: 房间号
            qtype: 查询报表的类型, 可选值为:
                'day': 日报表
                'week': 周报表
                'month': 月报表
                'year': 年报表
            date: 查询日期
        """
        if not self.__started:
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        report_service = ReportService.instance()
        operation = kwargs.get('operation')
        room_id = kwargs.get('room_id')
        qtype = kwargs.get('qtype')
        date = kwargs.get('date')
        if room_id is None:
            logger.error('缺少参数room_id')
            raise RuntimeError('缺少参数room_id')
        if operation == 'query report':
            return report_service.get_report(room_id, qtype, date)
        elif operation == 'print report':
            return report_service.print_report(room_id, qtype, date)
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')
