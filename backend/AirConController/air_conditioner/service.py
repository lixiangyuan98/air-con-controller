"""
服务类

除AirConditionerService外，均采用单例模式
"""
import datetime
import threading
from typing import List, Tuple, Optional, Dict

from air_conditioner.models import DetailModel, Log
from utils import logger, master_machine_mode, fan_speed, room_status, UPDATE_FREQUENCY, \
    TEMPERATURE_CHANGE_RATE_PER_SEC, RepeatTimer, operations, DBFacade
from .entity import MasterMachine, Detail, Invoice, ReportFile, Report, InvoiceFile, Room


class AirConditionerService:
    """
    空调服务

    Attributes:
        __room: 房间
        __start_time: 服务开始时间
        __duration: 服务时长
        __wait_time: 剩余等待时长
        __target_speed: 目标风速
        __fee_rate: 费率
        __fee_since_start: 服务开始以来的费用
    """

    def __init__(self, room: Room, target_speed: int, fee_rate: float):
        """
        初始化空调服务

        Args:
            room: 房间
            target_speed: 目标风速
        """
        self.__room = room
        self.__start_time = ...  # type: datetime.datetime
        self.__duration = 0
        self.__wait_time = 120
        self.__target_speed = target_speed
        self.__fee_rate = fee_rate
        self.__fee_rate_per_sec = fee_rate / 60
        self.__fee_since_start = 0.0
        logger.info('初始化AirConditionerService')

    @property
    def room(self):
        return self.__room

    @property
    def start_time(self):
        return self.__start_time

    @property
    def duration(self):
        return self.__duration

    @property
    def wait_time(self):
        return self.__wait_time

    @wait_time.setter
    def wait_time(self, wait_time):
        self.__wait_time = wait_time

    @property
    def target_speed(self):
        return self.__target_speed

    @target_speed.setter
    def target_speed(self, target_speed):
        self.__target_speed = target_speed

    @property
    def fee_rate(self):
        return self.__fee_rate

    @fee_rate.setter
    def fee_rate(self, fee_rate):
        self.__fee_rate_per_sec = fee_rate / 60
        self.__fee_rate = fee_rate

    @property
    def fee_since_start(self):
        return self.__fee_since_start

    def start(self):
        """服务开始"""
        self.__duration = 0
        self.__fee_since_start = 0.0
        self.__start_time = datetime.datetime.now()
        DBFacade.exec(Log.objects.create, room_id=self.room.room_id, operation=operations.DISPATCH,
                      op_time=datetime.datetime.now())
        logger.info('房间' + self.room.room_id + '开始服务')

    def finish(self):
        """服务结束"""
        detail = Detail(None, self.room.room_id, self.start_time, self.start_time +
                        datetime.timedelta(seconds=self.duration), self.target_speed,
                        self.fee_rate, self.fee_since_start)
        DBFacade.exec(DetailModel.objects.create, room_id=detail.room_id, start_time=detail.start_time,
                      finish_time=detail.finish_time, speed=detail.target_speed,
                      fee_rate=detail.fee_rate, fee=detail.fee)
        self.__start_time = ...
        logger.info('房间' + self.room.room_id + '停止服务')

    def update(self, mode):
        """定时更新队列内服务的状态"""
        if self.start_time is not ...:
            self.__duration += UPDATE_FREQUENCY
            self.__room.service_time += UPDATE_FREQUENCY
            self.__fee_since_start += self.__fee_rate_per_sec * UPDATE_FREQUENCY
            self.__room.fee += self.__fee_rate_per_sec * UPDATE_FREQUENCY
            if mode == master_machine_mode.COOL:
                self.room.current_temp -= TEMPERATURE_CHANGE_RATE_PER_SEC[self.target_speed] * UPDATE_FREQUENCY
            else:
                self.room.current_temp += TEMPERATURE_CHANGE_RATE_PER_SEC[self.target_speed] * UPDATE_FREQUENCY
        else:
            self.__wait_time -= UPDATE_FREQUENCY


