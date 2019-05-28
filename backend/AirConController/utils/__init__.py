"""
工具类
"""
import copy
import logging

from threading import Timer, Thread, Lock

# 全局日志记录器
logger = logging.getLogger('django')
room_ids = ('309c', '310c', '311c', '312c', 'f3')
UPDATE_FREQUENCY = 1
TEMPERATURE_CHANGE_RATE_PER_SEC = 1 / 60


class RepeatTimer(Timer):
    """循环定时器"""

    def __init__(self, interval, function, *args, **kwargs):
        Timer.__init__(self, interval, function, *args, **kwargs)
        self.setName('Timer')

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)


class DBFacadeThread(Thread):

    def __init__(self, function, **kwargs):
        Thread.__init__(self)
        self.name = 'DBFacade'
        self.function = function
        self.kwargs = kwargs
        self.result = None

    def run(self):
        self.result = copy.copy(self.function(**self.kwargs))


class DBFacade:
    """数据库操作"""

    _lock = Lock()
    _thread = None

    @staticmethod
    def exec(function, **kwargs):
        if DBFacade._thread is not None:
            with DBFacade._lock:
                DBFacade._thread.join()
        with DBFacade._lock:
            DBFacade._thread = DBFacadeThread(function, **kwargs)
            DBFacade._thread.start()
            DBFacade._thread.join()
            return DBFacade._thread.result
