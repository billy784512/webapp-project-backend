from concurrent.futures import ThreadPoolExecutor, Future
from threading import Lock
from typing import Callable, Any


class TaskThreadPool:
    def __init__(self, max_workers: int):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, func: Callable[..., Any], *args, **kwargs) -> Future:
        return self.executor.submit(func, *args, **kwargs)

class ThreadPoolManager:
    _instance = None
    _lock = Lock()

    def __init__(self):
        if ThreadPoolManager._instance is not None:
            raise RuntimeError("Use instance() to access ThreadPoolManager.")
        
        self.read_pool = TaskThreadPool(max_workers=5)
        self.write_pool = TaskThreadPool(max_workers=1)

    @classmethod
    def instance(cls) -> "ThreadPoolManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