class AirConditionerServiceQueue:
    """
    空调服务队列

    Attributes:
        __MAX_NUM: 最大服务对象数
        __queue: 服务对象dict
        __min_speed: 队列中的最低风速
        __max_speed: 队列中的最高风速
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__MAX_NUM = 3
        self.__queue = {}  # type: Dict[str, AirConditionerService]
        self.__min_speed = ...  # type: int
        self.__max_speed = ...  # type: int
        logger.info('初始化AirConditionerServiceQueue')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    @property
    def queue(self):
        return self.__queue

    @property
    def min_speed(self):
        return self.__min_speed

    @property
    def max_speed(self):
        return self.__max_speed

    def __update_max_min_speed(self):
        values = self.queue.values()
        if len(values) == 0:
            self.__min_speed = None
            self.__max_speed = None
        else:
            self.__min_speed = min(values, key=lambda x: x.target_speed).target_speed
            self.__max_speed = max(values, key=lambda x: x.target_speed).target_speed

    def empty(self):
        return len(self.__queue) == 0

    def has_space(self):
        return self.__MAX_NUM - len(self.__queue)

    def push(self, service: AirConditionerService) -> Tuple[bool, Optional[AirConditionerService]]:
        """
        将服务对象加入服务队列

        Returns:
            如果房间能被加入服务队列, 则返回(True, 被换出的服务对象)
            如果房间不能被加入服务队列, 则返回(False, service)
        """
        if len(self.queue) < self.__MAX_NUM:
            self.queue[service.room.room_id] = service
            self.__update_max_min_speed()
            service.start()
            return True, None
        elif service.target_speed > self.__min_speed:
            services = [s for s in list(self.queue.values()) if s.target_speed == self.__min_speed]
            if len(services) == 1:
                service_to_pop = services[0]
            else:
                service_to_pop = max(services, key=lambda x: x.duration)
            self.queue.pop(service_to_pop.room.room_id)
            self.queue[service.room.room_id] = service
            service_to_pop.finish()
            self.__update_max_min_speed()
            service.start()
            return True, service_to_pop
        elif service.target_speed == self.__min_speed and service.target_speed == self.__max_speed:
            service.wait_time = 120
        else:
            service.wait_time = 86400  # 无限等待
        return False, service

    def pop(self) -> AirConditionerService:
        """将指定房间的服务对象移出服务队列"""
        raise NotImplementedError

    def remove(self, room_id: str):
        """将指定房间的服务对象从服务队列中移除"""
        if self.queue.get(room_id) is not None:
            service = self.queue.pop(room_id)
            service.finish()

    def update(self, mode) -> List[AirConditionerService]:
        """
        更新服务队列所有服务对象的状态

        Returns:
            到达目标温度的对象
        """
        reach_temp_services = []
        if len(self.queue.values()) != 0:
            for service in self.queue.values():
                service.update(mode)
                if mode == master_machine_mode.COOL:
                    if service.room.current_temp - service.room.target_temp < 0.01:
                        reach_temp_services.append(service)
                else:
                    if service.room.current_temp - service.room.target_temp > 0.01:
                        reach_temp_services.append(service)
        return reach_temp_services

    def get_service(self, room_id: str) -> AirConditionerService:
        return self.queue.get(room_id)


class WaitQueue:
    """
    等待队列

    Attributes:
        __queue: 等待对象dict
        __max_speed: 等待队列的最高风速
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__queue = {}  # type: Dict[str, AirConditionerService]
        self.__max_speed = 0
        logger.info('初始化WaitQueue')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    @property
    def queue(self):
        return self.__queue

    @property
    def max_speed(self):
        return self.__max_speed

    def empty(self):
        return len(self.__queue) == 0

    def push(self, service: AirConditionerService) -> None:
        """将房间加入等待队列"""
        # if service is not isinstance(service, AirConditionerService):
        #     logger.error('服务不存在')
        #     raise RuntimeError('服务不存在')
        self.queue[service.room.room_id] = service
        self.__max_speed = service.target_speed if service.target_speed > self.__max_speed else self.__max_speed
        logger.info('房间' + service.room.room_id + '开始等待')

    def pop(self) -> Optional[AirConditionerService]:
        """
        取出应当被服务的对象

        Returns:
            返回最高风速的对象中，剩余等待服务时间最少的服务对象
        """
        if len(self.queue) == 0:
            return None
        else:
            services = [s for s in list(self.queue.values()) if s.target_speed == self.__max_speed]
            if len(services) == 1:
                service_to_pop = services[0]
            else:
                service_to_pop = min(services, key=lambda x: x.wait_time)
            self.queue.pop(service_to_pop.room.room_id)
            self.__max_speed = max(list(self.queue.values()), key=lambda x: x.target_speed) \
                if len(list(self.queue)) != 0 else 0
            return service_to_pop

    def remove(self, room_id: str):
        """将指定房间的服务对象从等待队列中移除"""
        if self.queue.get(room_id) is not None:
            self.queue.pop(room_id)
            self.__max_speed = max(list(self.queue.values()), key=lambda x: x.target_speed) \
                if len(list(self.queue)) != 0 else 0

    def update(self, mode) -> List[AirConditionerService]:
        """
        更新等待队列所有服务对象的状态

        Returns:
            到达等待时间的对象
        """
        timeout_services = []
        if len(self.queue.values()) != 0:
            for service in self.queue.values():
                service.update(mode)
                if service.wait_time <= 0:
                    timeout_services.append(service)
        return timeout_services

    def get_service(self, room_id: str) -> AirConditionerService:
        return self.queue.get(room_id)


