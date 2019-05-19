import threading


class Controller:
    """
    控制器类(单例模式)

    负责将接收到的请求转发至对应的处理模块
    """

    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        """Singleton"""
        if not hasattr(Controller, '__instance'):
            with Controller._instance_lock:
                if not hasattr(Controller, '__instance'):
                    Controller.__instance = object.__new__(cls)
        return Controller.__instance

    def dispatch(self):
        """处理来自视图的请求"""
        pass