class UpdateService:
    """更新状态服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__service_queue = AirConditionerServiceQueue.instance()
        self.__wait_queue = WaitQueue.instance()
        self.__master_machine = MasterMachine.instance()
        self.timer = RepeatTimer(UPDATE_FREQUENCY, self._task)
        logger.info('初始化UpdateService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def _task(self):
        """周期定时任务"""
        reach_temp_services = self.__service_queue.update(self.__master_machine.mode)
        for service in reach_temp_services:
            self.__service_queue.remove(service.room.room_id)
            service.room.status = room_status.STANDBY
        timeout_services = self.__wait_queue.update(self.__master_machine.mode)
        for service in timeout_services:
            self.push_service(service)
        while self.__service_queue.has_space():
            service = self.__wait_queue.pop()
            if service is not None:
                self.push_service(service)
            else:
                break

    def push_service(self, service: AirConditionerService):
        """将指定服务放入服务队列或等待队列中"""
        serving_room = self.__master_machine.get_room(service.room.room_id)  # type: Room
        if (self.__master_machine.mode == master_machine_mode.COOL
            and serving_room.current_temp <= serving_room.target_temp) \
                or (self.__master_machine.mode == master_machine_mode.HOT
                    and serving_room.current_temp >= serving_room.target_temp):
            pass
        else:
            status, service = self.__service_queue.push(service)
            if status is True:
                serving_room.status = room_status.SERVING
            else:
                serving_room.status = room_status.WAITING
            if service is not None:
                waiting_room = self.__master_machine.get_room(service.room.room_id)
                waiting_room.status = room_status.WAITING
                self.__wait_queue.push(service)


class ChangeTempAndSpeedService:
    """改变温度/风速服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        self.__service_queue = AirConditionerServiceQueue.instance()
        self.__update_service = UpdateService.instance()
        self.__wait_queue = WaitQueue.instance()
        logger.info('初始化ChangeTempAndSpeedService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def init_temp_and_speed(self, room_id: str, target_temp: float, target_speed: int):
        """
        开机时初始化服务

        Args:
            room_id: 房间号
            target_temp: 目标温度
            target_speed: 目标风速
        """
        room = self.__master_machine.get_room(room_id)
        room.target_temp = target_temp
        room.current_speed = target_speed
        service = AirConditionerService(room, target_speed, self.__master_machine.fee_rate[target_speed])
        self.__update_service.push_service(service)
        logger.info('房间' + room.room_id + '初始化服务, 目标温度: ' + str(target_temp) + ', 风速: ' + str(target_speed))
        return self.__master_machine.get_slave_status(room)

    def change_temp(self, room_id: str, target_temp: float):
        """
        改变目标温度

        Args:
            room_id: 房间号
            target_temp: 目标温度
        """
        if not self.__master_machine.temp_low_limit < target_temp < self.__master_machine.temp_high_limit:
            logger.error('目标温度不合法')
            raise RuntimeError('目标温度不合法')
        room = self.__master_machine.get_room(room_id)
        room.target_temp = target_temp
        air_conditioner_service = self.__service_queue.get_service(room_id)
        if air_conditioner_service is None:  # 不在服务队列中
            air_conditioner_service = self.__wait_queue.get_service(room_id)
            if air_conditioner_service is None:  # 不在服务队列和等待队列
                air_conditioner_service = AirConditionerService(room, room.current_speed,
                                                                self.__master_machine.fee_rate[room.current_speed])
                self.__update_service.push_service(air_conditioner_service)
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=operations.CHANGE_TEMP,
                      op_time=datetime.datetime.now())
        logger.info('房间' + room_id + '改变目标温度为' + str(target_temp))

    def change_speed(self, room_id: str, target_speed: int):
        """
        改变目标风速

        Args:
            room_id: 房间号
            target_speed: 目标风速
        """
        if target_speed not in (fan_speed.LOW, fan_speed.NORMAL, fan_speed.HIGH):
            logger.error('目标风速不合法')
            raise RuntimeError('目标风速不合法')
        room = self.__master_machine.get_room(room_id)
        room.current_speed = target_speed
        air_conditioner_service = self.__service_queue.get_service(room_id)
        if air_conditioner_service is not None:  # 在服务队列中
            self.__service_queue.remove(room_id)
            air_conditioner_service.target_speed = target_speed
            air_conditioner_service.fee_rate = self.__master_machine.fee_rate[target_speed]
            while air_conditioner_service.target_speed < self.__wait_queue.max_speed:
                service_to_serve = self.__wait_queue.pop()
                if service_to_serve is not None:
                    self.__update_service.push_service(service_to_serve)
                else:
                    break
            self.__update_service.push_service(air_conditioner_service)
        else:
            air_conditioner_service = self.__wait_queue.get_service(room_id)
            if air_conditioner_service is not None:  # 在等待队列中
                self.__wait_queue.remove(room_id)
                air_conditioner_service.target_speed = target_speed
                air_conditioner_service.fee_rate = self.__master_machine.fee_rate[target_speed]
                self.__update_service.push_service(air_conditioner_service)
            else:  # 不在服务队列和等待队列中
                air_conditioner_service = AirConditionerService(room, target_speed,
                                                                self.__master_machine.fee_rate[target_speed])
                self.__update_service.push_service(air_conditioner_service)
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=operations.CHANGE_SPEED,
                      op_time=datetime.datetime.now())
        logger.info('房间' + room_id + '改变目标风速为' + str(target_speed))


class PowerService:
    """开关机服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        self.__service_queue = AirConditionerServiceQueue.instance()
        self.__wait_queue = WaitQueue.instance()
        logger.info('初始化PowerService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def slave_machine_power_on(self, room_id: str, current_temp: float) -> Tuple[float, int]:
        """
        开启指定从机

        Returns:
            要创建的服务的目标温度, 目标风速
        """
        if current_temp is None:
            logger.error('当前温度不合法')
            raise RuntimeError('当前温度不合法')
        room = self.__master_machine.get_room(room_id)
        room.current_temp = current_temp
        if room.status == room_status.CLOSED:
            # 按照默认温度风速创建服务
            room.target_temp = self.__master_machine.default_target_temp
            room.current_speed = self.__master_machine.default_speed
            target_temp, speed = self.__master_machine.default_target_temp, self.__master_machine.default_speed
        elif room.status == room_status.STANDBY:
            # 按照先前温度和风速创建服务
            target_temp, speed = room.target_temp, room.current_speed
        else:
            logger.error('房间已开机')
            raise RuntimeError('房间已开机')
        room.power_on(current_temp)
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=operations.POWER_ON,
                      op_time=datetime.datetime.now())
        return target_temp, speed

    def slave_machine_power_off(self, room_id):
        """关闭指定从机"""
        room = self.__master_machine.get_room(room_id)
        if room.status == room_status.CLOSED:
            logger.error('房间已关机')
            raise RuntimeError('房间已关机')
        self.__service_queue.remove(room_id)
        self.__wait_queue.remove(room_id)
        room.close_up()
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=operations.POWER_OFF,
                      op_time=datetime.datetime.now())


class AdministratorService:
    """
    管理服务

    Attributes:
        __master_machine: 主控机的对象
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = ...  # type: MasterMachine
        logger.info('初始化AdministratorService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def init_master_machine(self) -> None:
        """初始化主控机"""
        self.__master_machine = MasterMachine.instance()

    def set_master_machine_param(self, mode: str, temp_low_limit: float, temp_high_limit: float,
                                 default_target_temp: float, default_speed: int, fee_rate: tuple) -> None:
        """设置主控机参数"""
        if self.__master_machine is ...:
            logger.error('主控机未初始化')
            raise RuntimeError('主控机未初始化')
        if mode not in (master_machine_mode.COOL, master_machine_mode.HOT):
            logger.error('mode不存在')
            raise RuntimeError('mode不存在')
        if not temp_low_limit < default_target_temp < temp_high_limit:
            logger.error('目标温度不合法')
            raise RuntimeError('目标温度不合法')
        if default_speed not in (fan_speed.LOW, fan_speed.NORMAL, fan_speed.HIGH):
            logger.error('speed不存在')
            raise RuntimeError('speed不存在')
        if len(fee_rate) != 3:
            logger.error('费率阶梯不符')
            raise RuntimeError('费率阶梯不符')
        self.__master_machine.set_param(mode, temp_low_limit, temp_high_limit, default_target_temp,
                                        default_speed, fee_rate)

    def start_master_machine(self) -> dict:
        """
        启动主控机

        Returns:
            temp_low_limit: 最低温度
            temp_high_limit: 最高温度
        """
        if self.__master_machine is ...:
            logger.error('MasterMachine未初始化')
            raise RuntimeError('MasterMachine未初始化')
        UpdateService.instance().timer.start()
        return self.__master_machine.start()

    def stop_master_machine(self) -> None:
        """关闭主控机"""
        if self.__master_machine is ...:
            logger.error('MasterMachine未初始化')
            raise RuntimeError('MasterMachine未初始化')
        self.__master_machine.stop()
        UpdateService.instance().timer.cancel()

    def get_status(self) -> List[dict]:
        """
        获取所有从机状态

        Returns:
            room_id: 房间号
            current_temper: 当前温度
            speed: 当前风速
            mode: 工作模式
            fee: 总费用
            fee_rate: 当前费率
            status: 房间状态
            service_time: 服务时长
            target_temper: 目标温度
        """
        if self.__master_machine is ...:
            logger.error('MasterMachine未初始化')
            raise RuntimeError('MasterMachine未初始化')
        return self.__master_machine.get_all_status()

    def check_in(self, room_id: str):
        self.__master_machine.check_in(room_id)

    def check_out(self, room_id: str):
        self.__master_machine.check_out(room_id)


class GetFeeService:
    """获取费用服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        logger.info('初始化GetFeeService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_current_fee(self, room_id: str) -> Dict:
        """获取指定从机当前费用"""
        return self.__master_machine.get_slave_status(self.__master_machine.get_room(room_id))


class DetailService:
    """详单服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        logger.info('初始化DetailService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_detail(self, room_id: str) -> List[Detail]:
        """获取详单"""
        return self.__master_machine.get_detail(room_id)[1]

    def print_detail(self, room_id: str) -> str:
        """打印详单"""
        check_in_time, details = self.__master_machine.get_detail(room_id)
        return Detail.get_detail_file(room_id, check_in_time, details).save()


class InvoiceService:
    """账单服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        logger.info('初始化InvoiceService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_invoice(self, room_id: str) -> Invoice:
        """获取账单"""
        return self.__master_machine.get_invoice(room_id)

    def print_invoice(self, room_id: str) -> str:
        """打印账单"""
        invoice = self.__master_machine.get_invoice(room_id)
        return InvoiceFile(invoice).save()


class ReportService:
    """报表服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        logger.info('初始化ReportService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_report(self, room_id: str, qtype: str, date: datetime.datetime) -> Report:
        """获取报表"""
        if qtype == 'day':
            start_time = datetime.datetime(date.year, date.month, date.day)
            finish_time = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)
        elif qtype == 'week':
            first_day = date - datetime.timedelta(days=date.weekday())
            last_day = date + datetime.timedelta(days=6 - date.weekday())
            start_time = datetime.datetime(first_day.year, first_day.month, first_day.day)
            finish_time = datetime.datetime(last_day.year, last_day.month, last_day.day, 23, 59, 59)
        elif qtype == 'month':
            start_time = datetime.datetime(date.year, date.month, 1)
            finish_time = datetime.datetime(date.year, date.month + 1, 1) - datetime.timedelta(days=1)
        elif qtype == 'year':
            start_time = datetime.datetime(date.year, 1, 1)
            finish_time = datetime.datetime(date.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            logger.error('不支持的qtype')
            raise RuntimeError('不支持的qtype')
        return self.__master_machine.get_report(room_id, start_time, finish_time)

    def print_report(self, room_id: str, qtype: str, date: datetime.datetime) -> str:
        """打印报表"""
        report = self.get_report(room_id, qtype, date)
        return ReportFile(report).save()
